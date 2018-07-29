import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pedal.report import *
from pedal.source import set_source
from pedal.tifa import tifa_analysis
from pedal.resolvers import simple
import pedal.sandbox.compatibility as compatibility

class TestCode(unittest.TestCase):

    def test_gently(self):
        clear_report()
        (success, score, category, label, 
         message, data, hide) = simple.resolve()
        self.assertFalse(success)
        self.assertEqual(message, "No errors reported.")
        
        gently('You should always create unit tests.')
        (success, score, category, label, 
         message, data, hide) = simple.resolve()
        self.assertFalse(success)
        self.assertEqual(message, 'You should always create unit tests.')
        
        gently('A boring message that we should not show.')
        (success, score, category, label, 
         message, data, hide) = simple.resolve()
        self.assertFalse(success)
        self.assertEqual(message, 'You should always create unit tests.')
        
        set_success()
        (success, score, category, label, 
         message, data, hide) = simple.resolve()
        self.assertTrue(success)
        self.assertEqual(message, 'You should always create unit tests.')
    
    def test_hidden_error(self):
        clear_report()
        set_source('import pedal')
        tifa_analysis()
        (success, score, category, label, 
         message, data, hide) = simple.resolve()
        self.assertNotEqual(message, "No errors reported.")
    
    def test_unmessaged_tifa(self):
        clear_report()
        set_source('import random\nrandom')
        tifa_analysis()
        (success, score, category, label, 
         message, data, hide) = simple.resolve()
        self.assertEqual(message, "No errors reported.")
    
    def test_premade_exceptions(self):
        try:
            a
        except Exception as e:
            ne = e
        clear_report()
        set_source('a=0\na')
        compatibility.raise_exception(ne)
        (success, score, category, label, 
         message, data, hide) = simple.resolve()
        self.assertEqual(message, "Hey what happened???")

if __name__ == '__main__':
    unittest.main(buffer=False)