from kgfiller import enable_logging, logger, PATH_DATA_DIR
from kgfiller.kg import KnowledgeGraph, create_query_for_instances, owl_name, human_name, PATH_ONTOLOGY
from kgfiller.ai import ai_query
from kgfiller.git import DataRepository
from kgfiller.strategies import find_instances_for_class


enable_logging()


with DataRepository() as repo:
    with KnowledgeGraph() as kg:
        for cls in kg.visit_classes_depth_first():
            commit = find_instances_for_class(kg, cls)
            kg.save()
            repo.maybe_commit(commit)
            # input("Press enter to continue...")
