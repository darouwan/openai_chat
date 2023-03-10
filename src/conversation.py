import openai
import uuid
from loguru import logger
import settings
import queue


class ContextConversation:
    def __init__(self, topic_name, system_msg='You are a helpful assistant.', max_chat_limit=11):
        """
        Initialize a new chat conversation
        :param topic_name:
        :param system_msg: Many conversations begin with a system message to gently instruct the assistant. For example, here is one of the system messages used for ChatGPT:
        You are ChatGPT, a large language model trained by OpenAI. Answer as concisely as possible. Knowledge cutoff: {knowledge_cutoff} Current date: {current_date}
        In general, gpt-3.5-turbo-0301 does not pay strong attention to the system message, and therefore important instructions are often better placed in a user message.
        """
        if openai.api_key is None:
            openai.api_key = settings.api_keys
        self.__topic_name = topic_name or 'New Topic'
        self.__topic_id = uuid.uuid1()
        self.__system_msg = system_msg
        self.__max_chat_limit = max_chat_limit
        self.__chat_history = queue.Queue(self.__max_chat_limit)
        self.__chat_history.put_nowait({"role": "system", "content": self.__system_msg})

    def send_chat(self, msg):
        if self.__chat_history.qsize() >= self.__max_chat_limit:
            self.__chat_history.get_nowait()
            self.__chat_history.get_nowait()
            logger.debug(f"Current chat history length = {self.__chat_history.qsize()}/{self.__max_chat_limit}")
        self.__chat_history.put_nowait({"role": "user", "content": msg})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=list(self.__chat_history.queue)
        )
        response_content = response['choices'][0]['message']['content']
        logger.debug(response_content)
        self.__chat_history.put_nowait({"role": "assistant", "content": response_content})
        return response_content

    def clear_chat_history(self):
        self.__chat_history = [{"role": "system", "content": self.__system_msg}]


class SingleConversation:
    def __init__(self, system_msg='You are a helpful assistant.'):
        """
        Initialize a new single conversation without context
        :param system_msg: Many conversations begin with a system message to gently instruct the assistant. For example,
         here is one of the system messages used for ChatGPT:
        You are ChatGPT, a large language model trained by OpenAI. Answer as concisely as possible. Knowledge cutoff:
        {knowledge_cutoff} Current date: {current_date}
        In general, gpt-3.5-turbo-0301 does not pay strong attention to the system message, and therefore important
        instructions are often better placed in a user message.
        """
        if openai.api_key is None:
            openai.api_key = settings.api_keys
        self.__system_msg = system_msg
        self.__chat_history = [{"role": "system", "content": self.__system_msg}]

    def send_chat(self, msg):
        self.__chat_history.append({"role": "user", "content": msg})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.__chat_history
        )
        response_content = response['choices'][0]['message']['content']
        logger.info(response_content)
        return response_content
