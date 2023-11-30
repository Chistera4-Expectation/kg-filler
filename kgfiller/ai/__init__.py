import os
import pathlib
import time
import typing
from dataclasses import dataclass

import yaml
from lazy_property import LazyProperty

from kgfiller import logger, PATH_DATA_DIR
from kgfiller.text import itemize, str_hash, Item
from kgfiller.utils import get_env_var


DEFAULT_BACKGROUND = get_env_var("BACKGROUND", "You're a dietician", "AI background")
DEFAULT_LIMIT = int(get_env_var("LIMIT", "100", "AI prompt limit"))


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
    def _limit_error(cls) -> typing.Type[Exception] | typing.Iterable[typing.Type[Exception]]:
        ...

    @LazyProperty
    def _chat_completion(self):
        timeout = 30  # seconds
        while True:
            try:
                return self._chat_completion_step()
            except Exception as e:
                errors = self._limit_error()
                if not isinstance(errors, typing.Iterable):
                    errors = [errors]
                if any(isinstance(e, t) for t in errors):
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

    def _chat_completion_to_dict(self, chat_completion) -> str:
        ...

    @property
    def api(self):
        return self.__class__.__name__

    def _cache(self):
        overwrite = self.cache_path.exists()
        verb = "Overwriting cache of" if overwrite else "Caching"
        logger.debug("%s query `%s` into file %s", verb, self, self.cache_path.absolute())
        completion = self._chat_completion_to_dict(self._chat_completion)
        with open(self.cache_path, "w") as f:
            print(f"# Cache for query: {self.question}", file=f)
            print(f"# (api: {self.api}, model: {self.model}, background: '{self.background}', limit: {self.limit}", end='', file=f)
            print(f", attempt: {self.attempt})" if self.attempt is not None else ')', file=f)
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

    def _extract_text_from_result(self, result) -> str:
        ...
        
    @property
    def result_text(self) -> str:
        return self._extract_text_from_result(self.result)
    
    def result_to_list(self) -> typing.List[Item]:
        return itemize(self.result_text)


DEFAULT_API: type = None


def ai_query(question: str, model: str = None, limit: int = None, attempt: int = None, background: str = None, api: type = None) -> AiQuery:
    if api is None:
        global DEFAULT_API
        api = DEFAULT_API
    limit = limit or DEFAULT_LIMIT
    return api(
        question=question,
        model=model,
        limit=limit,
        attempt=attempt,
        background=background
    )


def load_api_from_env(variable_name="API", default_api="almaai"):
    api = get_env_var(variable_name, default_api, "API type")
    if api == "almaai":
        import kgfiller.ai.openai as api
        api.almmai_endpoint()
    elif api == "openai":
        import kgfiller.ai.openai as api
    elif api == "hugging":
        import kgfiller.ai.hugging as api
    elif api == "anthropic":
        import kgfiller.ai.anthropic as api
    else:
        raise ValueError("Unknown API: " + api)
    logger.debug(f"Using API: {api.__name__} from environment variable: {variable_name}")
    return api
