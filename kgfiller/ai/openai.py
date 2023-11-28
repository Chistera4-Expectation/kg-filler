import os
import typing
from dataclasses import dataclass

import openai
import yaml

from kgfiller import logger, unescape
import kgfiller.ai as ai


DEFAULT_MODEL = "gpt-3.5-turbo"
DEFAULT_BACKGROUND = "You're a dietician."


openai.api_key = os.environ["OPENAI_API_KEY"] if "OPENAI_API_KEY" in os.environ else "None"
if openai.api_key:
    logger.debug("Loaded API key from environment variable OPENAI_API_KEY")
else:
    logger.warning("Environment variable OPENAI_API_KEY unset or empty")


def change_endpoint(endpoint: str):
    openai.api_base = endpoint


def almmai_endpoint():
    change_endpoint("http://clusters.almaai.unibo.it:23231/v1")
    global DEFAULT_MODEL
    DEFAULT_MODEL = "vicuna"


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
    def _limit_error(cls) -> typing.Type[Exception]:
        return openai.error.RateLimitError

    def _chat_completion_to_yaml(self) -> dict:
        return yaml.safe_load(str(self._chat_completion))

    def _extract_text_from_result(self) -> str:
        return unescape(self.result['choices'][0]['message']['content'])


ai.DEFAULT_API = OpenAiQuery
