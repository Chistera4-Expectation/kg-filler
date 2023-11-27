import tests
import unittest
from kgfiller.text import itemize


class TestItemize(unittest.TestCase):

    def test_normal_output(self):
        query_result = "1. Flour\n\n2. Yeast\n\n3. Sugar\n\n4. Salt\n\n5. Eggs\n\n6. Milk\n\n7. Butter"
        results = itemize(query_result)
        expected_items = ['Flour', 'Yeast', 'Sugar', 'Salt', 'Eggs', 'Milk', 'Butter']
        for index, result in enumerate(results):
            assert result.value == expected_items[index]
        
        query_result = "1. Beef sirloin\n\n2. Soy sauce\n\n3. Brown sugar\n\n4. Sesame oil\n\n5. Garlic\n\n6. Ginger\n\n7. Green onions\n\n8. Black pepper\n\n9. Rice wine\n\n10. Sesame seeds"
        results = itemize(query_result)
        expected_items = ['Beef sirloin', 'Soy sauce', 'Brown sugar', 'Sesame oil', 'Garlic', 'Ginger', 'Green onions', 'Black pepper', 'Rice wine', 'Sesame seeds']
        for index, result in enumerate(results):
            assert result.value == expected_items[index]

    def test_lengthy_elements(self):
        query_result = "- Green curry paste\n\n- Coconut milk\n\n- Chicken or tofu\n\n- Thai eggplant\n\n- Bamboo shoots\n\n- Green beans\n\n- Kaffir lime leaves\n\n- Thai basil leaves\n\n- Fish sauce\n\n- Palm sugar\n\n- Green chili peppers"
        results = itemize(query_result)
        expected_items = ['Green curry paste', 'Coconut milk', 'Chicken', 'Thai eggplant', 'Bamboo shoots', 'Green beans', 'Kaffir lime leaves', 'Thai basil leaves', 'Fish sauce', 'Palm sugar', 'Green chili peppers']
        for index, result in enumerate(results):
            print(result.value)
            assert result.value == expected_items[index]

    def test_inline_list(self):
        query_result = "tomatoes, onion, jalapeno pepper, cilantro, lime juice, salt."
        results = itemize(query_result)
        expected_items = ['tomatoes', 'onion', 'jalapeno pepper', 'cilantro', 'lime juice', 'salt']
        for index, result in enumerate(results):
            assert result.value == expected_items[index]

    def test_text_before_list(self):
        query_result = "ingredients are:\n\n1. Beef sirloin\n\n2. Soy sauce\n\n3. Brown sugar\n\n4. Sesame oil\n\n5. Garlic\n\n6. Ginger\n\n7. Green onions\n\n8. Black pepper\n\n9. Rice wine\n\n10. Sesame seeds"
        results = itemize(query_result)
        expected_items = ['Beef sirloin', 'Soy sauce', 'Brown sugar', 'Sesame oil', 'Garlic', 'Ginger', 'Green onions', 'Black pepper', 'Rice wine', 'Sesame seeds']
        for index, result in enumerate(results):
            assert result.value == expected_items[index]

        query_result = "possible ingredients can be:\n\n- tomatoes\n\n- onion\n\n- jalapeno pepper\n\n- cilantro\n\n- lime juice\n\n- salt"
        results = itemize(query_result)
        expected_items = ['tomatoes', 'onion', 'jalapeno pepper', 'cilantro', 'lime juice', 'salt']
        for index, result in enumerate(results):
            assert result.value == expected_items[index]

    def test_weird_last_element(self):
        query_result = "- Olive oil\n\n- Onion\n\n- Garlic\n\n- Carrots\n\n- Celery\n\n- Zucchini\n\n- Potatoes\n\n- Tomatoes\n\n- Tomato paste\n\n- Vegetable broth\n\n- Cannellini beans\n\n- Green beans\n\n- Pasta\n\n- Salt\n\n- Pepper\n\n- Basil\n\n- Parmesan cheese (optional)"
        results = itemize(query_result)
        expected_items = ['Olive oil', 'Onion', 'Garlic', 'Carrots', 'Celery', 'Zucchini', 'Potatoes', 'Tomatoes', 'Tomato paste', 'Vegetable broth', 'Cannellini beans', 'Green beans', 'Pasta', 'Salt', 'Pepper', 'Basil', 'Parmesan cheese']
        for index, result in enumerate(results):
            assert result.value == expected_items[index]

        query_result = "- Olive oil\n\n- Onion\n\n- Garlic\n\n- Carrots\n\n- Celery\n\n- Zucchini\n\n- Potatoes\n\n- Tomatoes\n\n- Tomato paste\n\n- Vegetable broth\n\n- Cannellini beans\n\n- Green beans\n\n- Pasta\n\n- Salt\n\n- Pepper\n\n- Basil\n\n- Parmesan cheese : optional"
        results = itemize(query_result)
        expected_items = ['Olive oil', 'Onion', 'Garlic', 'Carrots', 'Celery', 'Zucchini', 'Potatoes', 'Tomatoes', 'Tomato paste', 'Vegetable broth', 'Cannellini beans', 'Green beans', 'Pasta', 'Salt', 'Pepper', 'Basil', 'Parmesan cheese']
        for index, result in enumerate(results):
            assert result.value == expected_items[index]

        query_result = "- Olive oil\n\n- Onion\n\n- Garlic\n\n- Carrots\n\n- Celery\n\n- Zucchini\n\n- Potatoes\n\n- Tomatoes\n\n- Tomato paste\n\n- Vegetable broth\n\n- Cannellini beans\n\n- Green beans\n\n- Pasta\n\n- Salt\n\n- Pepper\n\n- Basil\n\n- Parmesan cheese (optional) : 50gr"
        results = itemize(query_result)
        expected_items = ['Olive oil', 'Onion', 'Garlic', 'Carrots', 'Celery', 'Zucchini', 'Potatoes', 'Tomatoes', 'Tomato paste', 'Vegetable broth', 'Cannellini beans', 'Green beans', 'Pasta', 'Salt', 'Pepper', 'Basil', 'Parmesan cheese']
        for index, result in enumerate(results):
            assert result.value == expected_items[index]

    def test_or_in_element(self):
        query_result = "1. Whole wheat flour\n\n2. Water\n\n3. Yeast\n\n4. Salt\n\n5. Honey or sugar\n\n6. Olive oil or butter"
        results = itemize(query_result)
        expected_items = ['Whole wheat flour', 'Water', 'Yeast', 'Salt', 'Honey', 'Olive oil']
        for index, result in enumerate(results):
            assert result.value == expected_items[index]

    def test_optional_elements(self):
        query_result = "1. Whole wheat flour\n\n2. Water\n\n3. Yeast\n\n4. Salt\n\n5. Honey (optional)\n\n6. Olive oil (optional)"
        results = itemize(query_result)
        expected_items = ['Whole wheat flour', 'Water', 'Yeast', 'Salt', 'Honey', 'Olive oil']
        for index, result in enumerate(results):
            assert result.value == expected_items[index]

        query_result = "- Tortillas\n\n- Enchilada sauce\n\n- Shredded cheese\n\n- Cooked chicken (optional)\n\n- Diced onions (optional)\n\n- Diced tomatoes (optional)\n\n- Sliced black olives (optional)\n\n- Sour cream (optional)"
        results = itemize(query_result)
        expected_items = ['Tortillas', 'Enchilada sauce', 'Shredded cheese', 'Cooked chicken', 'Diced onions', 'Diced tomatoes', 'Sliced black olives', 'Sour cream']
        for index, result in enumerate(results):
            assert result.value == expected_items[index]

    def test_parenthesis(self):
        query_result = "1. Beef (sirloin)\n\n2. Soy sauce\n\n3. Brown sugar (raw)\n\n4. Sesame oil\n\n5. Garlic\n\n6. Ginger\n\n7. Green onions (peeled)\n\n8. Black pepper\n\n9. Rice wine\n\n10. Sesame seeds"
        results = itemize(query_result)
        expected_items = ['Beef', 'Soy sauce', 'Brown sugar', 'Sesame oil', 'Garlic', 'Ginger', 'Green onions', 'Black pepper', 'Rice wine', 'Sesame seeds']
        for index, result in enumerate(results):
            assert result.value == expected_items[index]

    def test_unclosed_parenthesis(self):
        query_result = "1. Beef (usually thinly sliced ribeye\n\n2. Soy sauce\n\n3. Brown sugar (raw\n\n4. Sesame oil\n\n5. Garlic\n\n6. Ginger\n\n7. Green onions\n\n8. Black pepper\n\n9. Rice wine\n\n10. Sesame seeds"
        results = itemize(query_result)
        expected_items = ['Beef', 'Soy sauce', 'Brown sugar', 'Sesame oil', 'Garlic', 'Ginger', 'Green onions', 'Black pepper', 'Rice wine', 'Sesame seeds']
        for index, result in enumerate(results):
            assert result.value == expected_items[index]

        query_result = "1. Soy sauce\n\n2. Brown sugar (raw\n\n3. Sesame oil\n\n4. Garlic\n\n5. Ginger\n\n6. Green onions\n\n7. Black pepper\n\n8. Rice wine\n\n9. Sesame seeds\n\n10. beef (sirloin"
        results = itemize(query_result)
        expected_items = ['Soy sauce', 'Brown sugar', 'Sesame oil', 'Garlic', 'Ginger', 'Green onions', 'Black pepper', 'Rice wine', 'Sesame seeds', 'beef']
        for index, result in enumerate(results):
            assert result.value == expected_items[index]
