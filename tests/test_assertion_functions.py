"""
Tests related to checking function definitions
"""

import unittest
from pedal.assertions.static import *
from tests.execution_helper import Execution, ExecutionTestCase


class TestAssertions(ExecutionTestCase):
    def test_function_found_complex(self):
        with Execution('def x(a: int, b: str, c: [int]) -> str: pass\nx') as e:
            self.assertFalse(ensure_function('x', 3, (int, str, 'list[int]'),
                                             str))
        self.assertFeedback(e, "No Errors\nNo errors reported.")

    def test_function_missing_parameter(self):
        with Execution('def x(a: int, b, c: [int]) -> str: pass\nx') as e:
            self.assertTrue(ensure_function('x', 3, (int, str, 'list[int]'), str))
        self.assertFeedback(e, "Missing Parameter Type\n"
                               "The function named <code class='pedal-name'>x</code> "
                               "has a parameter named <code class='pedal-name'>b</code>, "
                               "but that parameter does not have a type specified.")

    def test_function_custom_class(self):
        with Execution('D = list\ndef x(a: int, c: D) -> str: pass\nx\nD') as e:
            f = ensure_function('x', parameters=(int, 'int'), returns=str)
            self.assertTrue(f)
        print(f.fields)
        self.assertFeedback(e, "Wrong Parameter Type\n"
                               "The function named <code class='pedal-name'>x</code> "
                               "has a parameter named <code class='pedal-name'>c</code> "
                               "that is a 'D' type, but should be a number.")


if __name__ == '__main__':
    unittest.main(buffer=False)
