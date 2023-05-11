import logging
import pathlib


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


def escape(string: str) -> str:
    return string.translate(ESCAPED)


def unescape(string: str) -> str:
    for k, v in UNESCAPED.items():
        if k in string:
            string = string.replace(k, v)
    return string
