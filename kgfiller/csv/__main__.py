from kgfiller.csv import *


ingredients = set()


for entry in load_dataset(["Ingredients"]):
    for ingredient in entry["Ingredients"]:
        ingredients.add(ingredient.value)


ingredients = list(ingredients)
ingredients.sort()

for i in ingredients:
    print(i)
