import unittest
import os
import sys

pedal_library = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, pedal_library)

from pedal.cait.cait_api import parse_program
from pedal.toolkit.files import files_not_handled_correctly
from pedal.toolkit.functions import match_signature, output_test, unit_test
from pedal.toolkit.utilities import (is_top_level, function_prints,
                                     no_nested_function_definitions,
                                     find_function_calls, function_is_called,
                                     only_printing_variables, prevent_literal,
                                     find_prior_initializations,
                                     prevent_unused_result, ensure_literal,
                                     prevent_builtin_usage, find_operation,
                                     prevent_advanced_iteration,
                                     ensure_operation, prevent_operation)
from pedal.toolkit.imports import ensure_imports
from pedal.toolkit.printing import ensure_prints
from execution_helper import Execution

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
        
        with Execution('with open("A.txt") as out:\n  print(out.read())') as e:
            self.assertFalse(files_not_handled_correctly("A.txt"))
        self.assertEqual(e.message, "No errors reported.")
        
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
    
    def test_output_test(self):
        # All passing
        with Execution('def a(x):\n  print(x+1)\na(1)') as e:
            self.assertIsNotNone(output_test('a', (2, "3")))
        self.assertEqual(e.message, "No errors reported.")
        
        # All failing
        with Execution('def a(x,y):\n  print(x-y)\na(1,2)') as e:
            self.assertIsNone(output_test('a', (1, 2, "3")))
        self.assertIn("wrong output 1/1 times", e.message)

