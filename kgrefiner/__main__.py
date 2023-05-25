import logging
from kgfiller import enable_logging
from kgfiller.git import DataRepository
from kgfiller.kg import KnowledgeGraph
from kgfiller.strategies import INSTANCE_NAME_FANCY, CLASS_LIST_FANCY, CLASS_NAME_FANCY
from kgrefiner import get_conflicting_classes, exclusive_classes_check


enable_logging(logging.INFO)


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
        # Post-processing
        # If an individual appears both under Diary and under Diary-Alternative, remove it from Diary
        conflicting_classes = get_conflicting_classes(kg)
        for cls1, cls2 in conflicting_classes:
            commit = exclusive_classes_check(cls1, cls2)
            kg.save()
            repo.maybe_commit(commit)