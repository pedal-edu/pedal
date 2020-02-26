import unittest
import os
import sys

pedal_library = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, pedal_library)

from tests.execution_helper import Execution
from pedal.core.commands import *


class TestFeedback(unittest.TestCase):
    maxDiff = None

    def test_no_errors(self):
        with Execution('a=0\na') as e:
            pass
        self.assertEqual(e.feedback, "No Errors\nNo errors reported.")

    def test_success(self):
        with Execution('a=0\na') as e:
            set_success()
        self.assertEqual(e.feedback, "Complete\nGreat work!")

    def test_runtime(self):
        with Execution('0+"A"', old_style_messages=True) as e:
            suppress("analyzer")
        self.assertEqual(e.feedback, "TypeError\n<pre>unsupported operand "
                                     "type(s) for +: 'int' and 'str'</pre>\n"
                                     "Type errors most often occur when an expression "
                                     "tries to combine two objects with types that should "
                                     "not be combined. Like using <code>+</code> to add a "
                                     "number to a list instead of <code>.append</code>, "
                                     "or dividing a string by a number."
                                     "<br><b>Suggestion:</b> To fix a type error you will "
                                     "most likely need to trace through your code and "
                                     "make sure the variables have the types you expect "
                                     "them to have."
                         )

    @unittest.skip
    def test_tifa(self):
        with Execution('0+"A"') as e:
            pass
        self.assertEqual(e.feedback, "TypeError<br><pre>unsupported operand "
                                     "type(s) for +: 'int' and 'str'</pre>\n")


if __name__ == '__main__':
    unittest.main(buffer=False)
