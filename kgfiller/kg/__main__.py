from kgfiller import enable_logging
from kgfiller.kg import KnowledgeGraph


enable_logging()


with KnowledgeGraph() as kg:
    for cls in kg.visit_classes_depth_first():
        kg.add_instance(cls, f"dummy_{cls.name.lower()}")
