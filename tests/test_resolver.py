import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pedal.report import *
from pedal.resolvers import simple

class TestCode(unittest.TestCase):

    def test_gently(self):
        clear_report()
        success, message = simple.resolve()
        self.assertFalse(success)
        self.assertEqual(message, "No errors reported.")
        
        gently('You should always create unit tests.')
        success, message = simple.resolve()
        self.assertFalse(success)
        self.assertEqual(message, 'You should always create unit tests.')
        
        gently('A boring message that we should not show.')
        success, message = simple.resolve()
        self.assertFalse(success)
        self.assertEqual(message, 'You should always create unit tests.')
        
        set_success()
        success, message = simple.resolve()
        self.assertTrue(success)
        self.assertEqual(message, 'You should always create unit tests.')

if __name__ == '__main__':
    unittest.main(buffer=False)