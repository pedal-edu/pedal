"""
Check utilities.sorting
"""
import unittest
from pedal.utilities.sorting import topological_sort


class TestTopologicalSort(unittest.TestCase):
    def test_topological_sort(self):
        basic = ['Apple', 'Banana', 'Corn', 'Date', 'Eggplant']
        self.assertEqual(topological_sort(basic, {}), basic)

        backwards = basic[::-1]
        self.assertEqual(topological_sort(backwards, {}), backwards)

        force = {'Apple': ['Corn', 'Date'],
                 'Date': ['Corn', 'Eggplant'],
                 'Banana': ['Eggplant']}
        self.assertEqual(topological_sort(basic, force),
                         ['Apple', 'Banana', 'Date', 'Corn', 'Eggplant'])

        self.assertEqual(topological_sort(backwards, force),
                         ['Banana', 'Apple', 'Date', 'Eggplant', 'Corn'])

        force = {'Eggplant': ['Date'],
                 'Date': ['Corn'],
                 'Corn': ['Banana'],
                 'Banana': ['Apple']}
        self.assertEqual(topological_sort(basic, force),
                         backwards)

        self.assertEqual(topological_sort(backwards, force),
                         backwards)

    def test_project_names(self):
        names = ['records', 'render_introduction',
                 'create_world', 'render',
                 'get_options', 'choose', 'update',
                 'render_ending', 'win_and_lose_paths',
                 'conclusion']
        orderings = {'choose': ['win_and_lose_paths'],
                     'create_world': ['render',
                                      'get_options',
                                      'render_ending',
                                      'win_and_lose_paths'],
                     'get_options': ['choose', 'update', 'win_and_lose_paths'],
                     'render': ['win_and_lose_paths'],
                     'render_ending': ['win_and_lose_paths'],
                     'render_introduction': ['win_and_lose_paths'],
                     'update': ['win_and_lose_paths'],
                     'win_and_lose_paths': ['conclusion']}
        expected = ['records',
                    'render_introduction',
                    'create_world',
                    'render',
                    'get_options', 'choose',
                    'update',
                    'render_ending',
                    'win_and_lose_paths',
                    'conclusion']
        self.assertEqual(topological_sort(names, orderings), expected)


if __name__ == '__main__':
    unittest.main(buffer=False)
