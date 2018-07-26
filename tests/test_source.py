import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pedal.report import *
from pedal.source import *

class TestCode(unittest.TestCase):

    def test_catches_blank_files(self):
        clear_report()
        set_source('')
        feedback = get_all_feedback()
        self.assertTrue(feedback)
        self.assertEqual(feedback[0].label, 'blank_source')
        
        clear_report()
        set_source('                  \n\n\n \n\n\n      ')
        feedback = get_all_feedback()
        self.assertTrue(feedback)
        self.assertEqual(feedback[0].label, 'blank_source')

    def test_catches_syntax_errors(self):
        clear_report()
        set_source('a b c')
        feedback = get_all_feedback()
        self.assertTrue(feedback)
        self.assertEqual(feedback[0].label, 'syntax_error')

if __name__ == '__main__':
    unittest.main(buffer=False)