import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pedal.report import *
from pedal.source import set_source
from pedal.tifa import tifa_analysis
from pedal.resolvers import simple
from pedal.sandbox import compatibility
from pedal.toolkit.files import *

class Execution:
    def __init__(self, code):
        self.code = code
    
    def __enter__(self):
        clear_report()
        set_source(self.code)
        tifa_analysis()
        return self
    
    def __exit__(self, *args):
        compatibility.run_student(raise_exceptions=True)
        suppress("runtime", "FileNotFoundError")
        (self.success, self.score, self.category, self.label, 
         self.message, self.data, self.hide) = simple.resolve()

class TestCode(unittest.TestCase):

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
        

if __name__ == '__main__':
    unittest.main(buffer=False)