import unittest
from kgfiller.ai import ai_query


class TestPostprocess(unittest.TestCase):

    def test_normal_output(self):
        question = 'ingredient list for Beef Bulgogi, names only'
        query = ai_query(question)
        results = query.result_to_list()
        for index, result in enumerate(results):
            results[index] = str(result).lower()
        print('Question is "{}"'.format(question))
        print('Results:')
        for item in results:
            print('\t{}'.format(item))
        assert ('beef' in results) or ('beef sirloin' in results)
        question = 'ingredient list for Brioche bread, names only'
        query = ai_query(question)
        results = query.result_to_list()
        for index, result in enumerate(results):
            results[index] = str(result).lower()
        print('Question is "{}"'.format(question))
        print('Results:')
        for item in results:
            print('\t{}'.format(item))
        assert ('flour' in results)

    def test_lengthy_elements(self):
        question = 'ingredient list for Green Curry, names only'
        query = ai_query(question)
        results = query.result_to_list()
        for index, result in enumerate(results):
            results[index] = str(result).lower()
        print('Question is "{}"'.format(question))
        print('Results:')
        for item in results:
            print('\t{}'.format(item))
        assert ('green curry paste' in results) and ('green chili peppers' in results)

    def test_inline_list(self):
        question = 'ingredient list for Pico de Gallo, names only'
        query = ai_query(question)
        results = query.result_to_list()
        for index, result in enumerate(results):
            results[index] = str(result).lower()
        print('Question is "{}"'.format(question))
        print('Results:')
        for item in results:
            print('\t{}'.format(item))
        assert ('tomatoes' in results) and ('salt' in results)


    def test_weird_last_element(self):
        question = 'ingredient list for Minestrone Soup, names only'
        query = ai_query(question)
        results = query.result_to_list()
        for index, result in enumerate(results):
            results[index] = str(result).lower()
        print('Question is "{}"'.format(question))
        print('Results:')
        for item in results:
            print('\t{}'.format(item))
        assert 'olive oil' in results
        for result in results:
            assert '(optional)' not in result

    def test_or_in_element(self):
        question = 'ingredient list for Whole wheat bread, names only'
        query = ai_query(question)
        results = query.result_to_list()
        for index, result in enumerate(results):
            results[index] = str(result).lower()
        print('Question is "{}"'.format(question))
        print('Results:')
        for item in results:
            print('\t{}'.format(item))
        for result in results:
            assert '(or)' not in result

    def test_optional_elements(self):
        question = 'ingredient list for Enchiladas, names only'
        query = ai_query(question)
        results = query.result_to_list()
        for index, result in enumerate(results):
            results[index] = str(result).lower()
        print('Question is "{}"'.format(question))
        print('Results:')
        for item in results:
            print('\t{}'.format(item))
        for result in results:
            assert '(optional)' not in result