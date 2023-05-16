import openai
import os
from kgfiller import logger, PATH_DATA_DIR, unescape
import pathlib
from dataclasses import dataclass
from lazy_property import LazyProperty
import hashlib
import yaml
import typing
import re
from dataclasses import dataclass
import time


PATTERN_LIST_ITEM = re.compile(r"^\n?(?:\d+.|[-*+]|[#]+|\s*)\s*(.*?)$", re.MULTILINE)
PATTERN_ITEM_WITH_PARENTHESES = re.compile(r"(?:[,;])?(.+?)(?:\s+\((.+?)\))")
PATTERN_ITEM_WITH_DETAILS = re.compile(r"(.+?)(?:(?:\s+-+\s+|:\s+)(.+))")


@dataclass
class Item:
    value: str
    metadata: typing.Optional[str] = None

    @staticmethod
    def from_string(string: str) -> typing.List["Item"]:
        items = []
        for match in PATTERN_ITEM_WITH_PARENTHESES.finditer(string):
            items.append(Item(match.group(1).strip(), match.group(2).strip()))
        for match in PATTERN_ITEM_WITH_DETAILS.finditer(string):
            items.append(Item(match.group(1).strip(), match.group(2).strip()))
        if len(items) == 0:
            items.append(Item(string.strip()))
        return items

    def __str__(self) -> str:
        return self.value + (f" ({self.metadata})" if self.metadata else "")


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

    def print(self, prefix: str = None):
        if prefix:
            print(prefix, end='')
        print("total API calls:", self.total_api_calls, "total tokens:", self.total_tokens, flush=True)


stats = OpenAiStats()


@dataclass
class AiQuery:
    question: str
    model: str
    limit: int
    attempt: int

    def _chat_completion_step(self) -> openai.ChatCompletion:
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
    def _chat_completion(self) -> openai.ChatCompletion:
        while True:
            try:
                return self._chat_completion_step()
            except openai.error.RateLimitError:
                logger.warning("Rate limit exceeded, retrying in 1 minute")
                time.sleep(60)
            
    
    @property
    def id(self):
        id = f"query#{self.question}#{self.model}#{self.limit}"
        if self.attempt is not None:
            id += f"#{self.attempt}"
        return id

    @LazyProperty
    def cache_path(self) -> pathlib.Path:
        id = _str_hash(self.id)
        return PATH_DATA_DIR / f"cache-{id}.yml"

    def _cache(self):
        overwrite = self.cache_path.exists()
        verb = "Overwriting cache of" if overwrite else "Caching"
        logger.debug("%s query `%s` into file %s", verb, self, self.cache_path.absolute())
        with open(self.cache_path, "w") as f:
            print(f"# Cache for query: {self.question}", file=f)
            print(f"# (model: {self.model}, limit: {self.limit}", end='', file=f)
            print(f", attempt: {self.attempt})" if self.attempt is not None else ')', file=f)
            completion = yaml.safe_load(str(self._chat_completion))
            yaml.dump(completion, f)

    def _parse_cache(self) -> dict:
        logger.debug("Parsing cache file %s", self.cache_path.absolute())
        if not self.cache_path.exists():
            raise FileNotFoundError(f"Cache file {self.cache_path.absolute()} does not exist")
        with open(self.cache_path, "r") as f:
            try:
                return yaml.safe_load(f)
            except yaml.YAMLError:
                logger.warning("Removing invalid cache file %s", self.cache_path.absolute())
                self.cache_path.unlink()
                return None

    @property
    def result(self) -> typing.Union[openai.ChatCompletion, dict]:
        if not self.cache_path.exists():
            self._cache()
            return self._chat_completion
        else:
            return self._parse_cache() or self._chat_completion
        
    @property
    def result_text(self) -> str:
        return unescape(self.result['choices'][0]['message']['content'])
    
    def result_to_list(self, skip_first: bool = True, skip_last=True) -> typing.List[str]:
        items = PATTERN_LIST_ITEM.findall(self.result_text)
        if skip_first:
            items = items[1:]
        if skip_last:
            items = items[:-1]
        return [i for item in items for i in Item.from_string(item)]


def ai_query(question: str, model: str = "gpt-3.5-turbo", limit: int = 100, attempt: int = None) -> AiQuery:
    return AiQuery(question, model, limit, attempt)
