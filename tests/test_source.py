import unittest
import os
import sys
from textwrap import dedent

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pedal.core import *
from pedal.core.commands import clear_report, get_all_feedback, contextualize_report
from pedal.source import *
from pedal.tifa import tifa_analysis
from tests.execution_helper import Execution
import pedal.resolvers.sectional as sectional


class TestCode(unittest.TestCase):

    def test_catches_blank_files(self):
        contextualize_report('')
        verify()
        feedback = get_all_feedback()
        self.assertTrue(feedback)
        self.assertEqual(feedback[0].label, 'blank_source')

        contextualize_report('                  \n\n\n \n\n\n      ')
        verify()
        feedback = get_all_feedback()
        self.assertTrue(feedback)
        self.assertEqual(feedback[0].label, 'blank_source')

    def test_catches_syntax_errors(self):
        contextualize_report('a b c')
        verify()
        feedback = get_all_feedback()
        self.assertTrue(feedback)
        self.assertEqual(feedback[0].label, 'syntax_error')

    def test_syntax_traceback_good(self):
        with Execution('a=0\nb b b\nc = 0') as e:
            pass
        self.assertFalse(e.final.success)
        self.assertEqual(e.final.label, 'syntax_error')
        self.assertEqual("""Bad syntax on line 2

The traceback was:
Line 2 of file answer.py
    b b b


Suggestion: Check line 2, the line before it, and the line after it.""", e.final.message)

    def test_no_more_input(self):
        contextualize_report('def x():')
        verify()
        feedback = get_all_feedback()
        self.assertTrue(feedback)
        self.assertEqual(feedback[0].label, 'syntax_error')
        self.assertEqual(feedback[0].message, """Bad syntax on line 1

The traceback was:
Line 1 of file answer.py
    def x():


Suggestion: Check line 1, the line before it, and the line after it.""")

    def test_sections_syntax_errors(self):
        contextualize_report(dedent('''
        NAMES = [____, ____]
        ##### Part 1
        a = 0
        print(a)
        ##### Part 2
        Syntax Error!
        ##### Part 3
        Runtime Error
        '''))
        separate_into_sections(independent=True)
        check_section_exists(3)
        self.assertEqual(get_all_feedback()[0].label, "FeedbackSourceSection")
        next_section()
        verify_section()
        self.assertEqual(get_all_feedback()[1].label, "FeedbackSourceSection")
        next_section()
        verify_section()
        feedback = get_all_feedback()
        self.assertTrue(feedback)
        self.assertEqual(feedback[3].label, "syntax_error")
        print(feedback[0].location)
        self.assertEqual(feedback[3].location.line, 7)

    def test_damaged_sections(self):
        contextualize_report(dedent('''
        NAMES = [____, ____]
        ##### Part 1
        a = 0
        print(a)
        ##### Part 2
        Syntax Error!
        #### Part 3
        Runtime Error
        '''))
        verify()
        separate_into_sections()
        check_section_exists(3)
        feedback = get_all_feedback()
        self.assertTrue(feedback)
        self.assertTrue(feedback[0].label, "incorrect_number_of_sections")

    def test_sections_tifa(self):
        contextualize_report(dedent('''
        ##### Part 1
        a = 0
        ##### Part 2
        print(a)
        ##### Part 3
        print(b)
        '''))
        separate_into_sections(independent=False)
        # First section has an unused variable
        next_section()
        self.assertEqual(len(get_all_feedback()), 2)
        tifa_analysis()
        self.assertEqual(len(get_all_feedback()), 3)
        # Second section uses said variable
        next_section()
        self.assertEqual(len(get_all_feedback()), 4)
        tifa_analysis()
        self.assertEqual(len(get_all_feedback()), 4)
        # Third section has a new unused variables
        next_section()
        self.assertEqual(len(get_all_feedback()), 5)
        tifa_analysis()
        feedback = get_all_feedback()
        self.assertEqual(len(get_all_feedback()), 6)
        finals = sectional.resolve()
        self.assertEqual("""FeedbackSourceSection
Feedback separated into groups
Unused Variable
The variable a was given a value on line 3, but was never used after that.
Initialization Problem
The variable b was used on line 7, but it was not given a value on a previous line. You cannot use a variable until it has been given a value.""",
                         "\n".join(f.title+"\n"+f.message for f in finals.values()))


if __name__ == '__main__':
    unittest.main(buffer=False)
