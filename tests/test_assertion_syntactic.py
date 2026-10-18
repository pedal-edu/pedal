from textwrap import dedent
import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pedal.assertions.syntactic import *
from pedal.utilities.system import IS_AT_LEAST_PYTHON_39
from tests.execution_helper import Execution, ExecutionTestCase, SUCCESS_MESSAGE

class TestAssertionsSyntactic(ExecutionTestCase):
    def test_reject_code_used(self):
        with Execution('sum([1,2,3])') as e:
            self.assertTrue(reject_code('sum([1,2,3])'))
        self.assertFeedback(e, "May Not Use Code\n"
                               "You used the code sum([1,2,3]). "
                               "You may not use that code.")


    def test_reject_code_not_used(self):
        with Execution('max([1,2,3])') as e:
            self.assertFalse(reject_code('sum([1,2,3])'))
        self.assertFeedback(e, SUCCESS_MESSAGE)


    def test_reject_code_above_limit(self):
        with Execution('a=0\na=0\na=1') as e:
            self.assertTrue(reject_code('a=0', at_most=1))
        self.assertFeedback(e, "May Not Use Code\n"
                               "You used the code a=0. "
                               "You may not use that code more than "
                               "1 times, but you used it 2 times.")


    def test_reject_code_below_limit(self):
        with Execution('a=0\na=1', run_tifa=False) as e:
            self.assertFalse(reject_code('a=0', at_most=2))
        self.assertFeedback(e, SUCCESS_MESSAGE)


    def test_require_code_missing(self):
        with Execution('max([1,2,3])') as e:
            self.assertTrue(require_code('sum([1,2,3])'))
        self.assertFeedback(e, "Must Use Code\n"
                               "You must use the code sum([1,2,3]).")


    def test_require_code_present(self):
        with Execution('sum([1,2,3])') as e:
            self.assertFalse(require_code('sum([1,2,3])'))
        self.assertFeedback(e, SUCCESS_MESSAGE)


    def test_require_code_below_limit(self):
        with Execution('a=0\na=1') as e:
            self.assertTrue(require_code('a=0', at_least=2))
        self.assertFeedback(e, "Must Use Code\n"
                               "You must use the code a=0 at least "
                               "2 times, but you used it 1 times.")


    def test_require_code_meets_limit(self):
        with Execution('a=0\na=0\na=1', run_tifa=False) as e:
            self.assertFalse(require_code('a=0', at_least=2))
        self.assertFeedback(e, SUCCESS_MESSAGE)


    def test_reject_code_regex_used(self):
        with Execution('sum([1,2,3])') as e:
            self.assertTrue(reject_code_regex(r'sum\s*\('))
        self.assertFeedback(e, "May Not Use Pattern\n"
                               "You used the code sum(. "
                               "You may not use that code.")


    def test_reject_code_regex_not_used(self):
        with Execution('max([1,2,3])') as e:
            self.assertFalse(reject_code_regex(r'sum\s*\('))
        self.assertFeedback(e, SUCCESS_MESSAGE)


    def test_reject_code_regex_above_limit(self):
        with Execution('print(1)\nprint(2)\nprint(3)') as e:
            self.assertTrue(reject_code_regex(r'print\s*\(', at_most=2))
        self.assertFeedback(e, "May Not Use Pattern\n"
                               "You used the code print(. "
                               "You may not use that code more than "
                               "2 times, but you used it 3 times.")


    def test_reject_code_regex_below_limit(self):
        with Execution('print(1)\nprint(2)') as e:
            self.assertFalse(reject_code_regex(r'print\s*\(', at_most=2))
        self.assertFeedback(e, SUCCESS_MESSAGE)


    def test_require_code_regex_missing(self):
        with Execution('max([1,2,3])') as e:
            self.assertTrue(require_code_regex(r'sum\s*\('))
        self.assertFeedback(e, "Must Use Pattern\n"
                               "You must use the pattern sum\\s*\\(.")


    def test_require_code_regex_present(self):
        with Execution('sum([1,2,3])') as e:
            self.assertFalse(require_code_regex(r'sum\s*\('))
        self.assertFeedback(e, SUCCESS_MESSAGE)


    def test_require_code_regex_below_limit(self):
        with Execution('print(1)\nprint(2)') as e:
            self.assertTrue(require_code_regex(r'print\s*\(', at_least=3))
        self.assertFeedback(e, ('Must Use Pattern\n'
 'You must use the pattern print\\s*\\( at least 3 times, but you used it 2 '
 'times. You did use the pattern at least once, where you wrote print('))


    def test_require_code_regex_meets_limit(self):
        with Execution('print(1)\nprint(2)\nprint(3)') as e:
            self.assertFalse(require_code_regex(r'print\s*\(', at_least=3))
        self.assertFeedback(e, SUCCESS_MESSAGE)


    def test_reject_code_regex_with_flags(self):
        with Execution('Print(1)\nprint(2)') as e:
            self.assertTrue(reject_code_regex(r'print\s*\(', flags=re.IGNORECASE, at_most=1))
        self.assertFeedback(e, "May Not Use Pattern\n"
                               "You used the code Print(. "
                               "You may not use that code more than "
                               "1 times, but you used it 2 times.")


    def test_require_code_finds_text_in_string(self):
        with Execution('x = "sum([1,2,3])"', run_tifa=False) as e:
            self.assertFalse(require_code('sum([1,2,3])'))
        self.assertFeedback(e, SUCCESS_MESSAGE)


    def test_reject_code_finds_text_in_comment(self):
        with Execution('# sum([1,2,3])\npass') as e:
            self.assertTrue(reject_code('sum([1,2,3])'))
        self.assertFeedback(e, "May Not Use Code\n"
                               "You used the code sum([1,2,3]). "
                               "You may not use that code.")

    def test_require_finds_partial_function_header(self):
        with Execution('from bakery import assert_equal\n\ndef target_function(x: int)\n    pass\ntarget_function()', run_verify=False, run_student=False) as e:
            self.assertFalse(require_code('def target_function('))
            self.assertFalse(require_code_regex(r'def target_function\([^:]+?:[^:]+?\)'))
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_require_ignores_bad_partial_function_header(self):
        with Execution('from bakery import assert_equal\n\ndef target_function(x: int, y: int)\n    pass\ntarget_function()', run_verify=False, run_student=False) as e:
            self.assertTrue(require_code_regex(r'def target_function\([^:]+?:[^:]+?\)'))
        self.assertFeedback(e, ('Must Use Pattern\n'
 'You must use the pattern def target_function\\([^:]+?:[^:]+?\\).'))

    def test_custom_feedback_message_partial_header(self):
        with Execution(
                'from bakery import assert_equal\n\ndef target_function(x: int)\n    pass\ntarget_function()',
                run_verify=False, run_student=False) as e:
            self.assertFalse(require_code_regex(r'def target_function\([^:]+?:[^:]+?\)', else_message="You at least had part of the code there!"))
        self.assertEqual(e.final.positives[0].message, "You at least had part of the code there!")