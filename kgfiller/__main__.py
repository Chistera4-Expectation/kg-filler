from kgfiller import enable_logging, logger, PATH_DATA_DIR
from kgfiller.kg import KnowledgeGraph, create_query_for_instances, owl_name, human_name, PATH_ONTOLOGY
from kgfiller.ai import ai_query
from kgfiller.git import DataRepository

enable_logging()


def commit(repo, query, cls):
    instances = list(query.result_to_list())
    message = f"add {len(instances)} instances to class {human_name(cls)} from AI answer"
    description = "Instances being added:\n- " + "\n- ".join(map(owl_name, instances))
    description += "\nQuery cache in file: " + str(query.cache_path.relative_to(PATH_DATA_DIR))
    repo.commit_edits_if_any(message, PATH_ONTOLOGY, description, query.cache_path)


with DataRepository() as repo:
    with KnowledgeGraph() as kg:
        for cls in kg.visit_classes_depth_first():
            query = ai_query(create_query_for_instances(cls))
            print(f"?- {query.question}.")
            results = list(query.result_to_list())
            if len(results) == 0:
                logger.warning("No results for query '%s', AI answer: %s", query.question, query.result_text)
            else:
                for instance in results:
                    kg.add_instance(cls, instance)
                commit(repo, query, cls)
            input("Press enter to continue...")
