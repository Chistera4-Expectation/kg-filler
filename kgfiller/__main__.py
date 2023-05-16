from kgfiller import enable_logging
from kgfiller.kg import KnowledgeGraph
from kgfiller.git import DataRepository
from kgfiller.strategies import *


enable_logging()


instance_queries = [
    f"instances list for class {CLASS_NAME_FANCY}, names only",
    f"instances list for class {CLASS_NAME_FANCY}",
    f"examples list for {CLASS_NAME_FANCY}, names only",
    f"examples list for {CLASS_NAME_FANCY}",
]


recipe_queries = [
    f"ingredient list for {INSTANCE_NAME_FANCY}, names only",
]


with DataRepository() as repo:
    with KnowledgeGraph() as kg:
        for cls in kg.visit_classes_depth_first():
            commit = find_instances_for_class(kg, cls, instance_queries)
            kg.save()
            repo.maybe_commit(commit)
        #     # input("Press enter to continue...")
        # for instance in kg.onto.Recipe.instances():
        #     commit = find_related_instances(kg, instance, kg.onto.ingredientOf, kg.onto.Edible, recipe_queries)
        #     kg.save()
        #     repo.maybe_commit(commit)
        #     # input("Press enter to continue...")
