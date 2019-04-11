import unittest
import os
import sys
from textwrap import dedent

pedal_library = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, pedal_library)

from pedal.report import *
from pedal.source import set_source
from pedal.assertions import *
from tests.execution_helper import Execution
from pedal.assertions.setup import _topological_sort


class TestAssertions(unittest.TestCase):

    def test_exceptional_mode(self):
        with Execution('a = 0') as e:
            set_assertion_mode(exceptions=True)
            self.assertRaises(AssertionException, assertEqual, 1, 3)
        
    def test_primitive_assertions(self):
        with Execution(dedent("0")) as e:
            @section(1)
            def part1():
                assertEqual(5, 0)
        self.assertEqual(e.feedback, dedent("""
        Instructor Test<br>Student code failed instructor test.<br>
        5 != 0""").lstrip())
    
    def test_sandbox_assertions(self):
        with Execution(dedent('''
            def add(a, b, c):
                return a + b - c
        ''')) as e:
            @section(1)
            def part1():
                assertEqual(e.student.call('add', 1, 6, 3), 10)
            suppress("analyzer")
        self.assertEqual(e.feedback, dedent("""
        Instructor Test<br>Student code failed instructor test.<br>
        I ran:<pre>add(1, 6, 3)</pre>
        The result was:<pre>4</pre>
        But I expected the result to be equal to:<pre>10</pre>""").lstrip())
        
        with Execution(dedent('''
            def add(a, b, c):
                return a + b - c
        ''')) as e:
            @section(1)
            def part2():
                assertEqual(10, e.student.call('add', 1, 6, 3))
            suppress("analyzer")
        self.assertEqual(e.feedback, dedent("""
        Instructor Test<br>Student code failed instructor test.<br>
        I ran:<pre>add(1, 6, 3)</pre>
        The result was:<pre>4</pre>
        But I expected the result to be equal to:<pre>10</pre>""").lstrip())
        
        with Execution(dedent('''
            def add(a, b, c):
                if a < 0:
                    return -1
                return a + b + c
        ''')) as e:
            @section(1)
            def part2():
                assertEqual(10, e.student.call('add', 1, 6, 3))
                assertEqual(8, e.student.call('add', -1, 6, 3))
            suppress("analyzer")
        self.assertEqual(e.feedback, dedent("""
        Instructor Test<br>Student code failed instructor test.<br>
        I ran:<pre>add(-1, 6, 3)</pre>
        The result was:<pre>-1</pre>
        But I expected the result to be equal to:<pre>8</pre>""").lstrip())
        
        with Execution(dedent('''
            def add(a, b, c):
                return a + b - c
            def expected_answer():
                return 10
        ''')) as e:
            @section(1)
            def part3():
                assertEqual(e.student.call('expected_answer', target='expect'),
                            e.student.call('add', 1, 6, 3, target='actual'))
            suppress("analyzer")
        self.assertEqual(e.feedback, dedent("""
        Instructor Test<br>Student code failed instructor test.<br>
        I ran:<pre>expect = expected_answer()
        actual = add(1, 6, 3)</pre>
        The value of <code>expect</code> was:<pre>10</pre>
        The value of <code>actual</code> was:<pre>4</pre>
        But I expected <code>expect</code> to be equal to <code>actual</code>""").lstrip())
        
        with Execution(dedent('''
            def make_color():
                return "purple"
        ''')) as e:
            @section(1)
            def part4():
                assertIn(e.student.call('make_color'), ('red', 'blue', 'green'))
            suppress("analyzer")
        self.assertEqual(e.feedback, dedent("""
        Instructor Test<br>Student code failed instructor test.<br>
        I ran:<pre>make_color()</pre>
        The result was:<pre>'purple'</pre>
        But I expected the result to be in:<pre>('red', 'blue', 'green')</pre>""").lstrip())
        
        with Execution(dedent('''
            def make_colors():
                return ["purple", "orange", "muave"]
        ''')) as e:
            @section(1)
            def part1():
                assertIn('blue', e.student.call('make_colors'))
            suppress("analyzer")
        self.assertEqual(e.feedback, dedent("""
        Instructor Test<br>Student code failed instructor test.<br>
        I ran:<pre>make_colors()</pre>
        The result was:<pre>['purple', 'orange', 'muave']</pre>
        But I expected the result to contain:<pre>'blue'</pre>""").lstrip())
        
        with Execution(dedent('''
            def make_colors():
                return ["purple", "orange", "muave"]
        ''')) as e:
            @section(1)
            def part1():
                assertNotIn('purple', e.student.call('make_colors'))
            suppress("analyzer")
        self.assertEqual(e.feedback, dedent("""
        Instructor Test<br>Student code failed instructor test.<br>
        I ran:<pre>make_colors()</pre>
        The result was:<pre>['purple', 'orange', 'muave']</pre>
        But I expected the result to not contain:<pre>'purple'</pre>""").lstrip())
        
        with Execution(dedent('''
            def make_colors():
                return ["purple", "orange", "muave"]
            def make_color():
                return 'blue'
        ''')) as e:
            @section(1)
            def part1():
                assertIn(e.student.call('make_color', target="color"),
                         e.student.call('make_colors', target="colors"))
            suppress("analyzer")
        self.assertEqual(e.feedback, dedent("""
        Instructor Test<br>Student code failed instructor test.<br>
        I ran:<pre>color = make_color()
        colors = make_colors()</pre>
        The value of <code>color</code> was:<pre>'blue'</pre>
        The value of <code>colors</code> was:<pre>['purple', 'orange', 'muave']</pre>
        But I expected <code>color</code> to be in <code>colors</code>""").lstrip())
        
        with Execution(dedent('''
            def make_colors():
                return ["purple", "orange", "muave"]
            def make_color():
                return 'blue'
        ''')) as e:
            @section(1)
            def part1():
                assertIn(e.student.call('make_color'),
                         e.student.call('make_colors'))
            suppress("analyzer")
        self.assertEqual(e.feedback, dedent("""
        Instructor Test<br>Student code failed instructor test.<br>
        I ran:<pre>make_color()
        make_colors()</pre>
        The first result was:<pre>'blue'</pre>
        The second result was:<pre>['purple', 'orange', 'muave']</pre>
        But I expected the first result to be in the second result""").lstrip())
        
        with Execution(dedent('''
            def make_color():
                return 0
        ''')) as e:
            @section(1)
            def part1():
                assertTrue(e.student.call('make_color'))
            suppress("analyzer")
        self.assertEqual(e.feedback, dedent("""
        Instructor Test<br>Student code failed instructor test.<br>
        I ran:<pre>make_color()</pre>
        The result was false:<pre>0</pre>
        But I expected the result to be true""").lstrip())
        
        with Execution(dedent('''
            def add_from_input(val2):
                val1 = input("Give me a number:")
                return int(val1) - val2
            add_from_input
        ''')) as e:
            @section(1)
            def part1():
                assertEqual(e.student.call('add_from_input', 4, inputs="6"), 10)
            suppress("analyzer")
        self.assertEqual(e.feedback, dedent("""
        Instructor Test<br>Student code failed instructor test.<br>
        I ran:<pre>add_from_input(4)</pre>
        I entered as input:<pre>6</pre>
        The result was:<pre>2</pre>
        But I expected the result to be equal to:<pre>10</pre>""").lstrip())
        
        with Execution(dedent('''
            def make_brackets():
                return "{}"
        ''')) as e:
            @section(1)
            def part1():
                assertEqual(e.student.call('make_brackets'), "[]",
                            exact=True)
            suppress("analyzer")
        self.assertEqual(e.feedback, dedent("""
        Instructor Test<br>Student code failed instructor test.<br>
        I ran:<pre>make_brackets()</pre>
        The result was:<pre>'{}'</pre>
        But I expected the result to be equal to:<pre>'[]'</pre>""").lstrip())
        
        
        
        # Test {} in output or context
        
