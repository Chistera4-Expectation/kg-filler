from kgfiller import logger, Commitable, Commit
from kgfiller.utils import first_or_none
from kgfiller.kg import KnowledgeGraph, human_name
from kgfiller.ai import ai_query
import owlready2 as owlready
import typing


CLASS_NAME = "__CLASS_NAME__"
CLASS_NAME_FANCY = "__CLASS_NAME_FANCY_"
INSTANCE_NAME = "__INSTANCE_NAME__"
INSTANCE_NAME_FANCY = "__INSTANCE_NAME_FANCY_"
RELATION_NAME = "__RELATION_NAME__"
RELATION_NAME_FANCY = "__RELATION_NAME_FANCY_"
CLASS_LIST = "__CLASS_LIST__"
CLASS_LIST_FANCY = "__CLASS_LIST_FANCY_"


def _apply_replacements(pattern: str, replacements: typing.Dict[str, str]) -> str:
    for key, value in replacements.items():
        pattern = pattern.replace(key, value)
    return pattern


def find_instances_for_class(kg: KnowledgeGraph, cls: owlready.ThingClass, queries: typing.List[str], max_retries: int = 2) -> Commitable:
    replacements = {
        CLASS_NAME: cls.name,
        CLASS_NAME_FANCY: human_name(cls),
    }
    questions = [_apply_replacements(pattern, replacements) for pattern in queries]
    for question in questions:
        files = [kg.path]
        for attempt in range(0, max_retries):
            query = ai_query(question=question, attempt=attempt if attempt > 0 else None)
            results = list(query.result_to_list())
            if len(results) == 0:
                logger.warning("No results for query '%s', AI answer: %s", query.question, query.result_text)
                continue
            description = f"Query: {query.question}.\nAnswers:"
            for result in results:
                instance = kg.add_instance(cls, result.value)
                description += f"\n- {result} => adding instance {instance.name} to class {cls.name}"
            files.append(query.cache_path)
            description += f"\nQuery cache in files:"
            for file in files[1:]:
                description += f"\n- {str(file)}"
            return Commit(
                message=f"add {len(results)} instances to class {cls.name} from AI answer",
                description=description,
                files=files,
            )


def find_related_instances(kg: KnowledgeGraph, instance: owlready.Thing, relation: owlready.ObjectPropertyClass, default_class: owlready.ThingClass, queries: typing.List[str], instance_as_object: bool = False, max_retries: int = 2) -> Commitable:
    replacements = {
        INSTANCE_NAME: instance.name,
        INSTANCE_NAME_FANCY: human_name(instance),
        RELATION_NAME: relation.name,
        RELATION_NAME_FANCY: human_name(relation),
    }
    questions = [_apply_replacements(pattern, replacements) for pattern in queries]
    for question in questions:
        files = [kg.path]
        for attempt in range(0, max_retries):
            query = ai_query(question=question, attempt=attempt if attempt > 0 else None)
            results = list(query.result_to_list())
            if len(results) == 0:
                logger.warning("No results for query '%s', AI answer: %s", query.question, query.result_text)
                continue
            description = f"Query: {query.question}.\nAnswers:"
            for result in results:
                for word in result.split_by_words():
                    new_instance = kg.add_instance(default_class, word)
                    if instance_as_object:
                        kg.add_property(new_instance, relation, instance)
                    else:
                        kg.add_property(instance, relation, new_instance)
                    description += f"\n- {word} => adding instance {new_instance.name} to class {default_class.name}, and relate it to {instance.name} as {relation.name}"
            files.append(query.cache_path)
            description += f"\nQuery cache in files:"
            for file in files[1:]:
                description += f"\n- {str(file)}"
            return Commit(
                message=f"add {len(results)} instances to class {default_class.name}, and as many relations to instance {instance.name} from AI answer",
                description=description,
                files=files,
            )


def move_to_most_adequate_subclass(kg: KnowledgeGraph, instance: owlready.Thing, root_class: owlready.ThingClass, queries: typing.List[str], max_retries: int = 2) -> Commitable:
    sub_types_by_name = dict()
    replacements = {
        INSTANCE_NAME: instance.name,
        INSTANCE_NAME_FANCY: human_name(instance),
        CLASS_NAME: root_class.name,
        CLASS_NAME_FANCY: human_name(root_class),
        CLASS_LIST: set(),
        CLASS_LIST_FANCY: set(),
    }
    for cls in root_class.subclasses():
        replacements[CLASS_LIST].add(f"'{cls.name}'")
        replacements[CLASS_LIST_FANCY].add(f"'{human_name(cls)}'")
        sub_types_by_name[cls.name] = cls
        sub_types_by_name[human_name(cls)] = cls
    replacements[CLASS_LIST] = ", ".join(replacements[CLASS_LIST])
    replacements[CLASS_LIST_FANCY] = ", ".join(replacements[CLASS_LIST_FANCY])
    questions = [_apply_replacements(pattern, replacements) for pattern in queries]
    for question in questions:
        files = [kg.path]
        for attempt in range(0, max_retries):
            query = ai_query(question=question, attempt=attempt if attempt > 0 else None)
            result = first_or_none(cls for name, cls in sub_types_by_name.items() if name in query.result_text)
            if result is None:
                logger.warning("Inconclusive answer for query '%s', AI answer: %s", query.question, query.result_text)
                continue
            description = f"Query: {query.question}.\nAnswer:\n\t{query.result_text}"
            description += f"\nmeaning that the most adequate type for {instance.name} is {result.name}."
            instance = kg.add_instance(result, instance.name)
            description += f"Current classes of {instance.name} are:"
            for cls in instance.is_a:
                description += f"\n- {cls.name}"
            files.append(query.cache_path)
            description += f"\nQuery cache in files:"
            for file in files[1:]:
                description += f"\n- {str(file)}"
            return Commit(
                message=f"make {instance.name} an instance of classes {[cls.name for cls in instance.is_a]} from AI answer",
                description=description,
                files=files,
            )
