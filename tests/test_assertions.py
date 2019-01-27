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
        self.assertEqual(e.feedback, dedent("""
        Instructor Test<br>Student code failed instructor test.<br>
        I ran:<br>
        <pre>add(1, 6, 3)</pre>
        The result was equal to:
        <pre>4</pre>
        But I expected the result to be equal to:
        <pre>10</pre>""").lstrip())
        
    def test_sandbox_assertions_flipped(self):
        with Execution(dedent('''
            def add(a, b, c):
                return a + b - c
        ''')) as e:
            @section(1)
            def part1():
                assertEqual(10, e.student.call('add', 1, 6, 3))
        self.assertEqual(e.feedback, dedent("""
        Instructor Test<br>Student code failed instructor test.<br>
        I ran:<br>
        <pre>add(1, 6, 3)</pre>
        The result was equal to:
        <pre>4</pre>
        But I expected the result to be equal to:
        <pre>10</pre>""").lstrip())
        
        # Test {} in output or context

if __name__ == '__main__':
    unittest.main(buffer=False)
