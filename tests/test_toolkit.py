import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pedal.report import *
from pedal.source import set_source
from pedal.tifa import tifa_analysis
from pedal.resolvers import simple
from pedal.toolkit.files import *

class TestCode(unittest.TestCase):

    def test_files_not_handled_correctly(self):
        clear_report()
        set_source('open("not opened.txt")')
        tifa_analysis()
        self.assertTrue(files_not_handled_correctly(1))
        _, _, _, _, message, _, _ = simple.resolve()
        self.assertEqual(message, "You have not closed all the files you were "
                         "supposed to.")
        
        clear_report()
        set_source('open("not opened.txt")\nclose()')
        tifa_analysis()
        self.assertTrue(files_not_handled_correctly(1))
        _, _, _, _, message, _, _ = simple.resolve()
        self.assertEqual(message, "You have attempted to call "
                         "<code>close</code> as a function, but it is "
                         "actually a method of the file object.")
        
        clear_report()
        set_source('open()')
        tifa_analysis()
        self.assertTrue(files_not_handled_correctly(1))
        _, _, _, _, message, _, _ = simple.resolve()
        self.assertEqual(message, "You have called the <code>open</code> "
                           "function without any arguments. It needs a "
                           "filename.")
        
        clear_report()
        set_source('"filename.txt".open()')
        tifa_analysis()
        self.assertTrue(files_not_handled_correctly(1))
        _, _, _, _, message, _, _ = simple.resolve()
        self.assertEqual(message, "You have attempted to call "
                         "<code>open</code> as a method, but it is actually a "
                         "built-in function.")
         
        clear_report()
        set_source('a = open("A.txt")\na.close()')
        tifa_analysis()
        self.assertTrue(files_not_handled_correctly(2))
        _, _, _, _, message, _, _ = simple.resolve()
        self.assertEqual(message, "You have not opened all the files you "
                         "were supposed to.")
        
        clear_report()
        set_source('a = open("A.txt")\nb = open("B.txt")'
                   '\na.close()\nb.close()')
        tifa_analysis()
        self.assertTrue(files_not_handled_correctly(1))
        _, _, _, _, message, _, _ = simple.resolve()
        self.assertEqual(message, "You have opened more files than you "
                         "were supposed to.")
                         
        clear_report()
        set_source('a = open("A.txt")\n'
                   '\na.close()\na.close()')
        tifa_analysis()
        self.assertTrue(files_not_handled_correctly(1))
        _, _, _, _, message, _, _ = simple.resolve()
        self.assertEqual(message, "You have closed more files than you "
                         "were supposed to.")
         
        clear_report()
        set_source('with open("A.txt") as out:\n  b = open("B.txt")'
                   '\n  b.close()')
        tifa_analysis()
        self.assertTrue(files_not_handled_correctly(1))
        _, _, _, _, message, _, _ = simple.resolve()
        self.assertEqual(message, "You have opened more files than you "
                         "were supposed to.")
         
        clear_report()
        set_source('with open("A.txt") as out:\n  print(out.read())')
        tifa_analysis()
        self.assertTrue(files_not_handled_correctly("X.txt"))
        _, _, _, _, message, _, _ = simple.resolve()
        self.assertEqual(message, "You need the literal value "
                         "<code>'X.txt'</code> in your code.")
        
        clear_report()
        set_source('a = open("filename.txt")\na.close()')
        tifa_analysis()
        self.assertFalse(files_not_handled_correctly(1))
        

if __name__ == '__main__':
    unittest.main(buffer=False)