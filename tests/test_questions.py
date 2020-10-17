import unittest
import os
import sys
from textwrap import dedent
from pprint import pprint

from pedal.source import set_source

from pedal.cait import parse_program
from pedal.sandbox.commands import run

pedal_library = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, pedal_library)

from pedal import *
from pedal.core import *
from pedal.resolvers import sectional
from pedal.questions import *
from pedal.assertions import *

from tests.execution_helper import Execution, ExecutionTestCase


class TestQuestions(ExecutionTestCase):

    def test_choose_ask(self):
        with Execution('0') as e:
            set_seed(0)
            question_A = Question("QA", "Create a for loop.", [])
            question_B = Question("QB", "Create an if statement.", [])
            pool_1 = Pool("P1", [question_A, question_B])
            pool_1.choose().ask()
        self.assertFeedback(e, "Show Question\nCreate a for loop.")
        
        with Execution('0') as e:
            set_seed(1)
            question_A = Question("QA", "Create a for loop.", [])
            question_B = Question("QB", "Create an if statement.", [])
            pool_1 = Pool("P1", [question_A, question_B])
            pool_1.choose().ask()
        self.assertFeedback(e, "Show Question\nCreate an if statement.")

    # TODO: Finish this test once the functionality is ready!
    @unittest.skip
    def test_exam_progress(self):
        def test_has_loop(question):
            ast = parse_program()
            if not ast.find_all("For"):
                gently("No for loop yet.")
            else:
                question.answer()
        question_A = Question("QA", "Create a for loop.", [test_has_loop])
        question_B = Question("QB", "Create an if statement.", [])
        pool_1 = Pool("P1", [question_A, question_B])
        def test_variable(question):
            student = run()
            if assert_has_variable(student, "alpha", value=2):
                question.answer()
        question_C = Question("QC", "Create a variable.", [test_variable])
        pool_2 = Pool("P2", [question_C])
        def test_second_variable(question):
            student = run()
            if not assert_has_variable(student, "beta", value=3):
                question.answer()
                set_success()
        question_D = Question("QD", "Create a beta variable.", [test_second_variable])
        pool_3 = Pool("P3", [question_D])
        def make_exam(code):
            """

            Args:
                code:
            """
            clear_report()
            set_seed(0)
            set_source(code)
            student = run()
            pool_1.choose().ask()
            pool_2.choose().ask()
            if pool_1.answered and pool_2.answered:
                pool_3.choose().ask()
        # Opened a blank file and evaluated
        make_exam('')
        finals = sectional.resolve()
        print(finals)
        self.assertEqual(finals[0][0]['message'], "Create a for loop.")
        self.assertEqual(finals[0][1]['message'], "Create a variable.")
        self.assertEqual(finals[0][2]['message'], "Source code file is blank.")
        # Tried writing some inadequate code
        make_exam('if True: pass')
        finals = sectional.resolve()
        self.assertEqual(finals[0][0]['message'], "Create a for loop.")
        # Tried writing some bad code
        make_exam('1 + ""')
        finals = sectional.resolve()
        self.assertEqual(finals[0][0]['message'], "Create a for loop.")
        self.assertEqual(finals[0][1]['message'], "Create a variable.")
        self.assertEqual(finals[0][2]['message'], dedent("""
               A TypeError occurred:

<pre>Unsupported operand type(s) for +: 'int' and 'str'</pre>

I ran the file `answer.py`.

The traceback was:
  Line 1 of file answer.py
    1 + ""


Type errors occur when you use an operator or function on the wrong type of value. For example, using `+` to add to a list (instead of `.append`), or dividing a string by a number.

Suggestion: To fix a type error, you should trace through your code. Make sure each expression has the type you expect it to have.""").lstrip())
        # Tried writing some good code
        make_exam('for x in []: pass')
        final_success, final_score, _, finals = sectional.resolve()
        self.assertEqual(finals[0][0]['message'], "Create a variable.")
        self.assertFalse(final_success)
        # Tried writing some 100% correct code
        make_exam('for x in []: pass\nalpha = 2\nbeta = 3')
        final_success, final_score, _, finals = sectional.resolve()
        self.assertEqual(finals[0][0]['message'], "No errors reported.")
        self.assertTrue(final_success)

if __name__ == '__main__':
    unittest.main(buffer=False)
