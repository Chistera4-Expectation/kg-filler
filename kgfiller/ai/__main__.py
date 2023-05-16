from kgfiller.ai import ai_query, stats
from kgfiller import enable_logging

enable_logging()

while True:
    try:
        question = input("?- ")
        query = ai_query(question)
        for result in query.result_to_list():
            print("\t-", result)
        stats.print()
    except EOFError:
        break
