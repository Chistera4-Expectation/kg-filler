from kgfiller import logger
from kgfiller.git import DataRepository
from kgfiller.kg import subtype
from kgfiller.strategies import *
from kgfiller.text import gather_possible_duplicates, gather_all_instances_of_class_without_subclasses
from kgfiller.utils import load_queries_yaml


queries = load_queries_yaml()
instance_queries = queries['instance']
recipe_queries = queries['recipe']
relation_queries = queries['relation']
rebalance_queries = queries['rebalance']
duplicates_queries = queries['duplicate']


with DataRepository() as repo:
    with KnowledgeGraph() as kg:
        Recipe = kg.onto.Recipe
        logger.debug('Step 1. Finding food instances...')
        for cls in kg.visit_classes_depth_first():
            if not subtype(cls, Recipe):
                logger.debug('Step 1. Checking class "{}"...'.format(cls))
                commit = find_instances_for_class(kg, cls, instance_queries)
                kg.save()
                repo.maybe_commit(commit)
        logger.debug('Step 2. Finding recipe instances...')
        for cls in kg.visit_classes_depth_first():
            if subtype(cls, Recipe, strict=True):
                logger.debug('Step 2. Finding recipe instances for class "{}"...'.format(cls))
                commit = find_instances_for_recipes(kg, cls, recipe_queries)
                kg.save()
                repo.maybe_commit(commit)
        logger.debug('Step 3. Finding relation instances...')
        for instance in kg.onto.Recipe.instances():
            logger.debug('Step 3. Checking instance "{}"...'.format(instance))
            commit = find_related_instances(kg, instance, kg.onto.ingredientOf, kg.onto.Edible, relation_queries, instance_as_object=True)
            kg.save()
            repo.maybe_commit(commit)
        logger.debug('Step 4. Refining position of food instances...')
        already_met_instances = set()
        for cls in kg.visit_classes_depth_first():
            if not is_leaf(cls):
                classes_to_avoid = [Recipe] if not subtype(cls, Recipe) else None
                for instance in gather_all_instances_of_class_without_subclasses(cls):
                    if instance not in already_met_instances:
                        logger.debug('Step 4. Checking instance "{}" in class "{}"...'.format(instance, cls))
                        already_met_instances.add(instance)
                        commit = move_to_most_adequate_subclass(kg, instance, cls, leaf_descendants, rebalance_queries, classes_to_avoid=classes_to_avoid)
                        if not commit.should_commit:
                            commit.should_commit = True
                            kg.save()
                            repo.maybe_commit(commit)
                            commit = move_to_most_adequate_subclass(kg, instance, cls, all_descendants, rebalance_queries, classes_to_avoid=classes_to_avoid)
                        commit.should_commit = True
                        kg.save()
                        repo.maybe_commit(commit)
        logger.debug('Step 5. Checking duplicate food instances...')
        for cls in kg.visit_classes_depth_first():
            if not subtype(cls, Recipe):
                possible_duplicates = gather_possible_duplicates(cls)
                # logger.debug('Step 5. Possible duplicates in class "{}" are: {}'.format(cls, possible_duplicates))
                for possible_duplicates_couple in possible_duplicates:
                    logger.debug('Step 5. Checking couple "{}" in class "{}"...'.format(possible_duplicates_couple, cls))
                    commit = check_duplicates(kg, cls, possible_duplicates_couple, duplicates_queries)
                    kg.save()
                    repo.maybe_commit(commit)
