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

        with Execution('a=0\nb b b\nc = 0') as e:
            pass
        self.assertFalse(e.success)
        print(e.feedback)
        self.assertEqual(e.label, 'syntax_error')
        self.assertIn("Bad syntax on line 2", e.message)

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
        separate_into_sections()
        check_section_exists(3)
        self.assertFalse(get_all_feedback())
        next_section()
        verify_section()
        self.assertFalse(get_all_feedback())
        next_section()
        verify_section()
        feedback = get_all_feedback()
        self.assertTrue(feedback)
        self.assertEqual(feedback[0].label, "syntax_error")
        self.assertEqual(feedback[0].locations[0].line, 7)

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
        separate_into_sections()
        # First section has an unused variable
        next_section()
        self.assertEqual(len(get_all_feedback()), 0)
        tifa_analysis(True)
        self.assertEqual(len(get_all_feedback()), 1)
        # Second section uses said variable
        next_section()
        self.assertEqual(len(get_all_feedback()), 1)
        tifa_analysis(True)
        self.assertEqual(len(get_all_feedback()), 1)
        # Third section has a new unused variables
        next_section()
        self.assertEqual(len(get_all_feedback()), 1)
        tifa_analysis(True)
        feedback = get_all_feedback()
        self.assertEqual(len(get_all_feedback()), 2)


if __name__ == '__main__':
    unittest.main(buffer=False)
