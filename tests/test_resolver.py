import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pedal.report import *
from pedal.source import set_source, next_section, verify_section
from pedal.tifa import tifa_analysis
from pedal.resolvers import simple, sectional
import pedal.sandbox.compatibility as compatibility

from execution_helper import Execution

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
    
    def test_explain(self):
        # Tifa < Explain
        with Execution('1+""') as e:
            explain("You cannot add those.")
        self.assertEqual(e.message, "You cannot add those.")
        # Tifa > Gently
        with Execution('1+""') as e:
            gently("You cannot add those.")
        self.assertEqual(e.label, "Incompatible types")
    
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
    
    def test_partials(self):
        with Execution('0') as e:
            give_partial(.1, "You had a zero in your code.")
            give_partial(.1, "You looped correctly.")
        self.assertEqual(e.message, "No errors reported.")
        self.assertEqual(e.score, .2)
        self.assertFalse(e.success)
        
        with Execution('0') as e:
            give_partial(.1, "You had a zero in your code.")
            give_partial(.1, "You looped correctly.")
            gently("Okay but you still only wrote 0.")
        self.assertEqual(e.message, "Okay but you still only wrote 0.")
        self.assertEqual(e.score, .2)
        self.assertFalse(e.success)
        
        with Execution('0') as e:
            give_partial(.1, "You had a zero in your code.")
            give_partial(.1, "You looped correctly.")
            set_success()
        self.assertEqual(e.message, "Great work!")
        self.assertEqual(e.score, .2)
        self.assertTrue(e.success)
    
    def test_analyzer_suppression(self):
        clear_report()
        set_source('1+"Hello"')
        tifa_analysis()
        compatibility.run_student(raise_exceptions=True)
        suppress("analyzer")
        (success, score, category, label, 
         message, data, hide) = simple.resolve()
        self.assertEqual(category, "Runtime")
        self.assertEqual(label, "TypeError")
    
    def test_runtime_suppression(self):
        clear_report()
        set_source('import json\njson.loads("0")+"1"')
        tifa_analysis()
        compatibility.run_student(raise_exceptions=True)
        suppress("Runtime")
        (success, score, category, label, 
         message, data, hide) = simple.resolve()
        self.assertEqual(category, "Instructor")
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
        self.assertEqual(message, "<pre>name 'a' is not defined</pre>\n"+
        "A name error almost always means that you have used a variable before it has a value.  Often this may be a simple typo, so check the spelling carefully.  <br><b>Suggestion: </b>Check the right hand side of assignment statements and your function calls, this is the most likely place for a NameError to be found. It really helps to step through your code, one line at a time, mentally keeping track of your variables.")
    
    def test_suppress_premade(self):
        try:
            a
        except Exception as e:
            ne = e
        clear_report()
        set_source('import json\njson.loads("0")+"1"')
        tifa_analysis()
        compatibility.raise_exception(ne)
        suppress("Runtime")
        (success, score, category, label, 
         message, data, hide) = simple.resolve()
        self.assertEqual(category, "Instructor")
        self.assertEqual(label, "No errors")
        self.assertEqual(message, "No errors reported.")
    
    def test_success(self):
        clear_report()
        set_source('a=0\na')
        tifa_analysis()
        set_success()
        (success, score, category, label, 
         message, data, hide) = simple.resolve()
        self.assertEqual(category, "Complete")
        self.assertEqual(label, "Complete")
        self.assertEqual(message, "Great work!")
    
    def test_success_suppression(self):
        clear_report()
        set_source('a=0\na')
        tifa_analysis()
        set_success()
        suppress('success')
        (success, score, category, label, 
         message, data, hide) = simple.resolve()
        self.assertEqual(category, "Instructor")
        self.assertEqual(label, "No errors")
        self.assertEqual(message, "No errors reported.")
    
    def test_empty(self):
        clear_report()
        set_source('    ')
        tifa_analysis()
        compatibility.run_student(raise_exceptions=True)
        (success, score, category, label, 
         message, data, hide) = simple.resolve()
        self.assertEqual(category, "Syntax")
        self.assertEqual(label, "Blank source")
        self.assertEqual(message, "Source code file is blank.")
    
    def test_gently_vs_runtime(self):
        # Runtime > Gently
        clear_report()
        set_source('import json\njson.loads("0")+"1"')
        tifa_analysis()
        compatibility.run_student(raise_exceptions=True)
        gently("I have a gentle opinion, but you don't want to hear it.")
        (success, score, category, label, 
         message, data, hide) = simple.resolve()
        self.assertEqual(category, "Runtime")
        
        # Runtime < Explain
        clear_report()
        set_source('import json\njson.loads("0")+"1"')
        tifa_analysis()
        compatibility.run_student(raise_exceptions=True)
        explain("LISTEN TO ME")
        (success, score, category, label, 
         message, data, hide) = simple.resolve()
        self.assertEqual(category, "instructor")
    
    def test_input(self):
        with Execution('input("Type something:")') as e:
            pass
        self.assertNotEqual(e.category, "Runtime")
        self.assertEqual(e.label, "No errors")
        
        with Execution('float(input("Type something:"))') as e:
            pass
        self.assertNotEqual(e.category, "Runtime")
        self.assertEqual(e.label, "No errors")
    
    def test_sectional_error(self):
        clear_report()
        set_source('a=0\n##### Part 1\nprint("A")\n##### Part 2\nsyntax error',
                   sections=True)
        next_section()
        if verify_section():
            compatibility.run_student(raise_exceptions=True)
            give_partial(.2)
        next_section()
        if verify_section():
            compatibility.run_student(raise_exceptions=True)
            give_partial(.3)
        (success, score, hc, messages) = sectional.resolve()
        self.assertEqual(success, False)
        self.assertEqual(score, .2)
        self.assertEqual(len(messages), 2)
    
    def test_sectional_success(self):
        clear_report()
        set_source('a=0\n##### Part 1\nprint("A")\n##### Part 2\nprint("B")',
                   sections=True)
        next_section()
        if verify_section():
            compatibility.run_student(raise_exceptions=True)
            give_partial(.2)
        next_section()
        if verify_section():
            compatibility.run_student(raise_exceptions=True)
            give_partial(.3)
            set_success()
        (success, score, hc, messages) = sectional.resolve()
        self.assertEqual(success, True)
        self.assertEqual(score, .5)
        self.assertEqual(len(messages), 1)

if __name__ == '__main__':
    unittest.main(buffer=False)