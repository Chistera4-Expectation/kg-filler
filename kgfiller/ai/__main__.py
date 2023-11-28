from kgfiller.ai import ai_query
import kgfiller.ai.hugging as hugging
from kgfiller import enable_logging


enable_logging()
# openai.almmai_endpoint()


while True:
    try:
        question = input("?- ")
        query = ai_query(question)
        print(query.result_text)
        print("> itemized results:", query.result_to_list())
        hugging.stats.print()
    except EOFError:
        break
