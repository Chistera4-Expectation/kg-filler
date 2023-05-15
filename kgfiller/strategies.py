from kgfiller import logger, Commitable, Commit
from kgfiller.kg import KnowledgeGraph, create_query_for_instances, owl_name, human_name
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
            for instance in results:
                kg.add_instance(cls, instance)
            return Commit(
                message=f"add {len(results)} instances to class {human_name(cls)} from AI answer",
                description="Query: " + query.question + ".\n"
                        "Instances being added:\n- " + \
                        "\n- ".join(map(owl_name, results)) + \
                        "\nQuery cache in file: " + \
                        str(query.cache_path.relative_to(kg.path)),
                files=[kg.path, query.cache_path],
            )
        
