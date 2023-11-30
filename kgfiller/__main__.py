from kgfiller import enable_logging
from kgfiller.git import DataRepository
from kgfiller.kg import subtype
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


rebalance_queries = [
    f"most adequate class for '{INSTANCE_NAME_FANCY}' among: {CLASS_LIST_FANCY}. concise",
]


with DataRepository() as repo:
    with KnowledgeGraph() as kg:
        Recipe = kg.onto.Recipe
        for cls in kg.visit_classes_depth_first():
            commit = find_instances_for_class(kg, cls, instance_queries)
            kg.save()
            repo.maybe_commit(commit)
        for instance in kg.onto.Recipe.instances():
            commit = find_related_instances(kg, instance, kg.onto.ingredientOf, kg.onto.Edible, recipe_queries, instance_as_object=True)
            kg.save()
            repo.maybe_commit(commit)
        already_met_instances = set()
        for cls in kg.visit_classes_depth_first():
            if not is_leaf(cls) and not subtype(cls, Recipe):
                for instance in cls.instances():
                    if instance not in already_met_instances:
                        already_met_instances.add(instance)
                        commit = move_to_most_adequate_subclass(kg, instance, cls, leaf_descendants, rebalance_queries)
                        if not commit.should_commit:
                            commit.should_commit = True
                            kg.save()
                            repo.maybe_commit(commit)
                            commit = move_to_most_adequate_subclass(kg, instance, cls, all_descendants, rebalance_queries)
                        commit.should_commit = True
                        kg.save()
                        repo.maybe_commit(commit)
