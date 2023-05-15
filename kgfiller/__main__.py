from kgfiller import enable_logging
from kgfiller.kg import KnowledgeGraph
from kgfiller.git import DataRepository
from kgfiller.strategies import find_instances_for_class, CLASS_NAME_FANCY


enable_logging()


instance_queries = [
    f"instances list for class {CLASS_NAME_FANCY}",
    f"examples list for {CLASS_NAME_FANCY}",
]


with DataRepository() as repo:
    with KnowledgeGraph() as kg:
        for cls in kg.visit_classes_depth_first():
            commit = find_instances_for_class(kg, cls, instance_queries)
            kg.save()
            repo.maybe_commit(commit)
            # input("Press enter to continue...")
