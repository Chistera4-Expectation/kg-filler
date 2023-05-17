import re
from dataclasses import dataclass
import typing
import hashlib


PATTERN_INLINE_LIST_ITEM = re.compile(r"(?:,\s+(?:and\s+)?)?([^,.]+)", re.IGNORECASE)
PATTERN_LIST_ITEM = re.compile(r"^\n?(?:\d+.|[-*+]|[#]+)\s*(.*?)$", re.MULTILINE)
PATTERN_ITEM_WITH_PARENTHESES = re.compile(r"(?:[,;])?(.+?)(?:\s+\((.+?)\))")
PATTERN_ITEM_WITH_DETAILS = re.compile(r"(.+?)(?:(?:\s+-+\s+|:\s+)(.+))")


DEFAULT_SEPARATING_WORDS = {"and", "with", "or"}


def split_recursively(text: str, separators: typing.List[str] = None) -> typing.Iterable[str]:
    if separators is None:
        separators = list(DEFAULT_SEPARATING_WORDS)
    if len(separators) == 0:
        yield text.strip()
    else:
        for item in text.split(separators[0]):
            yield from split_recursively(item, separators[1:])


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
    
    def split_by_words(self, words: typing.List[str] = None) -> typing.List[str]:
        if words is not None and any(word in self.value for word in words):
            return list(split_recursively(self.value, words))
        else:
            return [self.value]

    def __str__(self) -> str:
        return self.value + (f" ({self.metadata})" if self.metadata else "")
    

def str_hash(input: str, hash_function = 'sha256') -> str:
    hashf = getattr(hashlib, hash_function)
    return hashf(input.encode("utf-8")).hexdigest()


def _listify_lines(text: str, skip_first: bool = None, skip_last: bool=None) -> typing.List[str]:
    if skip_first is None:
        skip_first = True
    if skip_last is None:
        skip_last = True
    items = PATTERN_LIST_ITEM.findall(text)
    if skip_first:
        items = items[1:]
    if skip_last:
        items = items[:-1]
    return items


def _listify_line(text: str, skip_first: bool = None, skip_last: bool=None) -> typing.List[str]:
    if skip_first is None:
        skip_first = False
    if skip_last is None:
        skip_last = False
    items = []
    for match in PATTERN_INLINE_LIST_ITEM.finditer(text):
        items.append(match.group(1).strip())
    return items


def listify(text: str, skip_first: bool = None, skip_last: bool=None) -> typing.List[str]:
    if "\n" in text:
        return _listify_lines(text, skip_first, skip_last)
    elif PATTERN_LIST_ITEM.fullmatch(text):
        return _listify_lines(text, False, False)
    else:
        return _listify_line(text, skip_first, skip_last)


def itemize(text: str, skip_first: bool = None, skip_last: bool=None) -> typing.List[Item]:
    items = []
    for item in listify(text, skip_first, skip_last):
        items.extend(Item.from_string(item))
    return items
