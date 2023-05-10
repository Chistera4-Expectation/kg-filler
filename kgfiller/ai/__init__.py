import openai
import os
from kgfiller import logger, PATH_DATA_DIR
import pathlib
from dataclasses import dataclass
from lazy_property import LazyProperty
import hashlib
import json
import typing


openai.api_key = os.environ["OPENAI_API_KEY"] if "OPENAI_API_KEY" in os.environ else None
if openai.api_key:
    logger.debug("Loaded API key from environment variable OPENAI_API_KEY")
else:
    logger.warning("Environment variable OPENAI_API_KEY unset or empty")


def _str_hash(input: str, hash_function = 'sha256') -> str:
    hashf = getattr(hashlib, hash_function)
    return hashf(input.encode("utf-8")).hexdigest()

@dataclass
class OpenAiStats:
    total_api_calls: int = 0
    total_tokens: int = 0

    def plus(self, other: openai.ChatCompletion):
        self.total_api_calls += 1
        self.total_tokens += other.usage.total_tokens


stats = OpenAiStats()


@dataclass
class AiQuery:
    question: str
    model: str
    limit: int

    @LazyProperty
    def _chat_completion(self) -> openai.ChatCompletion:
        result = openai.ChatCompletion.create(
            model=self.model,
            max_tokens=self.limit,
            messages=[
                {"role": "user", "content": self.question}
            ]
        )
        stats.plus(result)
        return result

    @LazyProperty
    def _cache_path(self) -> pathlib.Path:
        id = _str_hash(f"query#{self.question}#{self.model}#{self.limit}")
        return PATH_DATA_DIR / f"cache-{id}.json"

    def _cache(self):
        overwrite = self._cache_path.exists()
        verb = "Overwriting cache of" if overwrite else "Caching"
        logger.debug("%s query `%s` into file %s", verb, self, self._cache_path.absolute())
        with open(self._cache_path, "w") as f:
            completion = self._chat_completion
            f.write(str(completion))

    def _parse_cache(self) -> dict:
        logger.debug("Parsing cache file %s", self._cache_path.absolute())
        if not self._cache_path.exists():
            raise FileNotFoundError(f"Cache file {self._cache_path.absolute()} does not exist")
        with open(self._cache_path, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                logger.warning("Removing invalid cache file %s", self._cache_path.absolute())
                self._cache_path.unlink()
                return None

    @property
    def result(self) -> typing.Union[openai.ChatCompletion, dict]:
        if not self._cache_path.exists():
            self._cache()
            return self._chat_completion
        else:
            return self._parse_cache() or self._chat_completion
        
    @property
    def result_text(self) -> str:
        return self.result['choices'][0]['message']['content']


def query(question: str, model: str = "gpt-3.5-turbo", limit: int = 100) -> AiQuery:
    return AiQuery(question=question, model=model, limit=limit)
