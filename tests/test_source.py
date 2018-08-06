import unittest
import os
import sys

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

if __name__ == '__main__':
    unittest.main(buffer=False)