from kgfiller.ai import ai_query
import kgfiller.ai.openai as openai
from kgfiller import enable_logging


enable_logging()
openai.almmai_endpoint()


while True:
    try:
        question = input("?- ")
        query = ai_query(question)
        print(query.result_text)
        print("> itemized results:", query.result_to_list())
        openai.stats.print()
    except EOFError:
        break
