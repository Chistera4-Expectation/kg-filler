from kgfiller import enable_logging, logger
from kgfiller.git import DataRepository
from kgfiller.kg import subtype
from kgfiller.strategies import *
from kgfiller.text import gather_possible_duplicates
from kgfiller.utils import load_queries_json


enable_logging()

queries = load_queries_json()
instance_queries = queries['instance']
recipe_queries = queries['recipe']
relation_queries = queries['relation']
rebalance_queries = queries['rebalance']
duplicates_queries = queries['duplicate']


with DataRepository() as repo:
    with KnowledgeGraph() as kg:
        Recipe = kg.onto.Recipe
        for cls in kg.visit_classes_depth_first():
            if not subtype(cls, Recipe):
                commit = find_instances_for_class(kg, cls, instance_queries)
                kg.save()
                repo.maybe_commit(commit)
        commit = find_instances_for_recipes(kg, Recipe, recipe_queries)
        kg.save()
        repo.maybe_commit(commit)
        for instance in kg.onto.Recipe.instances():
            commit = find_related_instances(kg, instance, kg.onto.ingredientOf, kg.onto.Edible, relation_queries, instance_as_object=True)
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
        for cls in kg.visit_classes_depth_first():
            if not subtype(cls, Recipe):
                possible_duplicates = gather_possible_duplicates(cls)
                logger.debug('Possible duplicates in class "{}" are: {}'.format(cls, possible_duplicates))
                for possible_duplicates_couple in possible_duplicates:
                    logger.debug('Checking couple {}'.format(possible_duplicates_couple))
                    commit = check_duplicates(kg, cls, possible_duplicates_couple, duplicates_queries)
                    kg.save()
                    repo.maybe_commit(commit)
