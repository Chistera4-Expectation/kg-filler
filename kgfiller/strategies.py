import typing

import owlready2 as owlready

from kgfiller import logger, Commitable, Commit
from kgfiller.ai import ai_query, AiQuery
from kgfiller.kg import KnowledgeGraph, human_name, is_leaf
from kgfiller.text import Item
from kgfiller.utils import first_or_none


CLASS_NAME = "__CLASS_NAME__"
CLASS_NAME_FANCY = "__CLASS_NAME_FANCY_"
INSTANCE_NAME = "__INSTANCE_NAME__"
INSTANCE_NAME_FANCY = "__INSTANCE_NAME_FANCY_"
RELATION_NAME = "__RELATION_NAME__"
RELATION_NAME_FANCY = "__RELATION_NAME_FANCY_"
CLASS_LIST = "__CLASS_LIST__"
CLASS_LIST_FANCY = "__CLASS_LIST_FANCY_"


DEFAULT_MAX_RETRIES = 2


def _apply_replacements(pattern: str, **replacements) -> str:
    for key, value in replacements.items():
        pattern = pattern.replace(key, value)
    return pattern


class QueryProcessor(Commit):
    def __init__(self):
        Commit.__init__(self, "", [], "", True)
        self._kg = None
        self._queries = []

    def reset(self, kg: KnowledgeGraph):
        self._kg = kg
        self.description = ""
        self.files = [kg.path]
        self.message = ""
        self.should_commit = True

    def final_message(self, kg: KnowledgeGraph, query: AiQuery, *results) -> str:
        raise NotImplementedError()

    def admissible(self, kg: KnowledgeGraph, query: AiQuery) -> bool:
        raise NotImplementedError()

    def process(self, kg: KnowledgeGraph, query: AiQuery):
        raise NotImplementedError()

    def __call__(self, query: AiQuery) -> bool:
        self._queries.append(query)
        self.files.append(query.cache_path)
        if not self.admissible(self._kg, query):
            return False
        results = self.process(self._kg, query)
        self.message = self.final_message(self._kg, query, *results)
        if not self.message:
            raise ValueError("No message set for query")
        if self.description:
            self.description = self.description.strip()
        return True

    def describe(self, msg: str, prefix='\n', suffix=''):
        self.description += prefix + msg + suffix

    def describe_caches(self):
        self.describe("Query cache in files:")
        for file in self.files[1:]:
            self.describe(f"- {str(file)}")

    def inconclusive(self):
        self.message = f"inconclusive sequence of {len(self._queries)} queries"
        self.should_commit = False
        self.description = ""
        self.describe("Queries:")
        for query in self._queries:
            self.describe(f"?- {query.question}\n\t!- {query.result_text}")


class MultipleResultsQueryProcessor(QueryProcessor):
    def __init__(self):
        super().__init__()
        self._results = []

    def admissible(self, kg: KnowledgeGraph, query: AiQuery) -> bool:
        self._results = query.result_to_list()
        return len(self._results) > 0

    def process(self, kg: KnowledgeGraph, query: AiQuery):
        self.describe(f"Query: {query.question}.\nAnswers:")
        results = []
        for result in self._results:
            r = self.process_result(kg, query, result)
            if isinstance(r, typing.Iterable):
                results.extend(r)
            else:
                results.append(r)
        return results

    def process_result(self, kg: KnowledgeGraph, query: AiQuery, result: Item) -> typing.Any:
        raise NotImplementedError()


class SingleResultQueryProcessor(QueryProcessor):
    def __init__(self):
        super().__init__()
        self._result = None

    def admissible(self, kg: KnowledgeGraph, query: AiQuery) -> bool:
        self._result = self.parse_result(kg, query)
        return self._result is not None

    def parse_result(self, kg: KnowledgeGraph, query: AiQuery) -> typing.Any:
        raise NotImplementedError()

    def process(self, kg: KnowledgeGraph, query: AiQuery):
        self.describe(f"Query: {query.question}.\nAnswer:\n\t{query.result_text}")
        return [self.process_result(kg, query, self._result)]

    def process_result(self, kg: KnowledgeGraph, query: AiQuery, result: typing.Any) -> typing.Any:
        raise NotImplementedError()


def _make_queries(kg: KnowledgeGraph,
                  queries: typing.List[str],
                  query_processor: QueryProcessor,
                  max_retries: int,
                  **replacements) -> Commitable:
    questions = [_apply_replacements(pattern, **replacements) for pattern in queries]
    query_processor.reset(kg)
    for question in questions:
        for attempt in range(0, max_retries):
            query = ai_query(question=question, attempt=attempt if attempt > 0 else None)
            if not query_processor(query):
                logger.warning("No results for query '%s', AI answer: %s", query.question, query.result_text)
                continue
            query_processor.describe_caches()
            return query_processor
    query_processor.inconclusive()
    return query_processor


