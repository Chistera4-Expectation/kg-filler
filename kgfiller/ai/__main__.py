from kgfiller.ai import ai_query, stats

q = ai_query("What is the meaning of life?")
print(q.result_text)
print(stats)
