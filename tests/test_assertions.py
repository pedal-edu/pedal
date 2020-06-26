import unittest
import os
import sys
from textwrap import dedent

from pedal import suppress

pedal_library = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, pedal_library)

from pedal.core import *
from pedal.source import set_source
from pedal.assertions import *
from tests.execution_helper import Execution, ExecutionTestCase
from pedal.assertions.setup import _topological_sort, set_assertion_mode


class TestAssertions(ExecutionTestCase):

    def test_exceptional_mode(self):
        with Execution('a = 0') as e:
            set_assertion_mode(exceptions=True)
            self.assertRaises(AssertionException, assertEqual, 1, 3)

    def test_primitive_assertions(self):
        with Execution(dedent("0")) as e:
            @phase('1')
            def part1():
                assertEqual(5, 0)
        self.assertFeedback(e, """
        Instructor Test
        Student code failed instructor test.
        5 != 0""")
    
    def test_sandbox_assertions(self):
        with Execution(dedent('''
            def add(a, b, c):
                return a + b - c
        ''')) as e:
            @phase('1')
            def part1():
                """

                """
                assertEqual(e.student.call('add', 1, 6, 3), 10)
            suppress("analyzer")
        self.assertEqual(e.feedback, dedent("""
        Instructor Test
        Student code failed instructor test.
        I ran:
        <pre>add(1, 6, 3)</pre>
        The result was:
        <pre>4</pre>
        But I expected the result to be equal to:
        <pre>10</pre>""").lstrip())
        
        with Execution(dedent('''
            def add(a, b, c):
                return a + b - c
        ''')) as e:
            @phase('1')
            def part2():
                """

                """
                assertEqual(10, e.student.call('add', 1, 6, 3))
            suppress("analyzer")
        self.assertEqual(e.feedback, dedent("""
        Instructor Test\nStudent code failed instructor test.<br>
        I ran:
        <pre>add(1, 6, 3)</pre>
        The result was:
        <pre>4</pre>
        But I expected the result to be equal to:
        <pre>10</pre>""").lstrip())
        
        with Execution(dedent('''
            def add(a, b, c):
                if a < 0:
                    return -1
                return a + b + c
        ''')) as e:
            @phase('1')
            def part2():
                """

                """
                assertEqual(10, e.student.call('add', 1, 6, 3))
                assertEqual(8, e.student.call('add', -1, 6, 3))
            suppress("analyzer")
        self.assertEqual(e.feedback, dedent("""
        Instructor Test\nStudent code failed instructor test.<br>
        I ran:
        <pre>add(-1, 6, 3)</pre>
        The result was:
        <pre>-1</pre>
        But I expected the result to be equal to:
        <pre>8</pre>""").lstrip())
        
        with Execution(dedent('''
            def add(a, b, c):
                return a + b - c
            def expected_answer():
                return 10
        ''')) as e:
            @phase('1')
            def part3():
                """

                """
                assertEqual(e.student.call('expected_answer', target='expect'),
                            e.student.call('add', 1, 6, 3, target='actual'))
            suppress("analyzer")
        self.assertEqual(e.feedback, dedent("""
        Instructor Test\nStudent code failed instructor test.<br>
        I ran:
        <pre>expect = expected_answer()
        actual = add(1, 6, 3)</pre>
        The value of <code>expect</code> was:
        <pre>10</pre>
        The value of <code>actual</code> was:
        <pre>4</pre>
        But I expected <code>expect</code> to be equal to <code>actual</code>""").lstrip())
        
        with Execution(dedent('''
            def make_color():
                return "purple"
        ''')) as e:
            @phase('1')
            def part4():
                """

                """
                assertIn(e.student.call('make_color'), ('red', 'blue', 'green'))
            suppress("analyzer")
        self.assertEqual(e.feedback, dedent("""
        Instructor Test\nStudent code failed instructor test.<br>
        I ran:
        <pre>make_color()</pre>
        The result was:
        <pre>'purple'</pre>
        But I expected the result to be in:
        <pre>('red', 'blue', 'green')</pre>""").lstrip())
        
        with Execution(dedent('''
            def make_colors():
                return ["purple", "orange", "muave"]
        ''')) as e:
            @phase('1')
            def part1():
                """

                """
                assertIn('blue', e.student.call('make_colors'))
            suppress("analyzer")
        self.assertEqual(e.feedback, dedent("""
        Instructor Test\nStudent code failed instructor test.<br>
        I ran:
        <pre>make_colors()</pre>
        The result was:
        <pre>['purple', 'orange', 'muave']</pre>
        But I expected the result to contain:
        <pre>'blue'</pre>""").lstrip())
        
        with Execution(dedent('''
            def make_colors():
                return ["purple", "orange", "muave"]
        ''')) as e:
            @phase('1')
            def part1():
                """

                """
                assertNotIn('purple', e.student.call('make_colors'))
            suppress("analyzer")
        self.assertEqual(e.feedback, dedent("""
        Instructor Test\nStudent code failed instructor test.<br>
        I ran:
        <pre>make_colors()</pre>
        The result was:
        <pre>['purple', 'orange', 'muave']</pre>
        But I expected the result to not contain:
        <pre>'purple'</pre>""").lstrip())
        
        with Execution(dedent('''
            def make_colors():
                return ["purple", "orange", "muave"]
            def make_color():
                return 'blue'
        ''')) as e:
            @phase('1')
            def part1():
                """

                """
                assertIn(e.student.call('make_color', target="color"),
                         e.student.call('make_colors', target="colors"))
            suppress("analyzer")
        self.assertEqual(e.feedback, dedent("""
        Instructor Test\nStudent code failed instructor test.<br>
        I ran:
        <pre>color = make_color()
        colors = make_colors()</pre>
        The value of <code>color</code> was:
        <pre>'blue'</pre>
        The value of <code>colors</code> was:
        <pre>['purple', 'orange', 'muave']</pre>
        But I expected <code>color</code> to be in <code>colors</code>""").lstrip())
        
        with Execution(dedent('''
            def make_colors():
                return ["purple", "orange", "muave"]
            def make_color():
                return 'blue'
        ''')) as e:
            @phase('1')
            def part1():
                """

                """
                assertIn(e.student.call('make_color'),
                         e.student.call('make_colors'))
            suppress("analyzer")
        self.assertEqual(e.feedback, dedent("""
        Instructor Test\nStudent code failed instructor test.<br>
        I ran:
        <pre>make_color()
        make_colors()</pre>
        The first result was:
        <pre>'blue'</pre>
        The second result was:
        <pre>['purple', 'orange', 'muave']</pre>
        But I expected the first result to be in the second result""").lstrip())
        
        with Execution(dedent('''
            def make_color():
                return 0
        ''')) as e:
            @phase('1')
            def part1():
                """

                """
                assertTrue(e.student.call('make_color'))
            suppress("analyzer")
        self.assertEqual(e.feedback, dedent("""
        Instructor Test\nStudent code failed instructor test.<br>
        I ran:
        <pre>make_color()</pre>
        The result was false:
        <pre>0</pre>
        But I expected the result to be true""").lstrip())
        
        with Execution(dedent('''
            def add_from_input(val2):
                val1 = input("Give me a number:")
                return int(val1) - val2
            add_from_input
        ''')) as e:
            @phase('1')
            def part1():
                """

                """
                assertEqual(e.student.call('add_from_input', 4, inputs="6"), 10)
            suppress("analyzer")
        self.assertEqual(e.feedback, dedent("""
        Instructor Test\nStudent code failed instructor test.<br>
        I ran:
        <pre>add_from_input(4)</pre>
        I entered as input:
        <pre>6</pre>
        The result was:
        <pre>2</pre>
        But I expected the result to be equal to:
        <pre>10</pre>""").lstrip())
        
        with Execution(dedent('''
            def make_brackets():
                return "{}"
        ''')) as e:
            @phase('1')
            def part1():
                """

                """
                assertEqual(e.student.call('make_brackets'), "[]",
                            exact=True)
            suppress("analyzer")
        self.assertEqual(e.feedback, dedent("""
        Instructor Test\nStudent code failed instructor test.<br>
        I ran:
        <pre>make_brackets()</pre>
        The result was:
        <pre>'{}'</pre>
        But I expected the result to be equal to:
        <pre>'[]'</pre>""").lstrip())
        
        with Execution(dedent('''
            def fail_on_3(num):
                if num == 3:
                    return False
                else:
                    return True
        ''')) as e:
            @phase('1')
            def part1():
                """

                """
                assertEqual(e.student.call('fail_on_3', 1, keep_context=True), True)
                assertEqual(e.student.call('fail_on_3', 2, keep_context=True), True)
                assertEqual(e.student.call('fail_on_3', 3, keep_context=True), True)
            suppress("analyzer")
        self.assertEqual(e.feedback, dedent("""
        Instructor Test
        Student code failed instructor test.
        I ran:
        <pre>fail_on_3(1)
        fail_on_3(2)
        fail_on_3(3)</pre>
        The result was:
        <pre>False</pre>
        But I expected the result to be equal to:
        <pre>True</pre>""").lstrip())
        
        # Test {} in output or context

    def test_print_assertions(self):
        with Execution(dedent('''
            def print_rating(r):
                print("""
            banana cream pudding
            alphabet soup
            raktajino""")
        ''')) as e:
            @phase('1')
            def part1():
                """

                """
                assertPrints(e.student.call("print_rating", 9),
                             ["banana cream pudding", "alphabet soup", "raktajino"])

            suppress("analyzer")
        self.assertFeedback(e, """
        Instructor Test
        Student code failed instructor test.
        I ran:
        <pre>print_rating(9)</pre>
        The function printed:
        <pre>
        banana cream pudding
        alphabet soup
        raktajino</pre>
        But I expected the output:
        <pre>banana cream pudding
        alphabet soup
        raktajino</pre>""")
        
class TestTopologicalSort(unittest.TestCase):
    def test_topological_sort(self):
        basic = ['Apple', 'Banana', 'Corn', 'Date', 'Eggplant']
        self.assertEqual(_topological_sort(basic, {}), basic)
        
        backwards = basic[::-1]
        self.assertEqual(_topological_sort(backwards, {}), backwards)
        
        force = {'Apple': ['Corn', 'Date'],
                 'Date': ['Corn', 'Eggplant'],
                 'Banana': ['Eggplant']}
        self.assertEqual(_topological_sort(basic, force),
                         ['Apple', 'Banana', 'Date', 'Corn', 'Eggplant'])
        
        self.assertEqual(_topological_sort(backwards, force),
                         ['Banana', 'Apple', 'Date', 'Eggplant', 'Corn'])

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
        expected = ['records',
                    'render_introduction',
                    'create_world', 
                    'render',
                    'get_options', 'choose', 
                    'update',
                    'render_ending',
                    'win_and_lose_paths',
                    'conclusion']
        self.assertEqual(_topological_sort(names, orderings), expected)

if __name__ == '__main__':
    unittest.main(buffer=False)
