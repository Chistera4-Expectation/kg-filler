import unittest
from kgfiller.ai import ai_query


class TestPostprocess(unittest.TestCase):

    def test_normal_output(self):
        question = 'ingredient list for Beef Bulgogi, names only'
        query = ai_query(question)
        results = query.result_to_list()
        assert len(results) == 10
        assert results[-1] == 'Sesame seeds'
        assert results[0] == 'Beef sirloin'
        question = 'ingredient list for Brioche bread, names only'
        query = ai_query(question)
        results = query.result_to_list()
        assert len(results) == 7
        assert results[-1] == 'Flour'
        assert results[0] == 'Butter'

    def test_lengthy_elements(self):
        question = 'ingredient list for Green Curry, names only'
        query = ai_query(question)
        results = query.result_to_list()
        assert len(results) == 11
        assert results[-1] == 'Green curry paste'
        assert results[0] == 'Green chili peppers'

    def test_inline_list(self):
        question = 'ingredient list for Pico de Gallo, names only'
        query = ai_query(question)
        results = query.result_to_list()
        assert len(results) == 6
        assert results[-1] == 'tomatoes'
        assert results[0] == 'salt'


    def test_weird_last_element(self):
        question = 'ingredient list for Minestrone Soup, names only'
        query = ai_query(question)
        results = query.result_to_list()
        assert len(results) == 17
        assert results[-1] == 'Olive oil'
        assert results[0] == 'Parmesan cheese'

    def test_or_in_element(self):
        question = 'ingredient list for Whole wheat bread, names only'
        query = ai_query(question)
        results = query.result_to_list()
        assert len(results) == 6
        assert results[-1] == 'Whole wheat flour'
        assert results[0] == 'Olive oil'

    def test_optional_elements(self):
        question = 'ingredient list for Enchiladas, names only'
        query = ai_query(question)
        results = query.result_to_list()
        assert len(results) == 8
        assert results[-1] == 'Tortillas'
        assert results[0] == 'Sour cream'