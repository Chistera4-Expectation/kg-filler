from kgfiller import enable_logging
from kgfiller.kg import KnowledgeGraph, create_query_for_instances
from kgfiller.ai import ai_query
# from kgfiller.git import DataRepository

enable_logging()

# with DataRepository() as repo:
with KnowledgeGraph() as kg:
    for cls in kg.visit_classes_depth_first():
        query_string = create_query_for_instances(cls)
        query = ai_query(query_string)
        print("   ", query.result_text, end="\n    ")
