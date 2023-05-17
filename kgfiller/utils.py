import typing


def overlap(a: typing.Iterable, b: typing.Iterable) -> bool:
    met_in_a = set()
    met_in_b = set()
    iter_a = iter(a)
    iter_b = iter(b)
    try:
        while True:
            item_a = next(iter_a)
            if item_a in met_in_b:
                return True
            met_in_a.add(item_a)
            item_b = next(iter_b)
            if item_b in met_in_a:
                return True
            met_in_b.add(item_b)
    except StopIteration:
        return False


def first(iterable: typing.Iterable[typing.Any]) -> typing.Any:
    return next(iter(iterable))


def first_or_none(iterable: typing.Iterable[typing.Any]) -> typing.Any:
    try:
        return first(iterable)
    except StopIteration:
        return None
