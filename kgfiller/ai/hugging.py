import os
import typing
from dataclasses import dataclass

from hugchat import hugchat
from hugchat.login import Login
import yaml

from kgfiller import logger, unescape
import kgfiller.ai as ai
from tempfile import mkdtemp


DEFAULT_MODEL = "hugging_mistral"
DEFAULT_BACKGROUND = "You're a dietician."


username = os.environ['HUG_NAME'] if "HUG_NAME" in os.environ else "None"
password = os.environ['HUG_PWD'] if "HUG_PWD" in os.environ else "None"
if username and password:
    logger.debug("Loaded Hugging face account credentials from environment variable HUG_NAME and HUG_PWD")
else:
    logger.warning("Environment variables HUG_NAME and HUG_PWD unset or empty")



@dataclass
class HuggingAiStats:
    total_api_calls: int = 0
    total_tokens: int = 0

    def plus(self, other: hugchat.Message):
        self.total_api_calls += 1
        self.total_tokens += other.text.count

    def print(self, prefix: str = None):
        if prefix:
            print(prefix, end='')
        print("total API calls:", self.total_api_calls, "total tokens:", self.total_tokens, flush=True)


stats = HuggingAiStats()


class HuggingAiQuery(ai.AiQuery):
    def __init__(self, **kwargs):
        if "model" not in kwargs or kwargs["model"] is None:
            kwargs["model"] = DEFAULT_MODEL
        if "background" not in kwargs or kwargs["background"] is None:
            kwargs["background"] = DEFAULT_BACKGROUND
        super().__init__(**kwargs)

    def _create_chatbot(self):
        sign = Login(username, password)
        cookies = sign.login()
        cookie_path_dir = mkdtemp("hugging-cookies")
        sign.saveCookiesToDir(cookie_path_dir)
        return hugchat.ChatBot(cookies=cookies.get_dict())

    def _select_llm(self, chat_bot):
        chosen_model_index = None
        for index, av_model in enumerate(chat_bot.get_available_llm_models()):
            if self.model.split('_')[-1].lower() in av_model.name.lower():
                chosen_model_index = index
        if chosen_model_index is not None:
            chat_bot.switch_llm(chosen_model_index)

    def _chat_completion_step(self):
        chat_bot = self._create_chatbot()
        self._select_llm(chat_bot)
        id = chat_bot.new_conversation()
        chat_bot.change_conversation(id)
        result = chat_bot.query(self.background + ".\n" + self.question, truncate=self.limit)
        result.wait_until_done()
        return result

    @classmethod
    def _limit_error(cls) -> typing.Type[Exception]:
        return hugchat.exceptions.ModelOverloadedError

    def _chat_completion_to_yaml(self) -> str:
        # TODO @andagio dobbiamo guardarci insieme qui
        return yaml.safe_load(str(self._chat_completion))

    def _extract_text_from_result(self) -> str:
        if 'mistral' in self.model:
            return unescape(self.result)
        elif 'falcon' in self.model:
            return unescape(self.result['text'])
        elif 'openchat' in self.model:
            return unescape(self.result['text'])


ai.DEFAULT_API = HuggingAiQuery