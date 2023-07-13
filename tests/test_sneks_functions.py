"""
Unit tests from the old curriculum-sneks library that has now been ported into Pedal core.
"""
from textwrap import dedent
import unittest
from pedal import *
from pedal.assertions.static import *
from pedal.utilities.system import IS_AT_LEAST_PYTHON_39
from tests.execution_helper import Execution, ExecutionTestCase, SUCCESS_MESSAGE


class TestFiles(ExecutionTestCase):

    def test_files_not_closed(self):
        with Execution('open("not opened.txt")') as e:
            self.assertTrue(files_not_handled_correctly(1))
        self.assertFeedback(e, "Unclosed Files\nYou have not closed all the files you "
                               "were supposed to.")

    def test_files_closed_as_function(self):
        with Execution('open("not opened.txt")\nclose()') as e:
            self.assertTrue(files_not_handled_correctly(1))
        self.assertFeedback(e, "Close Is a Method\nYou have attempted to call "
                               "`close` as a function, but it is "
                               "actually a method of the file object.")

    def test_files_open_without_filename(self):
        with Execution('open()') as e:
            self.assertTrue(files_not_handled_correctly(1))
        self.assertEqual(e.final.message, "You have called the `open` "
                                          "function without any arguments. It needs a "
                                          "filename.")

    def test_files_open_as_method(self):
        with Execution('"filename.txt".open()') as e:
            self.assertTrue(files_not_handled_correctly(1))
        self.assertEqual(e.final.message, "You have attempted to call "
                                          "`open` as a method, but it is actually a "
                                          "built-in function.")

    def test_files_not_all_files_opened(self):
        with Execution('a = open("A.txt")\na.close()') as e:
            self.assertTrue(files_not_handled_correctly(2))
        self.assertEqual(e.final.message, "You have not opened all the files you "
                                          "were supposed to.")

    def test_files_too_many_opens(self):
        with Execution('a = open("A.txt")\nb = open("B.txt")'
                       '\na.close()\nb.close()') as e:
            self.assertTrue(files_not_handled_correctly(1))
        self.assertEqual(e.final.message, "You have opened more files than you "
                                          "were supposed to.")

    def test_files_too_many_closes(self):
        with Execution('a = open("A.txt")\n\na.close()\na.close()') as e:
            self.assertTrue(files_not_handled_correctly(1))
        self.assertEqual(e.final.message, "You have closed more files than you "
                                          "were supposed to.")

    def test_files_too_many_with_opens(self):
        with Execution('with open("A.txt") as out:\n  b = open("B.txt")'
                       '\n  b.close()') as e:
            self.assertTrue(files_not_handled_correctly(1))
        self.assertEqual(e.final.message, "You have opened more files than you "
                                          "were supposed to.")

    def test_files_missing_filename(self):
        with Execution('with open("A.txt") as out:\n  print(out.read())') as e:
            self.assertTrue(files_not_handled_correctly("X.txt"))
            suppress(Feedback.CATEGORIES.RUNTIME)
        self.assertEqual(e.final.message, "You must use the literal value "
                                          "'X.txt'.")

    def test_files_with_open_success(self):
        with Execution('with open("A.txt") as out:\n  print(out.read())') as e:
            self.assertFalse(files_not_handled_correctly("A.txt"))
            suppress(Feedback.CATEGORIES.RUNTIME)
        self.assertEqual(e.final.message, "Great work!")

        with Execution('a = open("filename.txt")\na.close()') as e:
            self.assertFalse(files_not_handled_correctly(1))


class TestFiles(ExecutionTestCase):
    def test_only_printing_variables(self):
        with Execution('a,b=0,1\nprint(a,b)') as e:
            self.assertFalse(only_printing_variables())
        with Execution('print(0,"True", True)') as e:
            self.assertTrue(only_printing_variables())
        with Execution('print(True)') as e:
            self.assertTrue(only_printing_variables())


    def test_prevent_advanced_iteration(self):
        with Execution('while False:\n  pass') as e:
            prevent_advanced_iteration()
        self.assertEqual(e.final.message, "You used a while loop on line 1. You may not use that.")
        with Execution('sum([1,2,3])') as e:
            prevent_advanced_iteration()
        self.assertEqual(e.final.message, "You used the function sum on line 1. You may not use that function.")

    @unittest.skip
    def test_ensure_assignment(self):
        with Execution('a=0') as e:
            self.assertNotEqual(ensure_assignment("a", "Num"), False)
        with Execution('a=""') as e:
            self.assertNotEqual(ensure_assignment("a", "Str"), False)
        with Execution('a=True') as e:
            self.assertNotEqual(ensure_assignment("a", "Bool"), False)