import unittest
import os
import sys
from textwrap import dedent

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pedal.report import *
from pedal.source import *
from execution_helper import Execution

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
    
    def test_sections(self):
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
        verify_sections(3)
        feedback = get_all_feedback()
        self.assertFalse(feedback)

if __name__ == '__main__':
    unittest.main(buffer=False)