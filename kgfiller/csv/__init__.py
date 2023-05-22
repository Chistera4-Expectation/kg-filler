import csv
from kgfiller import PATH_DATA_DIR, logger
import typing
import pathlib
from kgfiller.text import Item


PATH_DATASET = PATH_DATA_DIR / "dataset.csv"
logger.debug("PATH_DATASET = %s", PATH_DATASET.absolute())


# def is_list(string: str) -> bool:
#     return (string.startswith("[") and string.endswith("]")) or "," in string


def parse_as_list(string: str) -> typing.Generator[Item, None, None]:
    if string.startswith("[") and string.endswith("]"):
        string = string[1:-1]
    for token in string.split(","):
        token = token.strip()
        for apices in ["'", '"']:
            if token.startswith(apices) and token.endswith(apices):
                token = token[1:-1]
        yield from Item.from_string(token)


def load_dataset(list_fields: typing.Iterable[str],
                 path: pathlib.Path = PATH_DATASET) -> typing.Generator[typing.Dict[str, str], None, None]:
    with open(path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for k, v in row.items():
                if k in list_fields:
                    row[k] = list(parse_as_list(v))
            yield row
