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
            question_A = Question("QA", "Create a for loop.", [lambda q: False])
            question_B = Question("QB", "Create an if statement.", [lambda q: False])
            pool_1 = Pool("P1", [question_A, question_B])
            pool_1.choose().ask()
        self.assertFeedback(e, "Show Question\nCreate a for loop.")
        
        with Execution('0') as e:
            set_seed(1)
            question_A = Question("QA", "Create a for loop.", [lambda q: False])
            question_B = Question("QB", "Create an if statement.", [lambda q: False])
            pool_1 = Pool("P1", [question_A, question_B])
            pool_1.choose().ask()
        self.assertFeedback(e, "Show Question\nCreate an if statement.")

    def test_choose_ask_using_with(self):
        with Execution('0') as e:
            set_seed(0)
            with Pool("P2") as pool_2:
                with Question("QA", "Create a for loop") as question_A:
                    gently("No answer")
                with Question("QB", "Create an if statement") as question_B:
                    gently("Different answer")
            pool_2.ask()
        self.assertFeedback(e, "Instructor Feedback\nNo answer")

    def test_function_grader_tifa(self):
        # Defaults to ignoring the grading function
        with Execution('def x(a: int) -> int:\n return a') as e:
            fg = FunctionGrader("x", [1, [int], int], [ [[1], 1], [[3], 3] ])
            pool_1 = Pool("P1", [Question("Q1", "Identity function", fg)])
            pool_1.choose().ask()
        self.assertFeedback(e, "Complete\nGreat work!")

        # Detects when not suppressed
        with Execution('def x(a: int) -> int:\n return a') as e:
            fg = FunctionGrader("x", [1, [int], int], [ [[1], 1], [[3], 3] ], {
                'suppress_function_unused': False
            })
            pool_1 = Pool("P1", [Question("Q1", "Identity function", fg)])
            pool_1.choose().ask()
        self.assertFeedback(e, "Unused Variable\nThe function x was given a definition on line 1, but was never used after that.")

        # Still detects other suppressed variables
        with Execution('def x(a: int) -> int:\n return 0\ny=0') as e:
            fg = FunctionGrader("x", [1, [int], int], [ [[1], 0], [[3], 0] ])
            pool_1 = Pool("P1", [Question("Q1", "Identity function", fg)])
            pool_1.choose().ask()
        self.assertFeedback(e, "Unused Variable\nThe variable y was given a value on line 3, but was never used after that.")

    # TODO: Finish this test once the functionality is ready!

    @unittest.skip("Question system is incomplete, finish testing!")
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
