import typing
from dataclasses import dataclass

from hugchat import hugchat
from hugchat.login import Login

from kgfiller import logger, unescape
import kgfiller.ai as ai
from kgfiller.utils import get_env_var
from tempfile import mkdtemp

DEFAULT_MODEL = get_env_var("MODEL", "mistral", "Hugging model")
DEFAULT_BACKGROUND = ai.DEFAULT_BACKGROUND

username = get_env_var("HUGGING_USERNAME", "", "Hugging username")
password = get_env_var("HUGGING_PASSWORD", "", "Hugging password")


def _get_hugging_message_text(message: hugchat.Message) -> str:
    if hasattr(message, 'text'):
        return unescape(message.text)
    elif isinstance(message, dict) and 'text' in message:
        return unescape(message['text'])
    else:
        return unescape(str(message))


@dataclass
class HuggingAiStats:
    total_api_calls: int = 0
    total_tokens: int = 0

    def plus(self, other: hugchat.Message):
        self.total_api_calls += 1
        self.total_tokens += len(_get_hugging_message_text(other).split())

    def print(self, prefix: str = None):
        if prefix:
            print(prefix, end='')
        print("total API calls:", self.total_api_calls, "total tokens:", self.total_tokens, flush=True)


stats = HuggingAiStats()


_cookies = None


def _hugging_sign_in(username=username, password=password):
    global _cookies
    if _cookies is None:
        sign = Login(username, password)
        cookie_path_dir = mkdtemp("hugging-cookies")
        sign.saveCookiesToDir(cookie_path_dir)
        _cookies = sign.login()
    return _cookies


_chatbot = None


def _hugging_chat_bot(username=username, password=password):
    cookies = _hugging_sign_in(username, password)
    global _chatbot
    if _chatbot is None:
        _chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
    return _chatbot


class HuggingAiQuery(ai.AiQuery):
    def __init__(self, **kwargs):
        if "model" not in kwargs or kwargs["model"] is None:
            kwargs["model"] = DEFAULT_MODEL
        if "background" not in kwargs or kwargs["background"] is None:
            kwargs["background"] = DEFAULT_BACKGROUND
        super().__init__(**kwargs)

    def _create_chatbot(self):
        # cookies = _hugging_sign_in()
        # return hugchat.ChatBot(cookies=cookies.get_dict())
        return _hugging_chat_bot()

    def _new_conversation(self, chat_bot):
        id = chat_bot.new_conversation()
        chat_bot.change_conversation(id)

    def _select_llm(self, chat_bot):
        candidates = [(index, model) for index, model in enumerate(chat_bot.get_available_llm_models())
                      if self.model.lower() in model.name.lower()]
        if candidates:
            chat_bot.switch_llm(candidates[0][0])
            self.model = candidates[0][1]
        else:
            logger.warning(f"Model ${self.model} not found, using default")

    def _chat_completion_step(self):
        chat_bot = self._create_chatbot()
        self._new_conversation(chat_bot)
        self._select_llm(chat_bot)
        self._new_conversation(chat_bot)
        result = chat_bot.query(self.background + ".\n" + self.question, truncate=self.limit)
        result.wait_until_done()
        stats.plus(result)
        return result

    @classmethod
    def _limit_error(cls) -> typing.Iterable[typing.Type[Exception]]:
        return hugchat.exceptions.ModelOverloadedError, hugchat.exceptions.ChatError

    def _chat_completion_to_dict(self, chat_completion) -> dict:
        return {
            'text': chat_completion.text,
            'error': chat_completion.error,
            'msg_status': chat_completion.msg_status,
        }

    def _extract_text_from_result(self, result) -> str:
        return _get_hugging_message_text(result)


ai.DEFAULT_API = HuggingAiQuery