class TestUtilities(unittest.TestCase):
    def test_is_top_level(self):
        with Execution('print("Test")\ndef a(x):\n  print(x+1)\na(1)') as e:
            ast = parse_program()
            defs = ast.find_all('FunctionDef')
            self.assertEqual(len(defs), 1)
            self.assertTrue(is_top_level(defs[0]))
            self.assertEqual(len(defs[0].body), 1)
            self.assertFalse(is_top_level(defs[0].body[0]))
            calls = ast.find_all('Call')
            self.assertEqual(len(calls), 3)
            self.assertTrue(is_top_level(calls[0]))
            self.assertFalse(is_top_level(calls[1]))
        self.assertEqual(e.message, "No errors reported.")
    
    def test_no_nested_function_definitions(self):
        with Execution('if True:\n  def x():\n    pass\n  x()') as e:
            self.assertFalse(no_nested_function_definitions())
        self.assertEqual(e.message, "You have defined a function inside of "
                         "another block. For instance, you may have placed it "
                         "inside another function definition, or inside of a "
                         "loop. Do not nest your function definition!")
        with Execution('if True:\n  pass\ndef x():\n  pass\nx()') as e:
            self.assertTrue(no_nested_function_definitions())
        self.assertEqual(e.message, "No errors reported.")
    
    def test_function_prints(self):
        # Function prints
        with Execution('def a(x):\n  print(x+1)\na(1)') as e:
            self.assertTrue(function_prints())
        self.assertEqual(e.message, "No errors reported.")
        # Function only returns, no prints
        with Execution('def a(x):\n  return x+1\na(1)') as e:
            self.assertFalse(function_prints())
        self.assertEqual(e.message, "No errors reported.")
        # Function does not print, but prints exist
        with Execution('print("T")\ndef a(x):\n  x\na(1)\nprint("E")') as e:
            self.assertFalse(function_prints())
        self.assertEqual(e.message, "No errors reported.")
    
    def test_find_function_calls(self):
        with Execution('def a(x):\n  print(x,1)\na(1)\nprint("T")') as e:
            prints = find_function_calls('print')
            self.assertEqual(len(prints), 2)
            self.assertEqual(len(prints[0].args), 2)
            self.assertEqual(len(prints[1].args), 1)
        self.assertEqual(e.message, "No errors reported.")
        with Execution('a=[]\na.append(a)\na.pop()\n') as e:
            pops = find_function_calls('pop')
            self.assertEqual(len(pops), 1)
            self.assertEqual(len(pops[0].args), 0)
        self.assertEqual(e.message, "No errors reported.")
    
    def test_function_is_called(self):
        with Execution('a=[]\na.append(a)\na.pop()\n') as e:
            self.assertTrue(function_is_called('pop'))
            self.assertFalse(function_is_called('print'))
        self.assertEqual(e.message, "No errors reported.")
    
    def test_only_printing_variables(self):
        with Execution('a,b=0,1\nprint(a,b)') as e:
            self.assertTrue(only_printing_variables())
        with Execution('print(0,"True", True)') as e:
            self.assertFalse(only_printing_variables())
        with Execution('print(True)') as e:
            self.assertFalse(only_printing_variables())
    
    def test_find_prior_initializations(self):
        with Execution('a=0\na\na=5\na') as e:
            ast = parse_program()
            self.assertEqual(len(ast.body), 4)
            self.assertEqual(ast.body[3].ast_name, "Expr")
            self.assertEqual(ast.body[3].value.ast_name, "Name")
            priors = find_prior_initializations(ast.body[3].value)
            self.assertEqual(len(priors), 2)
    
    def test_prevent_unused_result(self):
        with Execution('a="H  "\na.strip()') as e:
            prevent_unused_result()
        self.assertEqual(e.message, "Remember! You cannot modify a string "
                         "directly. Instead, you should assign the result "
                         "back to the string variable.")
        
        with Execution('a="H  "\nb=a.strip()\nb') as e:
            prevent_unused_result()
        self.assertEqual(e.message, "No errors reported.")
        
        with Execution('a=[]\na.append(1)\na') as e:
            prevent_unused_result()
        self.assertEqual(e.message, "No errors reported.")
    
    def test_prevent_builtin_usage(self):
        with Execution('sum([1,2,3])') as e:
            self.assertEqual(prevent_builtin_usage(['sum', 'min']), 'sum')
        self.assertEqual(e.message, "You cannot use the builtin function "
                         "<code>sum</code>.")
        
        with Execution('max([1,2,3])') as e:
            self.assertIsNone(prevent_builtin_usage(['sum', 'min']))
        self.assertEqual(e.message, "No errors reported.")
    
    def test_prevent_literal(self):
        with Execution('a = 5\na') as e:
            self.assertEqual(prevent_literal(3, 4, 5), 5)
        self.assertEqual(e.message, "Do not use the literal value "
                         "<code>5</code> in your code.")
        with Execution('print("Hello")') as e:
            self.assertEqual(prevent_literal("Hello"), "Hello")
        self.assertEqual(e.message, "Do not use the literal value "
                         "<code>'Hello'</code> in your code.")
        with Execution('print("Hello", 5)') as e:
            self.assertFalse(prevent_literal("Fire", 3, 4))
        self.assertEqual(e.message, "No errors reported.")
    
    def test_ensure_literal(self):
        with Execution('a = 5\na') as e:
            self.assertEqual(ensure_literal(3, 4, 5), 3)
        self.assertEqual(e.message, "You need the literal value "
                         "<code>3</code> in your code.")
        with Execution('print("Hell")') as e:
            self.assertEqual(ensure_literal("Hello"), "Hello")
        self.assertEqual(e.message, "You need the literal value "
                         "<code>'Hello'</code> in your code.")
        with Execution('print("Fire", 3, 4)') as e:
            self.assertFalse(ensure_literal("Fire", 3, 4))
        self.assertEqual(e.message, "No errors reported.")
    
    def test_prevent_advanced_iteration(self):
        with Execution('while False:\n  pass') as e:
            prevent_advanced_iteration()
        self.assertEqual(e.message, "You should not use a <code>while</code> "
                         "loop to solve this problem.")
        with Execution('sum([1,2,3])') as e:
            prevent_advanced_iteration()
        self.assertEqual(e.message, "You cannot use the builtin function "
                         "<code>sum</code>.")
    
    def test_ensure_operation(self):
        with Execution('print(1-1)') as e:
            self.assertFalse(ensure_operation("+"))
        self.assertEqual(e.message, "You are not using the <code>+</code> "
                         "operator.")
        with Execution('print(1+1)') as e:
            self.assertNotEqual(ensure_operation("+"), False)
        self.assertEqual(e.message, "No errors reported.")
        with Execution('print(1!=1)') as e:
            self.assertNotEqual(ensure_operation("!="), False)
        self.assertEqual(e.message, "No errors reported.")
    
    def test_prevent_operation(self):
        with Execution('print(1+1)') as e:
            self.assertNotEqual(prevent_operation("+"), False)
        self.assertEqual(e.message, "You may not use the <code>+</code> "
                         "operator.")
        with Execution('print(1-1)') as e:
            self.assertFalse(prevent_operation("+"))
        self.assertEqual(e.message, "No errors reported.")
        with Execution('1 < 1') as e:
            self.assertNotEqual(prevent_operation("<"), False)
        self.assertEqual(e.message, "You may not use the <code><</code> "
                         "operator.")
    
    def test_find_operation(self):
        with Execution('1+1') as e:
            ast = parse_program()
            self.assertNotEqual(find_operation("+", ast), False)
        with Execution('1>1') as e:
            ast = parse_program()
            self.assertNotEqual(find_operation(">", ast), False)
        with Execution('True and True') as e:
            ast = parse_program()
            self.assertNotEqual(find_operation("and", ast), False)
        with Execution('not True') as e:
            ast = parse_program()
            self.assertNotEqual(find_operation("not", ast), False)
        with Execution('not (1 + 1) and 1 < 1 <= 10') as e:
            ast = parse_program()
            self.assertFalse(find_operation(">", ast))
        with Execution('1 in [1,2,3]') as e:
            ast = parse_program()
            self.assertNotEqual(find_operation("in", ast), False)

