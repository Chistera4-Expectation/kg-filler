import pathlib
import time
import typing
from dataclasses import dataclass

import yaml
from lazy_property import LazyProperty

from kgfiller import logger, PATH_DATA_DIR
from kgfiller.text import itemize, str_hash, Item


@dataclass
class AiQuery:
    question: str
    model: str
    limit: int
    attempt: int
    background: str

    def _chat_completion_step(self):
        ...

    @classmethod
    def _limit_error(cls) -> typing.Type[Exception]:
        ...

    @LazyProperty
    def _chat_completion(self):
        timeout = 30  # seconds
        while True:
            try:
                return self._chat_completion_step()
            except Exception as e:
                if isinstance(e, self._limit_error()):
                    logger.warning("Rate limit exceeded, retrying in %.2g seconds", timeout)
                    time.sleep(timeout)
                    timeout *= 1.5
                else:
                    raise e

    @property
    def id(self):
        fields = [self.question, self.model, self.limit, self.background, self.api]
        return "query#" + "#".join([str(f) for f in fields if f is not None])

    @LazyProperty
    def cache_path(self) -> pathlib.Path:
        id = str_hash(self.id)
        return PATH_DATA_DIR / f"cache-{id}.yml"

    def _chat_completion_to_yaml(self) -> str:
        ...

    @property
    def api(self):
        return self.__class__.__name__

    def _cache(self):
        overwrite = self.cache_path.exists()
        verb = "Overwriting cache of" if overwrite else "Caching"
        logger.debug("%s query `%s` into file %s", verb, self, self.cache_path.absolute())
        with open(self.cache_path, "w") as f:
            print(f"# Cache for query: {self.question}", file=f)
            print(f"# (api: {self.api}, model: {self.model}, background: {self.background}, limit: {self.limit}", end='', file=f)
            print(f", attempt: {self.attempt})" if self.attempt is not None else ')', file=f)
            completion = self._chat_completion_to_yaml()
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

    @LazyProperty
    def result(self):
        if not self.cache_path.exists():
            self._cache()
            return self._chat_completion
        else:
            return self._parse_cache() or self._chat_completion

    def _extract_text_from_result(self) -> str:
        ...
        
    @property
    def result_text(self) -> str:
        return self._extract_text_from_result()
    
    def result_to_list(self) -> typing.List[Item]:
        return itemize(self.result_text)


DEFAULT_API: type = None


def ai_query(question: str, model: str = None, limit: int = 100, attempt: int = None, background: str = None, api: type = None) -> AiQuery:
    if api is None:
        global DEFAULT_API
        api = DEFAULT_API
    return api(
        question=question,
        model=model,
        limit=limit,
        attempt=attempt,
        background=background
    )
