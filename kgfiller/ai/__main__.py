
from kgfiller.ai import ai_query, load_api_from_env
from kgfiller import enable_logging


enable_logging()
api = load_api_from_env()


while True:
    try:
        question = input("?- ")
        query = ai_query(question)
        print(query.result_text)
        print("> itemized results:", query.result_to_list())
        api.stats.print()
    except EOFError:
        break
    except KeyboardInterrupt:
        break