class TestTopologicalSort(unittest.TestCase):
    def test_topological_sort(self):
        basic = ['Apple', 'Banana', 'Corn', 'Date', 'Eggplant']
        self.assertEqual(_topological_sort(basic, {}), basic)
        
        backwards = basic[::-1]
        self.assertEqual(_topological_sort(backwards, {}), basic)
        
        force = {'Apple': ['Corn', 'Date'],
                 'Date': ['Corn', 'Eggplant'],
                 'Banana': ['Eggplant']}
        self.assertEqual(_topological_sort(basic, force),
                         ['Apple', 'Banana', 'Date', 'Corn', 'Eggplant'])
        
        self.assertEqual(_topological_sort(backwards, force),
                         ['Apple', 'Banana', 'Date', 'Corn', 'Eggplant'])

        force = {'Eggplant': ['Date'],
                 'Date': ['Corn'],
                 'Corn': ['Banana'],
                 'Banana': ['Apple']}
        self.assertEqual(_topological_sort(basic, force),
                         backwards)
        
        self.assertEqual(_topological_sort(backwards, force),
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
        expected = ['create_world', 
                    'get_options', 'choose', 
                    'records', 'render',
                    'render_ending', 'render_introduction',
                    'update',
                    'win_and_lose_paths',
                    'conclusion']
        self.assertEqual(_topological_sort(names, orderings), expected)

if __name__ == '__main__':
    unittest.main(buffer=False)
