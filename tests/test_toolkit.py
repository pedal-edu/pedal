import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pedal.report import *
from pedal.source import set_source
from pedal.tifa import tifa_analysis
from pedal.resolvers import simple
from pedal.sandbox import compatibility
from pedal.toolkit.files import files_not_handled_correctly
from pedal.toolkit.functions import match_signature, output_test, unit_test

class Execution:
    def __init__(self, code):
        self.code = code
    
    def __enter__(self):
        clear_report()
        set_source(self.code)
        tifa_analysis()
        compatibility.run_student(raise_exceptions=True)
        return self
    
    def __exit__(self, *args):
        suppress("runtime", "FileNotFoundError")
        (self.success, self.score, self.category, self.label, 
         self.message, self.data, self.hide) = simple.resolve()

class TestFiles(unittest.TestCase):

    def test_files_not_handled_correctly(self):
        with Execution('open("not opened.txt")') as e:
            self.assertTrue(files_not_handled_correctly(1))
        self.assertEqual(e.message, "You have not closed all the files you "
                         "were supposed to.")
        
        with Execution('open("not opened.txt")\nclose()') as e:
            self.assertTrue(files_not_handled_correctly(1))
        self.assertEqual(e.message, "You have attempted to call "
                         "<code>close</code> as a function, but it is "
                         "actually a method of the file object.")
        
        with Execution('open()') as e:
            self.assertTrue(files_not_handled_correctly(1))
        self.assertEqual(e.message, "You have called the <code>open</code> "
                           "function without any arguments. It needs a "
                           "filename.")
        
        with Execution('"filename.txt".open()') as e:
            self.assertTrue(files_not_handled_correctly(1))
        self.assertEqual(e.message, "You have attempted to call "
                         "<code>open</code> as a method, but it is actually a "
                         "built-in function.")
         
        
        with Execution('a = open("A.txt")\na.close()') as e:
            self.assertTrue(files_not_handled_correctly(2))
        self.assertEqual(e.message, "You have not opened all the files you "
                         "were supposed to.")
        
        
        with Execution('a = open("A.txt")\nb = open("B.txt")'
                   '\na.close()\nb.close()') as e:
            self.assertTrue(files_not_handled_correctly(1))
        self.assertEqual(e.message, "You have opened more files than you "
                         "were supposed to.")
                         
        
        with Execution('a = open("A.txt")\n\na.close()\na.close()') as e:
            self.assertTrue(files_not_handled_correctly(1))
        self.assertEqual(e.message, "You have closed more files than you "
                         "were supposed to.")
         
        
        with Execution('with open("A.txt") as out:\n  b = open("B.txt")'
                   '\n  b.close()') as e:
            self.assertTrue(files_not_handled_correctly(1))
        self.assertEqual(e.message, "You have opened more files than you "
                         "were supposed to.")
         
        
        with Execution('with open("A.txt") as out:\n  print(out.read())') as e:
            self.assertTrue(files_not_handled_correctly("X.txt"))
        self.assertEqual(e.message, "You need the literal value "
                         "<code>'X.txt'</code> in your code.")
        
        
        with Execution('a = open("filename.txt")\na.close()') as e:
            self.assertFalse(files_not_handled_correctly(1))
        
class TestFunctions(unittest.TestCase):

    def test_match_signature(self):
        with Execution('a = 0\na') as e:
            self.assertIsNone(match_signature('a', 0))
        self.assertEqual(e.message, "No function named <code>a</code> "
                         "was found.")
        
        with Execution('def a():\n  pass\na') as e:
            self.assertIsNotNone(match_signature('a', 0))
        self.assertNotEqual(e.message, "No function named <code>a</code> "
                            "was found.")
        
        with Execution('def a():\n  pass\na') as e:
            self.assertIsNone(match_signature('a', 1))
        self.assertNotEqual(e.message, "The function named <code>a</code> "
                            "has fewer parameters (0) than expected (1)")

        with Execution('def a(x, y):\n  pass\na') as e:
            self.assertIsNone(match_signature('a', 1))
        self.assertNotEqual(e.message, "The function named <code>a</code> "
                            "has fewer parameters (2) than expected (1)")
                            
        with Execution('def a(l, m):\n  pass\na') as e:
            self.assertIsNone(match_signature('a', 2, 'x', 'y'))
        self.assertEqual(e.message, "Error in definition of "
                         "<code>a</code>. Expected a parameter named "
                         "x, instead found l.")
        
        with Execution('def a(x, y):\n  pass\na') as e:
            self.assertIsNotNone(match_signature('a', 2, 'x', 'y'))
        self.assertNotEqual(e.message, "Error in definition of "
                            "<code>a</code>. Expected a parameter named "
                            "x, instead found l.")
    
    def test_unit_test(self):
        # All passing
        with Execution('def a(x,y):\n  return(x+y)\na') as e:
            self.assertIsNotNone(unit_test('a', (1, 2, 3)))
        self.assertEqual(e.message, "No errors reported.")
        
        # All failing
        with Execution('def a(x,y):\n  return(x-y)\na') as e:
            self.assertIsNone(unit_test('a', (1, 2, 3)))
        self.assertIn("it failed 1/1 tests", e.message)
        
        # Some passing, some failing
        with Execution('def a(x,y):\n  return(x-y)\na') as e:
            self.assertIsNone(unit_test('a', (1, 2, 3), (0, 0, 0)))
        self.assertIn("it failed 1/2 tests", e.message)
        
        # Optional tip
        with Execution('def a(x,y):\n  return(x-y)\na') as e:
            self.assertIsNone(unit_test('a', (1, 2, (3, "Try again!"))))
        self.assertIn("it failed 1/1 tests", e.message)
        self.assertIn("Try again!", e.message)
        
        # Float precision
        with Execution('def a(x,y):\n  return(x+y)\na') as e:
            self.assertIsNotNone(unit_test('a', (1.0, 2.0, 3.0)))
        self.assertEqual(e.message, "No errors reported.")
        
        # Not a function
        with Execution('a = 5\na') as e:
            self.assertIsNone(unit_test('a', (1, 2, 3)))
        self.assertEqual(e.message, "You defined a, but did not define "
                         "it as a function.")
        
        # Not defined
        with Execution('x = 5\nx') as e:
            self.assertIsNone(unit_test('a', (1, 2, 3)))
        self.assertEqual(e.message, "The function <code>a</code> was "
                         "not defined.")

if __name__ == '__main__':
    unittest.main(buffer=False)