from kgfiller import logger, Commitable, Commit
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


def find_related_instances(kg: KnowledgeGraph, instance: owlready.Thing, relation: owlready.ObjectPropertyClass, default_class: owlready.ThingClass, queries: typing.List[str], max_retries: int = 2) -> Commitable:
    replacements = {
        INSTANCE_NAME: instance.name,
        INSTANCE_NAME_FANCY: human_name(instance),
        RELATION_NAME: relation.name,
        RELATION_NAME_FANCY: human_name(relation),
    }
    questions = [_apply_replacements(pattern, replacements) for pattern in queries]
    for question in questions:
        for attempt in range(0, max_retries):
            query = ai_query(question=question, attempt=attempt if attempt > 0 else None)
            results = list(query.result_to_list())
            if len(results) == 0:
                logger.warning("No results for query '%s', AI answer: %s", query.question, query.result_text)
                continue
            description = f"Query: {query.question}.\nAnswers:"
            for result in results:
                new_instance = kg.add_instance(default_class, result.value)
                kg.add_property(instance, relation, new_instance)
                description += f"\n- {result} => adding instance {new_instance.name} to class {default_class.name}, and relate it to {instance.name} as {relation.name}"
            files = [kg.path, query.cache_path]
            description += f"\nQuery cache in file: {str(files[1])}"
            return Commit(
                message=f"add {len(results)} instances to class {default_class.name}, and as many relations to instance {instance.name} from AI answer",
                description=description,
                files=files,
            )

