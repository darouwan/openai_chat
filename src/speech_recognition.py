import os
import time

import azure.cognitiveservices.speech as speechsdk
import conversation
from loguru import logger

conv = conversation.ContextConversation("New", system_msg="Answer my question within 50 words")

# Creates an instance of a speech config with specified subscription key and service region.
# Replace with your own subscription key and service region (e.g., "westus").
speech_key = os.environ.get('SPEECH_KEY')
service_region = os.environ.get('SPEECH_REGION')


def speech_recognize_once_from_mic():
    """performs one-shot speech recognition from the default microphone"""
    logger.info("Please start your conversation:")
    # <SpeechRecognitionWithMicrophone>
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.speech_recognition_language = 'zh-CN'
    speech_config.speech_synthesis_voice_name = 'zh-CN-YunfengNeural'
    """
    	zh-CN-XiaochenNeural (Female)
        zh-CN-XiaohanNeural (Female)
        zh-CN-XiaomengNeural (Female)
        zh-CN-XiaomoNeural (Female)
        zh-CN-XiaoqiuNeural (Female)
        zh-CN-XiaoruiNeural (Female)
        zh-CN-XiaoshuangNeural (Female, Child)
        zh-CN-XiaoxiaoNeural (Female)
        zh-CN-XiaoxuanNeural (Female)
        zh-CN-XiaoyanNeural (Female)
        zh-CN-XiaoyiNeural (Female)
        zh-CN-XiaoyouNeural (Female, Child)
        zh-CN-XiaozhenNeural (Female)
        zh-CN-YunfengNeural (Male)
        zh-CN-YunhaoNeural (Male)
        zh-CN-YunjianNeural (Male)
        zh-CN-YunxiaNeural (Male)
        zh-CN-YunxiNeural (Male)
        zh-CN-YunyangNeural (Male)
        zh-CN-YunyeNeural (Male)
        zh-CN-YunzeNeural (Male)
    """

    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    # The default language is "en-us".
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    # Starts speech recognition, and returns after a single utterance is recognized. The end of a
    # single utterance is determined by listening for silence at the end or until a maximum of 15
    # seconds of audio is processed. It returns the recognition text as result.
    # Note: Since recognize_once() returns only a single utterance, it is suitable only for single
    # shot recognition like command or query.
    # For long-running multi-utterance recognition, use start_continuous_recognition() instead.
    while True:

        result = speech_recognizer.recognize_once()

        # Check the result
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            logger.info("Recognized: {}".format(result.text))
            response = conv.send_chat(result.text)
            logger.info(response)
            response = "" + response
            speech_synthesis_result = speech_synthesizer.speak_text_async(response)
            speech_synthesis_result.get()
        elif result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized")
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech Recognition canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))
        time.sleep(0.2)
    # </SpeechRecognitionWithMicrophone>


speech_recognize_once_from_mic()
