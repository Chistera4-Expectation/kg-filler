import logging
import pathlib
import re
import typing


logger = logging.getLogger("kgfiller")
logger.setLevel(logging.DEBUG)


LOG_DEBUG = logging.DEBUG
LOG_INFO = logging.INFO
LOG_WARNING = logging.WARNING
LOG_ERROR = logging.ERROR
LOG_CRITICAL = logging.CRITICAL
LOG_FATAL = logging.FATAL


def enable_logging(level:int = LOG_DEBUG, format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'):
    handler = logging.StreamHandler()
    handler.setLevel(level)
    formatter = logging.Formatter(format)
    handler.setFormatter(formatter)
    logger.handlers.clear()
    logger.addHandler(handler)


PATH_DATA_DIR = pathlib.Path(__file__).parent.parent / "data"
logger.debug("PATH_DATA_DIR = %s", PATH_DATA_DIR.absolute())


ESCAPED = str.maketrans({"\n":  r"\n", "\n":  r"\n"})
UNESCAPED = {r"\n": "\n", r"\n": "\n"}
PATTERN_SYMBOLS = re.compile(r"[^A-Za-z\d_]")


def escape(string: str) -> str:
    return string.translate(ESCAPED)


def unescape(string: str) -> str:
    for k, v in UNESCAPED.items():
        if k in string:
            string = string.replace(k, v)
    return string


def replace_symbols_with(name: str, replacement: str) -> str:
    replaced = PATTERN_SYMBOLS.sub(replacement, name)
    while replaced.endswith(replacement):
        replaced = replaced[:-1]
    return replaced


class Commitable(typing.Protocol):
    @property
    def description(self) -> str:
        ...
    
    @property
    def message(self) -> str:
        ...
    
    @property
    def files(self) -> typing.List[pathlib.Path]:
        ...

    @property
    def should_commit(self) -> bool:
        ...

    def __eq__(self, other: object) -> bool:
        return self.message == other.message and self.description == other.description and self.files == other.files and self.should_commit == other.should_commit
    
    def __hash__(self) -> int:
        return hash((self.message, self.description, self.files, self.should_commit))

    def print(self):
        print(self.message)
        print(self.description)


class Commit(Commitable):
    def __init__(self, message: str, files: typing.List[pathlib.Path], description: str = None, should_commit: bool = True):
        self._message = message
        self._files = files
        self._description = description
        self._should_commit = should_commit

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value
    
    @property
    def message(self) -> str:
        return self._message

    @message.setter
    def message(self, value: str):
        self._message = value
    
    @property
    def files(self) -> typing.List[pathlib.Path]:
        return self._files
    
    @files.setter
    def files(self, value: typing.List[pathlib.Path]):
        self._files = value

    @property
    def should_commit(self) -> bool:
        return self._should_commit

    @should_commit.setter
    def should_commit(self, value: bool):
        self._should_commit = value

    def __str__(self) -> str:
        return f"Commit({self.message}, {self.files}, {self.description}, {self.should_commit})"
    
    def __repr__(self) -> str:
        return str(self)
