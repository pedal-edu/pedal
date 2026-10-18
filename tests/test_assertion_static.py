from textwrap import dedent
import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pedal.assertions.static import *
from pedal.utilities.system import IS_AT_LEAST_PYTHON_39
from tests.execution_helper import Execution, ExecutionTestCase, SUCCESS_MESSAGE


class TestAssertions(ExecutionTestCase):
    def test_prevent_function_usage(self):
        with Execution('sum([1,2,3])') as e:
            f = prevent_function_call('sum')
            self.assertTrue(f)
        self.assertEqual(f.specifier, 'sum')
        self.assertFeedback(e, "May Not Use Function\n"
                               "You used the function sum on line 1. "
                               "You may not use that function.")

        with Execution('max([1,2,3])') as e:
            self.assertFalse(prevent_function_call('sum'))
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_prevent_operator_used(self):
        with Execution('2+3') as e:
            self.assertTrue(prevent_operation('+'))
        self.assertFeedback(e, "May Not Use Operator\n"
                               "You used the operator + on line 1. "
                               "You may not use that operator.")

    def test_prevent_operator_not_used(self):
        with Execution('+3') as e:
            self.assertFalse(prevent_function_call('+'))
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_prevent_operator_below_limit(self):
        with Execution('1+3-4') as e:
            self.assertFalse(prevent_function_call('+', at_most=2))
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_prevent_operator_above_limit(self):
        with Execution('2+3+4\n1+2') as e:
            self.assertTrue(prevent_operation('+', at_most=2))
        self.assertFeedback(e, "May Not Use Operator\n"
                               "You used the operator + on line 2. "
                               "You may not use that operator more than "
                               "2 times, but you used it 3 times.")

    def test_ensure_operator_above_limit(self):
        with Execution('2+3+4\n1+2') as e:
            self.assertTrue(ensure_operation('+', at_least=5))
        self.assertFeedback(e, "Must Use Operator\n"
                               "You must use the operator + at least "
                               "5 times, but you used it 3 times.")

    def test_prevent_muted(self):
        with Execution('sum([1,2,3])') as e:
            self.assertTrue(prevent_function_call('sum', muted=True))
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_prevent_literal_used_int(self):
        with Execution('a = 5\na') as e:
            self.assertTrue(prevent_literal(5))
        self.assertFeedback(e, "May Not Use Literal Value\n"
                               "You used the literal value 5 on line 1. "
                               "You may not use that value.")

    def test_prevent_literal_used_str(self):
        with Execution('print("Hello")') as e:
            self.assertTrue(prevent_literal("Hello"))
        self.assertFeedback(e, "May Not Use Literal Value\n"
                               "You used the literal value 'Hello' on line 1."
                               " You may not use that value.")

    def test_prevent_literal_unused(self):
        with Execution('print("Hello", 5)') as e:
            self.assertFalse(prevent_literal("Fire"))
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_prevent_literal_used_negative_int(self):
        with Execution('a = -1+2\na') as e:
            self.assertTrue(prevent_literal(-1))
        self.assertFeedback(e, "May Not Use Literal Value\n"
                               "You used the literal value -1 on line 1. "
                               "You may not use that value.")

    def test_prevent_literal_used_boolean(self):
        with Execution('a = True\na') as e:
            self.assertTrue(prevent_literal(True))
        self.assertFeedback(e, "May Not Use Literal Value\n"
                               "You used the literal value True on line 1. "
                               "You may not use that value.")

    def test_ensure_literal_used_int(self):
        with Execution('a = 6\na') as e:
            self.assertTrue(ensure_literal(5))
        self.assertFeedback(e, "Must Use Literal Value\n"
                               "You must use the literal value 5.")

    def test_ensure_literal_used_str(self):
        with Execution('print("Helo")') as e:
            self.assertTrue(ensure_literal("Hello"))
        self.assertFeedback(e, "Must Use Literal Value\n"
                               "You must use the literal value 'Hello'.")

    def test_ensure_literal_unused(self):
        with Execution('print("Hello", 5)') as e:
            self.assertFalse(ensure_literal("Hello"))
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_ensure_literal_used_negative_int(self):
        with Execution('a = -15+2\na') as e:
            self.assertTrue(ensure_literal(-1))
        self.assertFeedback(e, "Must Use Literal Value\n"
                               "You must use the literal value -1.")

    def test_ensure_literal_used_boolean(self):
        with Execution('a = False\na') as e:
            self.assertTrue(ensure_literal(True))
        self.assertFeedback(e, "Must Use Literal Value\n"
                               "You must use the literal value True.")

    def test_prevent_literal_bool_does_not_match_int(self):
        # True == 1 in Python, but the literals are different code
        with Execution('a = 1\na') as e:
            self.assertFalse(prevent_literal(True))
        self.assertFeedback(e, SUCCESS_MESSAGE)
        with Execution('a = 0\na') as e:
            self.assertFalse(prevent_literal(False))
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_prevent_literal_int_does_not_match_bool(self):
        with Execution('a = True\na') as e:
            self.assertFalse(prevent_literal(1))
        self.assertFeedback(e, SUCCESS_MESSAGE)
        with Execution('a = False\na') as e:
            self.assertFalse(prevent_literal(0))
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_prevent_literal_int_does_not_match_float(self):
        with Execution('a = 1.0\na') as e:
            self.assertFalse(prevent_literal(1))
        self.assertFeedback(e, SUCCESS_MESSAGE)
        with Execution('a = 1\na') as e:
            self.assertFalse(prevent_literal(1.0))
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_prevent_literal_used_float(self):
        with Execution('a = 1.0\na') as e:
            self.assertTrue(prevent_literal(1.0))
        self.assertFeedback(e, "May Not Use Literal Value\n"
                               "You used the literal value 1.0 on line 1. "
                               "You may not use that value.")

    def test_prevent_literal_used_none(self):
        with Execution('a = None\na') as e:
            self.assertTrue(prevent_literal(None))
        self.assertFeedback(e, "May Not Use Literal Value\n"
                               "You used the literal value None on line 1. "
                               "You may not use that value.")

    def test_prevent_literal_none_does_not_match_other_literals(self):
        with Execution('a = 0\nb = ""\nc = False\nprint(a, b, c)') as e:
            self.assertFalse(prevent_literal(None))
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_ensure_literal_bool_does_not_match_int(self):
        with Execution('a = 1\na') as e:
            self.assertTrue(ensure_literal(True))
        self.assertFeedback(e, "Must Use Literal Value\n"
                               "You must use the literal value True.")
        with Execution('a = True\na') as e:
            self.assertTrue(ensure_literal(1))
        self.assertFeedback(e, "Must Use Literal Value\n"
                               "You must use the literal value 1.")

    def test_ensure_literal_none(self):
        with Execution('a = None\na') as e:
            self.assertFalse(ensure_literal(None))
        self.assertFeedback(e, SUCCESS_MESSAGE)
        with Execution('a = 0\na') as e:
            self.assertTrue(ensure_literal(None))
        self.assertFeedback(e, "Must Use Literal Value\n"
                               "You must use the literal value None.")

    def test_ensure_ast_index_used(self):
        # Python 3.9+ no longer has an Index node, but 'Index' should still work
        with Execution('a = [1, 2]\na[0]') as e:
            self.assertFalse(ensure_ast('Index'))
        self.assertFeedback(e, SUCCESS_MESSAGE)
        with Execution('a = {"k": 1}\na["k"]') as e:
            self.assertFalse(ensure_ast('Index'))
        self.assertFeedback(e, SUCCESS_MESSAGE)
        # And so should the modern Subscript node
        with Execution('a = [1, 2]\na[0]') as e:
            self.assertFalse(ensure_ast('Subscript'))
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_ensure_ast_index_unused(self):
        with Execution('a = [1, 2]\na') as e:
            self.assertTrue(ensure_ast('Index'))
        self.assertFeedback(e, "Must Use Code\n"
                               "You must use an index.")
        # A slice is a Subscript, but not an Index
        with Execution('a = [1, 2]\na[0:1]') as e:
            self.assertTrue(ensure_ast('Index'))
        self.assertFeedback(e, "Must Use Code\n"
                               "You must use an index.")
        with Execution('a = [1, 2]\na[0:1]') as e:
            self.assertFalse(ensure_ast('Subscript'))
        self.assertFeedback(e, SUCCESS_MESSAGE)
        with Execution('a = [1, 2]\na[0:1]') as e:
            self.assertFalse(ensure_ast('Slice'))
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_prevent_ast_index_used(self):
        with Execution('a = [1, 2]\na[1]') as e:
            self.assertTrue(prevent_ast('Index'))
        self.assertFeedback(e, "May Not Use Code\n"
                               "You used an index on line 2. "
                               "You may not use that.")
        with Execution('a = [1, 2]\na[1]') as e:
            self.assertTrue(prevent_ast('Subscript'))
        self.assertFeedback(e, "May Not Use Code\n"
                               "You used a subscript on line 2. "
                               "You may not use that.")

    def test_prevent_ast_index_unused(self):
        with Execution('a = [1, 2]\na[0:1]\na') as e:
            self.assertFalse(prevent_ast('Index'))
        self.assertFeedback(e, SUCCESS_MESSAGE)
        with Execution('a = [1, 2]\na[0:1]\na[1]') as e:
            self.assertFalse(prevent_ast('Index', at_most=1))
        self.assertFeedback(e, SUCCESS_MESSAGE)
        with Execution('a = [1, 2]\na[0:1]\na[1]\na[0]') as e:
            self.assertTrue(prevent_ast('Index', at_most=1))
        self.assertFeedback(e, "May Not Use Code\n"
                               "You used an index on line 4. "
                               "You may not use that more than 1 times, "
                               "but you used it 2 times.")

    @unittest.skipUnless(IS_AT_LEAST_PYTHON_39, "requires python 3.9+")
    def test_ensure_function_types(self):
        # [int]
        with Execution(dedent("""
        def sum_high(numbers: list[int]) -> int:
            total = 0
            for num in numbers:
                if num >= 50:
                    total += num
            return total
        
        sum_high([1,2,3])
        """) )as e:
            self.assertFalse(ensure_function('sum_high', parameters=[[int]], returns='int'))
        self.assertFeedback(e, SUCCESS_MESSAGE)
        # list[int]
        with Execution(dedent("""
        def sum_high(numbers: list[int]) -> int:
            total = 0
            for num in numbers:
                if num >= 50:
                    total += num
            return total

        sum_high([1,2,3])
        """)) as e:
            self.assertFalse(ensure_function('sum_high', parameters=[list[int]], returns='int'))
        self.assertFeedback(e, SUCCESS_MESSAGE)

    @unittest.skipUnless(IS_AT_LEAST_PYTHON_39, "requires python 3.9+")
    def test_ensure_function_nested_and_constant_types(self):
        code = dedent("""
        def summarize(scores: dict[str, list[int]], threshold: float) -> None:
            print(scores, threshold)

        summarize({"a": [1]}, 0.5)
        """)
        with Execution(code) as e:
            self.assertFalse(ensure_function('summarize',
                                             parameters=[dict[str, list[int]], float],
                                             returns='None'))
        self.assertFeedback(e, SUCCESS_MESSAGE)
        with Execution(code) as e:
            self.assertFalse(ensure_function('summarize',
                                             parameters=['dict[str, list[int]]', 'float'],
                                             returns=None))
        self.assertFeedback(e, SUCCESS_MESSAGE)
        # Mismatched nested type is still caught
        with Execution(code) as e:
            f = ensure_function('summarize', parameters=[dict[str, list[str]], float])
            self.assertTrue(f)
        self.assertEqual(f.label, 'wrong_parameter_type')
        # Mismatched None return type is still caught
        with Execution(code) as e:
            f = ensure_function('summarize', returns=int)
            self.assertTrue(f)
        self.assertEqual(f.label, 'wrong_return_type')

    def test_prevent_printing_functions(self):
        with Execution(dedent("""def x():\n print('Hello')\nx()""")) as e:
            self.assertTrue(prevent_printing_functions())
        self.assertFeedback(e, """Do Not Print in Function
The function x is printing on line 2. However, that function is not supposed to print.""")

        with Execution(dedent("""def x():\n return 'Hello' \nx()""")) as e:
            self.assertFalse(prevent_printing_functions())
        self.assertFeedback(e, "Complete\nGreat work!")

        with Execution(dedent("""def x():\n return 'Hello' \ndef main():\n  print(x())\nmain()""")) as e:
            self.assertFalse(prevent_printing_functions('main'))
        self.assertFeedback(e, "Complete\nGreat work!")

        with Execution(dedent("""def x():\n return 'Hello' \ndef main():\n  print(x())\nmain()""")) as e:
            self.assertTrue(prevent_printing_functions('x'))
        self.assertFeedback(e, """Do Not Print in Function
The function main is printing on line 4. However, that function is not supposed to print.""")
