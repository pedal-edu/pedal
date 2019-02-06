import unittest
import os
import sys
from textwrap import dedent

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pedal.report import *
from pedal.source import *
from pedal.tifa import tifa_analysis
from tests.execution_helper import Execution


class TestCode(unittest.TestCase):

    def test_catches_blank_files(self):
        clear_report()
        set_source('')
        feedback = get_all_feedback()
        self.assertTrue(feedback)
        self.assertEqual(feedback[0].label, 'Blank source')

        clear_report()
        set_source('                  \n\n\n \n\n\n      ')
        feedback = get_all_feedback()
        self.assertTrue(feedback)
        self.assertEqual(feedback[0].label, 'Blank source')

    def test_catches_syntax_errors(self):
        clear_report()
        set_source('a b c')
        feedback = get_all_feedback()
        self.assertTrue(feedback)
        self.assertEqual(feedback[0].label, 'Syntax error')

        with Execution('a=0\nb b b\nc = 0') as e:
            pass
        self.assertFalse(e.success)
        self.assertEqual(e.label, 'Syntax error')
        self.assertEqual(e.message, "Invalid syntax on line 2")

    def test_sections_syntax_errors(self):
        clear_report()
        set_source(dedent('''
        NAMES = [____, ____]
        ##### Part 1
        a = 0
        print(a)
        ##### Part 2
        Syntax Error!
        ##### Part 3
        Runtime Error
        '''), sections=True)
        check_section_exists(3)
        self.assertFalse(get_all_feedback())
        next_section()
        verify_section()
        self.assertFalse(get_all_feedback())
        next_section()
        verify_section()
        feedback = get_all_feedback()
        self.assertTrue(feedback)
        self.assertEqual(feedback[0].label, "Syntax error")
        self.assertEqual(feedback[0].mistake['position']['line'], 7)

    def test_damaged_sections(self):
        clear_report()
        set_source(dedent('''
        NAMES = [____, ____]
        ##### Part 1
        a = 0
        print(a)
        ##### Part 2
        Syntax Error!
        #### Part 3
        Runtime Error
        '''), sections=True)
        check_section_exists(3)
        feedback = get_all_feedback()
        self.assertTrue(feedback)

    def test_sections_tifa(self):
        clear_report()
        set_source(dedent('''
        ##### Part 1
        a = 0
        ##### Part 2
        print(a)
        ##### Part 3
        print(b)
        '''), sections=True)
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
