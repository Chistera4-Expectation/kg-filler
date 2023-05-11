from kgfiller import enable_logging
from kgfiller.kg import KnowledgeGraph, create_query_for_instances, owl_name
from kgfiller.ai import ai_query
# from kgfiller.git import DataRepository

enable_logging()

# with DataRepository() as repo:
with KnowledgeGraph() as kg:
    for cls in kg.visit_classes_depth_first():
        query = ai_query(create_query_for_instances(cls))
        print(f"?- {query.question}.")
        for instance in query.result_to_list():
            print(f"\t- {owl_name(instance)} (fancy name: {instance})")
        input("Press enter to continue...")