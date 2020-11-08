import unittest
import os
import sys

pedal_library = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, pedal_library)

from tests.execution_helper import Execution, SUCCESS_MESSAGE
from pedal.core.commands import *


class TestFeedback(unittest.TestCase):
    maxDiff = None

    def test_no_errors(self):
        with Execution('a=0\na') as e:
            pass
        self.assertEqual(e.feedback, SUCCESS_MESSAGE)

    def test_success(self):
        with Execution('a=0\na') as e:
            set_success()
        self.assertEqual(e.feedback, "Complete\nGreat work!")

    def test_runtime(self):
        with Execution('0+"A"', old_style_messages=True) as e:
            suppress("analyzer")
        self.assertEqual(e.feedback,
                         """Type Error
A TypeError occurred:

    Unsupported operand type(s) for +: 'int' and 'str'

I ran your code.

The traceback was:
Line 1 of file answer.py
    0+"A"


Type errors occur when you use an operator or function on the wrong type of value. For example, using `+` to add to a list (instead of `.append`), or dividing a string by a number.

Suggestion: To fix a type error, you should trace through your code. Make sure each expression has the type you expect it to have.""")

    @unittest.skip
    def test_tifa(self):
        with Execution('0+"A"') as e:
            pass
        self.assertEqual(e.feedback, "TypeError<br><pre>unsupported operand "
                                     "type(s) for +: 'int' and 'str'</pre>\n")


if __name__ == '__main__':
    unittest.main(buffer=False)
