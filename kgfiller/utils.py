import typing
import os
import pathlib
import json
import yaml


PATH_REPO = pathlib.Path(__file__).parent.parent

def get_env_var(name: str, default: str, description) -> str:
    value = os.environ[name] if name in os.environ else None
    if value:
        print(f"Loaded {description} from environment variable {name}")
    else:
        print(f"Cannot load {description} because environment variable {name} is unset or empty. "
              f"Using default value: {default}")
        value = default
    return value

def load_queries_json():
    with open(os.path.join(PATH_REPO, "queries.json"), "r") as readfile:
        queries = json.load(readfile)
    chosen_onto = get_env_var('ONTOLOGY', 'food', 'Chosen ontology')
    chosen_api = get_env_var('API', 'almaai', 'Chosen API')
    chosen_model = get_env_var('MODEL', 'vicuna', 'Chosen model')
    return queries[chosen_onto][chosen_api][chosen_model]

def load_queries_yaml():
    print('Loading queries from yaml file at {}...'.format(os.path.join(PATH_REPO, "queries.yaml")))
    with open(os.path.join(PATH_REPO, "queries.yaml"), "r") as readfile:
        queries = yaml.safe_load(readfile)
    chosen_onto = get_env_var('ONTOLOGY', 'food', 'Chosen ontology')
    chosen_api = get_env_var('API', 'almaai', 'Chosen API')
    chosen_model = get_env_var('MODEL', 'vicuna', 'Chosen model')
    print('queries found: {}'.format(queries[chosen_onto][chosen_api][chosen_model]))
    return queries[chosen_onto][chosen_api][chosen_model]

def overlap(a: typing.Iterable, b: typing.Iterable) -> bool:
    met_in_a = set()
    met_in_b = set()
    iter_a = iter(a)
    iter_b = iter(b)
    over_a = False
    over_b = False
    while not (over_a and over_b):
        if not over_a:
            try:
                item_a = next(iter_a)
                if item_a in met_in_b:
                    return True
                met_in_a.add(item_a)
            except StopIteration:
                over_a = True
        if not over_b:
            try:
                item_b = next(iter_b)
                if item_b in met_in_a:
                    return True
                met_in_b.add(item_b)
            except StopIteration:
                over_b = True
    return False


def first(iterable: typing.Iterable[typing.Any]) -> typing.Any:
    return next(iter(iterable))


def first_or_none(iterable: typing.Iterable[typing.Any]) -> typing.Any:
    try:
        return first(iterable)
    except StopIteration:
        return None
