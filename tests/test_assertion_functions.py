"""
Tests related to checking function definitions
"""

import unittest

from pedal import unit_test
from pedal.assertions.static import *
from pedal.types.definitions import DictType, LiteralStr, StrType
from tests.execution_helper import Execution, ExecutionTestCase, SUCCESS_MESSAGE


class TestAssertions(ExecutionTestCase):
    def test_function_found_complex_passes(self):
        with Execution('def x(a: int, b: str, c: [int]) -> str: pass\nx') as e:
            self.assertFalse(ensure_function('x', 3, (int, str, [int]),
                                             str))
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_function_found_complex_fails(self):
        with Execution('def x(a: int, b: str, c: [int]) -> str: pass\nx') as e:
            self.assertTrue(ensure_function('x', 3, (int, str, [str]),
                                             str))
        self.assertFeedback(e, """Wrong Parameter Type
The function named x has a parameter named c that is a list of a number, but should be a list of a string.""")

    def test_function_missing_parameter(self):
        with Execution('def x(a: int, b, c: [int]) -> str: pass\nx') as e:
            self.assertTrue(ensure_function('x', 3, (int, str, 'list[int]'), str))
        self.assertFeedback(e, "Missing Parameter Type\n"
                               "The function named x "
                               "has a parameter named b, "
                               "but that parameter does not have a type specified.")

    @unittest.skip("This is currently broken!")
    def test_function_custom_class(self):
        with Execution('D = list\ndef x(a: int, c: D) -> str: pass\nx\nD') as e:
            f = ensure_function('x', parameters=(int, 'int'), returns=str)
            self.assertTrue(f)
        print(f.fields)
        self.assertFeedback(e, "Wrong Parameter Type\n"
                               "The function named x "
                               "has a parameter named c "
                               "that is a 'D' type, but should be a number.")

    def test_assert_type_custom_record_passes(self):
        Dog = DictType(literals=[LiteralStr("Name")], values=[StrType()])
        with Execution('Dog = {"Name": str}\ndef pet(d: Dog) -> str: return d["Name"]\npet({"Name": "Fido"})') as e:
            f = ensure_function('pet', parameters=('Dog',), returns=str)
            self.assertFalse(f)
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_assert_type_custom_record_fails(self):
        Dog = DictType(literals=[LiteralStr("Name")], values=[StrType()])
        with Execution('def pet(d: str) -> str: return d\npet("Fido")') as e:
            f = ensure_function('pet', parameters=('Dog',), returns=str)
            self.assertTrue(f)
        self.assertFeedback(e, "Wrong Parameter Type\n"
                               "The function named pet has a parameter named d"
                               " that is a string, but should be Dog.")

    def test_unit_test_partial_credit_true(self):
        with Execution('def add(a, b): return b', run_tifa=False) as e:
            unit_test('add',
                      ((1, 2), 3),
                      ((0, 0), 0),
                      ((0, 3), 3),
                      ((0, 5), 5),
                      ((1, 3), 4),
                      score="+100%",
                      partial_credit=True)
        self.assertEqual(3/5, e.final.score)
        self.assertFeedback(e, """
Failed Instructor Test
Student code failed instructor tests.
You passed 3/5 tests.

I ran your function add on some new arguments.
 | Arguments | Returned | Expected
× |     1, 2 | 2 | 3
  |     0, 0 | 0 | 0
  |     0, 3 | 3 | 3
  |     0, 5 | 5 | 5
× |     1, 3 | 3 | 4""")

    def test_bad_name_error_concatenation(self):
        with Execution("""
def make_polite(message: str) -> str:
    return ", please"+make_polite

make_polite("Pet the dog")""", run_tifa=False) as e:
            unit_test('make_polite',
                      ([""], ", please"),
                      (["Pet the dog"], "Pet the dog, please"),
                      (["Walk the dog"], "Walk the dog, please"))
        self.assertFeedback(e, """Type Error
A TypeError occurred:

    Can only concatenate str (not "function") to str

I ran your code.

The traceback was:
Line 5 of file answer.py
    make_polite("Pet the dog")

Line 3 of file answer.py in make_polite
        return ", please"+make_polite


Type errors occur when you use an operator or function on the wrong type of value. For example, using `+` to add to a list (instead of `.append`), or dividing a string by a number.

Suggestion: To fix a type error, you should trace through your code. Make sure each expression has the type you expect it to have.""")


if __name__ == '__main__':
    unittest.main(buffer=False)
