from kgfiller import logger, Commitable, Commit
from kgfiller.kg import KnowledgeGraph, create_query_for_instances
from kgfiller.ai import ai_query
import owlready2 as owlready


def find_instances_for_class(kg: KnowledgeGraph, cls: owlready.ThingClass, max_retries: int = 2) -> Commitable:
    for question in create_query_for_instances(cls):
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
            files = [kg.path, query.cache_path]
            description += f"\nQuery cache in file: {str(files[1])}"
            return Commit(
                message=f"add {len(results)} instances to class {cls.name} from AI answer",
                description=description,
                files=files,
            )