class TestImports(unittest.TestCase):
    def test_ensure_imports(self):
        with Execution('json = "0"\njson.loads("0")+0') as e:
            self.assertTrue(ensure_imports("json"))
        self.assertEqual(e.message, "You need to import the <code>json</code> "
                         "module.")
        with Execution('from requests import json\njson.loads("0")+0') as e:
            self.assertTrue(ensure_imports("json"))
        self.assertEqual(e.message, "You need to import the <code>json</code> "
                         "module.")
        with Execution('import json\njson.loads("0")+0') as e:
            self.assertFalse(ensure_imports("json"))
        self.assertEqual(e.message, "No errors reported.")
        with Execution('from json import loads\nloads("0")+0') as e:
            self.assertFalse(ensure_imports("json"))
        self.assertEqual(e.message, "No errors reported.")
        
class TestPrints(unittest.TestCase):
    def test_ensure_prints(self):
        with Execution('print(1)\nprint(2)') as e:
            self.assertFalse(ensure_prints(1))
        self.assertEqual(e.message, "You are printing too many times!")
        with Execution('print(1)\nprint(2)') as e:
            self.assertFalse(ensure_prints(3))
        self.assertEqual(e.message, "You are not printing enough things!")
        with Execution('a = 0\na') as e:
            self.assertFalse(ensure_prints(1))
        self.assertEqual(e.message, "You are not using the print function!")
        with Execution('def x():\n  print(x)\nx()') as e:
            self.assertFalse(ensure_prints(1))
        self.assertEqual(e.message, "You have a print function that is not at "
                                    "the top level. That is incorrect for "
                                    "this problem!")
        with Execution('print(1)\nprint(2)') as e:
            prints = ensure_prints(2)
            self.assertNotEqual(prints, False)
            self.assertEqual(len(prints), 2)
        self.assertEqual(e.message, "No errors reported.")

if __name__ == '__main__':
    unittest.main(buffer=False)