def find_instances_for_class(kg: KnowledgeGraph,
                             cls: owlready.ThingClass,
                             queries: typing.List[str],
                             max_retries: int = DEFAULT_MAX_RETRIES) -> Commitable:
    class FindInstancesQueryProcessor(MultipleResultsQueryProcessor):
        def final_message(self, kg: KnowledgeGraph, query: AiQuery, *results) -> str:
            return f"add {len(results)} instances to class {cls.name} from AI answer"

        def process_result(self, kg: KnowledgeGraph, query: AiQuery, result: Item):
            instance = kg.add_instance(cls, result.value)
            self.describe(f"- {result} => adding instance {instance.name} to class {cls.name}")
            return instance

    replacements = {
        CLASS_NAME: cls.name,
        CLASS_NAME_FANCY: human_name(cls),
    }
    return _make_queries(kg, queries, FindInstancesQueryProcessor(), max_retries=max_retries, **replacements)


def find_related_instances(kg: KnowledgeGraph,
                           instance: owlready.Thing,
                           relation: owlready.ObjectPropertyClass,
                           default_class: owlready.ThingClass,
                           queries: typing.List[str],
                           instance_as_object: bool = False,
                           max_retries: int = DEFAULT_MAX_RETRIES) -> Commitable:
    class FindRelatedInstancesQueryProcessor(MultipleResultsQueryProcessor):
        def final_message(self, kg: KnowledgeGraph, query: AiQuery, *results) -> str:
            return f"add {len(results)} instances to class {default_class.name}, and as many relations " \
                   f"to instance {instance.name} from AI answer"

        def process_result(self, kg: KnowledgeGraph, query: AiQuery, result: Item):
            results = []
            for word in result.split_by_words():
                new_instance = kg.add_instance(default_class, word)
                if instance_as_object:
                    kg.add_property(new_instance, relation, instance)
                else:
                    kg.add_property(instance, relation, new_instance)
                self.describe(f"- {result} => adding instance {new_instance.name} to class {default_class.name}, and "
                              f"relate it to {instance.name} as {relation.name}")
                results.append(new_instance)
            return results

    replacements = {
        INSTANCE_NAME: instance.name,
        INSTANCE_NAME_FANCY: human_name(instance),
        RELATION_NAME: relation.name,
        RELATION_NAME_FANCY: human_name(relation),
    }
    return _make_queries(kg, queries, FindRelatedInstancesQueryProcessor(), max_retries=max_retries, **replacements)


def move_to_most_adequate_class(kg: KnowledgeGraph,
                                instance: owlready.Thing,
                                classes: typing.Iterable[owlready.ThingClass],
                                queries: typing.List[str],
                                max_retries: int = DEFAULT_MAX_RETRIES) -> Commitable:
    class MoveToMostAdequateClassQueryProcessor(SingleResultQueryProcessor):

        def final_message(self, kg: KnowledgeGraph, query: AiQuery, *results) -> str:
            instance = results[0]
            return f"make {instance.name} an instance of classes {[cls.name for cls in instance.is_a]} from AI answer"

        def parse_result(self, kg: KnowledgeGraph, query: AiQuery) -> typing.Any:
            return first_or_none(cls for name, cls in sub_types_by_name.items() if name in query.result_text)

        def process_result(self, kg: KnowledgeGraph, query: AiQuery, result: typing.Any):
            self.describe(f"meaning that the most adequate type for {instance.name} is {result.name}.")
            i = kg.set_class_of_instance(instance, result)
            self.describe(f"Current classes of {i.name} are:")
            for cls in i.is_a:
                self.describe(f"- {cls.name}")
            return i

    sub_types_by_name = dict()
    replacements = {
        INSTANCE_NAME: instance.name,
        INSTANCE_NAME_FANCY: human_name(instance),
        CLASS_LIST: set(),
        CLASS_LIST_FANCY: set(),
    }
    for cls in classes:
        replacements[CLASS_LIST].add(f"'{cls.name}'")
        replacements[CLASS_LIST_FANCY].add(f"'{human_name(cls)}'")
        sub_types_by_name[cls.name] = cls
        sub_types_by_name[human_name(cls)] = cls
    replacements[CLASS_LIST] = ", ".join(replacements[CLASS_LIST])
    replacements[CLASS_LIST_FANCY] = ", ".join(replacements[CLASS_LIST_FANCY])
    return _make_queries(kg, queries, MoveToMostAdequateClassQueryProcessor(), max_retries=max_retries, **replacements)


SubClassSelector = typing.Callable[[owlready.ThingClass], typing.Iterable[owlready.ThingClass]]


def direct_subclasses(cls: owlready.ThingClass) -> typing.Iterable[owlready.ThingClass]:
    return cls.subclasses()


def all_descendants(cls: owlready.ThingClass) -> typing.Iterable[owlready.ThingClass]:
    return cls.descendants()


def leaf_descendants(cls: owlready.ThingClass) -> typing.Iterable[owlready.ThingClass]:
    return (c for c in all_descendants(cls) if is_leaf(c))


def move_to_most_adequate_subclass(kg: KnowledgeGraph,
                                   instance: owlready.Thing,
                                   root_class: owlready.ThingClass,
                                   subclass_selector: SubClassSelector,
                                   queries: typing.List[str],
                                   max_retries: int = DEFAULT_MAX_RETRIES) -> Commitable:
    classes = subclass_selector(root_class)
    return move_to_most_adequate_class(kg, instance, classes, queries, max_retries=max_retries)
