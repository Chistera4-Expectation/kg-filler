import hashlib
import re
import typing
from dataclasses import dataclass
import nltk
nltk.download('wordnet')
from nltk.corpus import wordnet


PATTERN_BULLETED = re.compile(r"[-*+]|[#]+")
PATTERN_NUMBERED = re.compile(r"\d+.")
PATTERN_INLINE_LIST_ITEM = re.compile(r"(\d+.|[-*+]|[#]+)\s*(.*?)(?=\d+.|[-*+]|[#]+|$)")
PATTERN_INTEXT_LIST_ITEM = re.compile(r"(?:,\s+(?:and\s+)?)?([^,.]+)", re.IGNORECASE)
PATTERN_LIST_ITEM = re.compile(r"^\n?(\d+.|[-*+]|[#]+)\s*(.*?)$", re.MULTILINE)
PATTERN_ITEM_WITH_PARENTHESES = re.compile(r"(?:[,;])?(.+?)(?:\s+\((.+?)\))")
PATTERN_ITEM_WITH_DETAILS = re.compile(r"(.+?)(?:(?:\s+-+\s+|:\s+)(.+))")
PATTERN_ITEM_WITH_OR_OPTION = re.compile(r"(.+?)(?:\s+or+\s+)(.+)")


DEFAULT_SEPARATING_WORDS = {"and", "with", "or"}


def split_recursively(text: str, separators: typing.Iterable[str] = None) -> typing.Iterable[str]:
    if separators is None:
        separators = list(DEFAULT_SEPARATING_WORDS)
    elif isinstance(separators, typing.Iterable) and not isinstance(separators, typing.List):
        separators = list(separators)
    if len(separators) == 0:
        yield text.strip()
    else:
        for item in text.split(separators[0]):
            yield from split_recursively(item, separators[1:])


def _is_meaningful_word(word: str) -> bool:
    if word:
        return len(wordnet.synsets(word.split()[-1].lower())) > 0
    return False


class Prefix:
    def __init__(self, value) -> None:
        self.value = value

    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"Prefix('{self.value}')"

    @property
    def is_empty(self) -> bool:
        return self.value == ""
    
    @property
    def is_numbered(self) -> bool:
        return PATTERN_NUMBERED.fullmatch(self.value) is not None
    
    @property
    def is_bulleted(self) -> bool:
        return PATTERN_BULLETED.fullmatch(self.value) is not None
    
    def __eq__(self, other: object) -> bool:
        return isinstance(other, Prefix) and self.is_empty == other.is_empty and self.is_bulleted == other.is_bulleted \
               and self.is_numbered == other.is_numbered
    
    def __hash__(self) -> int:
        return hash((self.is_empty, self.is_bulleted, self.is_numbered))


@dataclass
class Item:
    value: str
    metadata: typing.Optional[str] = None
    prefix: Prefix = Prefix("")

    @staticmethod
    def from_string(prefix: str, string: str) -> typing.List["Item"]:
        prefix = Prefix(prefix)
        items = []
        for match in PATTERN_ITEM_WITH_PARENTHESES.finditer(string):
            items.append(Item(value=match.group(1).strip(), prefix=prefix))
        if '(' in string and ')' not in string:
            items.append(Item(value=string.split('(')[0].strip(), prefix=prefix))
        for match in PATTERN_ITEM_WITH_DETAILS.finditer(string):
            items.append(Item(value=match.group(1).strip(), prefix=prefix))
        if len(items) == 0:
            items.append(Item(value=string.strip(), prefix=prefix))
        return items
    
    def is_meaningful(self) -> bool:
        return _is_meaningful_word(self.value.split()[-1])
    
    def split_by_words(self, words: typing.Iterable[str] = None) -> typing.List[str]:
        if words is None:
            words = DEFAULT_SEPARATING_WORDS
        words = [f" {w} " for w in words]
        if any(word in self.value for word in words):
            return list(split_recursively(self.value, words))
        else:
            return [self.value]

    def __str__(self) -> str:
        return self.value + (f" ({self.metadata})" if self.metadata else "")
    

def str_hash(input: str, hash_function = 'sha256') -> str:
    hashf = getattr(hashlib, hash_function)
    return hashf(input.encode("utf-8")).hexdigest()


def _listify_lines(text: str) -> typing.List[typing.Tuple[str, str]]:
    return PATTERN_LIST_ITEM.findall(text)


def _listify_line(text: str) -> typing.List[typing.Tuple[str, str]]:
    items = []
    for match in PATTERN_INLINE_LIST_ITEM.finditer(text):
        items.append(match.groups())
    if not items:
        for match in PATTERN_INTEXT_LIST_ITEM.finditer(text):
            items.append(("", match.group(1).strip()))
    return items


def listify(text: str) -> typing.List[typing.Tuple[str, str]]:
    if "\n" in text:
        return _listify_lines(text)
    else:
        return _listify_line(text)


def _itemize(text: str) -> typing.Iterable[Item]:
    for prefix_item in listify(text):
        for item in Item.from_string(*prefix_item):
            for word in item.split_by_words():
                yield Item(value=word, prefix=item.prefix)


def itemize(text: str) -> typing.List[Item]:
    text = text.strip()
    items = list(_itemize(text))
    if len(items) >= 2 and items[0].prefix != items[1].prefix:
        items = items[1:]
    items = [item for item in items if item.is_meaningful()]
    return items
