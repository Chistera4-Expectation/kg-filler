import typing
from dataclasses import dataclass

import openai
import yaml

from kgfiller import unescape
import kgfiller.ai as ai
from kgfiller.utils import get_env_var


DEFAULT_MODEL = get_env_var("MODEL", "gpt-3.5-turbo", "OpenAI model")
DEFAULT_BACKGROUND = ai.DEFAULT_BACKGROUND

openai.api_key = get_env_var("OPENAI_API_KEY", "null", "OpenAI API key")


def change_endpoint(endpoint: str):
    openai.api_base = endpoint


def almmai_endpoint():
    change_endpoint("http://clusters.almaai.unibo.it:23231/v1")
    global DEFAULT_MODEL
    DEFAULT_MODEL = get_env_var("MODEL", "vicuna", "OpenAI model")


@dataclass
class OpenAiStats:
    total_api_calls: int = 0
    total_tokens: int = 0

    def plus(self, other: openai.ChatCompletion):
        self.total_api_calls += 1
        self.total_tokens += other.usage.total_tokens

    def print(self, prefix: str = None):
        if prefix:
            print(prefix, end='')
        print("total API calls:", self.total_api_calls, "total tokens:", self.total_tokens, flush=True)


stats = OpenAiStats()


class OpenAiQuery(ai.AiQuery):
    def __init__(self, **kwargs):
        if "model" not in kwargs or kwargs["model"] is None:
            kwargs["model"] = DEFAULT_MODEL
        if "background" not in kwargs or kwargs["background"] is None:
            kwargs["background"] = DEFAULT_BACKGROUND
        super().__init__(**kwargs)

    def _chat_completion_step(self) -> openai.ChatCompletion:
        result = openai.ChatCompletion.create(
            model=self.model,
            max_tokens=self.limit,
            messages=[
                {"role": "system", "content": self.background},
                {"role": "user", "content": self.question}
            ]
        )
        stats.plus(result)
        return result

    @classmethod
    def _limit_error(cls) -> typing.Iterable[typing.Type[Exception]]:
        return openai.error.RateLimitError, openai.error.Timeout, openai.error.APIConnectionError

    def _chat_completion_to_dict(self, chat_completion) -> dict:
        return yaml.safe_load(str(chat_completion))

    def _extract_text_from_result(self, result) -> str:
        return unescape(result['choices'][0]['message']['content'])


ai.DEFAULT_API = OpenAiQuery
