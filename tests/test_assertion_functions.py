"""
Tests related to checking function definitions
"""

import unittest

from pedal.utilities.system import IS_AT_LEAST_PYTHON_311
from pedal import unit_test, block_function, evaluate, CommandBlock, run, call
from pedal.assertions.static import *
from pedal.assertions.runtime import assert_equal, assert_greater, assert_output_contains
from pedal.types.new_types import DictType, LiteralStr, StrType
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
The function named x has a parameter named c that is a list of integers, but should be a list of strings.""")

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
        #print(f.fields)
        self.assertFeedback(e, "Wrong Parameter Type\n"
                               "The function named x "
                               "has a parameter named c "
                               "that is a 'D' type, but should be a number.")

    def test_assert_type_custom_record_passes(self):
        Dog = DictType({LiteralStr("Name"): StrType()})
        with Execution('Dog = {"Name": str}\ndef pet(d: Dog) -> str: return d["Name"]\npet({"Name": "Fido"})') as e:
            f = ensure_function('pet', parameters=('Dog',), returns=str)
            self.assertFalse(f)
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_assert_type_custom_record_fails(self):
        Dog = DictType({LiteralStr("Name"): StrType()})
        with Execution('def pet(d: str) -> str: return d\npet("Fido")') as e:
            f = ensure_function('pet', parameters=('Dog',), returns=str)
            self.assertTrue(f)
        self.assertFeedback(e, "Wrong Parameter Type\n"
                               "The function named pet has a parameter named d"
                               " that is a string, but should be A Dog.")

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
===================================
× |      1, 2 |        2 |        3
  |      0, 0 |        0 |        0
  |      0, 3 |        3 |        3
  |      0, 5 |        5 |        5
× |      1, 3 |        3 |        4""")

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
I ran your code.

A TypeError occurred:

    Can only concatenate str (not "function") to str

The traceback was:
Line 5 of file answer.py
    make_polite("Pet the dog")
""" + ('    ^^^^^^^^^^^^^^^^^^^^^^^^^^\n' if IS_AT_LEAST_PYTHON_311 else "") + """
Line 3 of file answer.py in make_polite
        return ", please"+make_polite
""" + ('               ^^^^^^^^^^^^^^^^^^^^^^\n' if IS_AT_LEAST_PYTHON_311 else "") + """
Type errors occur when you use an operator or function on the wrong type of value. For example, using `+` to add to a list (instead of `.append`), or dividing a string by a number.

Suggestion: To fix a type error, you should trace through your code. Make sure each expression has the type you expect it to have.""")

    @unittest.skip("Temporarily disabled while we fix skulpt's context manager")
    def test_unit_test_with_style(self):
        with Execution("""
def add(a, b):
    return a - b""", run_tifa=False) as e:
            with unit_test('add'):
                assert_equal(call('add', 1, 2), 3)
                assert_equal(call('add', 0, 0), 0)
        self.assertFeedback(e, """Failed Instructor Test
Student code failed instructor tests.
You passed 1/2 tests.

I ran your function add on some new arguments.
  | Arguments | Returned | Expected
===================================
× |      1, 2 |       -1 |        3
  |      0, 0 |        0 |        0""")

    def test_unit_test_blocked_function(self):
        with Execution("""
def summate(numbers: [int]) -> int:
    return sum(numbers)

print(summate([1,2,3]))""", run_tifa=False) as e:
            block_function('sum')
            unit_test('summate', [([1, 2, 3],), 6])
        self.assertFeedback(e, """Failed Instructor Test
Student code failed instructor tests.
You passed 0/1 tests.

I ran your function summate on some new arguments.
  |     Arguments |                           Returned | Expected
=================================================================
× |     [1, 2, 3] | You are not allowed to call 'sum'. |        6""")

    def test_unit_test_extra_context(self):
        with Execution('def add(a, b): return b', run_tifa=False) as e:
            unit_test('add',
                      ('data, 5', 17),
                      (([3, 3], 3), 9),
                      score="+100%",
                      context=evaluate('[5, 3, 4]', target='data'),
                      partial_credit=True)
        #self.assertEqual(3 / 5, e.final.score)
        self.assertFeedback(e, """
Failed Instructor Test
Student code failed instructor tests.
You passed 0/2 tests.

I ran the code:
    data = [5, 3, 4]

I ran your function add on some new arguments.
  |     Arguments | Returned | Expected
=======================================
× |       data, 5 |        5 |       17
× |     [3, 3], 3 |        3 |        9""")

    def test_unit_test_extra_context_run(self):
        with Execution('def add(a, b): return b', run_tifa=False) as e:
            run('this_should_not_appear = 5')
            unit_test('add',
                      ('data, 5', 17),
                      (([3, 3], 3), 9),
                      score="+100%",
                      context=run('data = [5, 3, 4]\ndata2 = [1,2,3]'),
                      partial_credit=True)
        #self.assertEqual(3 / 5, e.final.score)
        self.assertFeedback(e, """
Failed Instructor Test
Student code failed instructor tests.
You passed 0/2 tests.

I ran the code:
    data = [5, 3, 4]
    data2 = [1,2,3]

I ran your function add on some new arguments.
  |     Arguments | Returned | Expected
=======================================
× |       data, 5 |        5 |       17
× |     [3, 3], 3 |        3 |        9""")

    def test_unit_test_extra_context_calls(self):
        with Execution('def add(a, b): return b', run_tifa=False) as e:
            with CommandBlock() as context:
                evaluate('[1,2,3]', target='data')
                evaluate('[1,2,3]', target='data2')
            unit_test('add',
                      ('data, 5', 17),
                      ('data2, 5', 17),
                      (([3, 3], 3), 9),
                      score="+100%",
                      context=context,
                      partial_credit=True)
        #self.assertEqual(3 / 5, e.final.score)
        self.assertFeedback(e, """
Failed Instructor Test
Student code failed instructor tests.
You passed 0/3 tests.

I ran the code:
    data = [1,2,3]
    data2 = [1,2,3]

I ran your function add on some new arguments.
  |     Arguments | Returned | Expected
=======================================
× |       data, 5 |        5 |       17
× |      data2, 5 |        5 |       17
× |     [3, 3], 3 |        3 |        9""")

if __name__ == '__main__':
    unittest.main(buffer=False)
