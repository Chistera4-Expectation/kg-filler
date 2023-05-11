from kgfiller import enable_logging
from kgfiller.kg import KnowledgeGraph
from kgfiller.git import DataRepository

enable_logging()

with DataRepository() as repo:
    with KnowledgeGraph() as kg:
        for cls in kg.visit_classes_depth_first():
            i = kg.add_instance(cls, f"dummy_{cls.name.lower()}")
            kg.save()
            repo.commit_edits_if_any(f"add dummy instance for class {cls}: {i.name}")
