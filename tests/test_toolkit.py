""" Tests for some AST operations stuffed into CAIT """
import unittest

from tests.execution_helper import Execution, SUCCESS_TEXT
from pedal.cait import *
from pedal.cait.find_node import (is_top_level, find_function_calls, function_is_called, find_prior_initializations,
                                  find_operation)


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
        self.assertEqual(e.final.message, SUCCESS_TEXT)

    def test_find_function_calls(self):
        with Execution('def a(x):\n  print(x,1)\na(1)\nprint("T")') as e:
            prints = find_function_calls('print')
            self.assertEqual(len(prints), 2)
            self.assertEqual(len(prints[0].args), 2)
            self.assertEqual(len(prints[1].args), 1)
        self.assertEqual(e.final.message, SUCCESS_TEXT)
        with Execution('a=[]\na.append(a)\na.pop()\n') as e:
            pops = find_function_calls('pop')
            self.assertEqual(len(pops), 1)
            self.assertEqual(len(pops[0].args), 0)
        self.assertEqual(e.final.message, SUCCESS_TEXT)

    def test_function_is_called(self):
        with Execution('a=[]\na.append(a)\na.pop()\n') as e:
            self.assertTrue(function_is_called('pop'))
            self.assertFalse(function_is_called('print'))
        self.assertEqual(e.final.message, SUCCESS_TEXT)

    def test_find_prior_initializations(self):
        with Execution('a=0\na\na=5\na') as e:
            ast = parse_program()
            self.assertEqual(len(ast.body), 4)
            self.assertEqual(ast.body[3].ast_name, "Expr")
            self.assertEqual(ast.body[3].value.ast_name, "Name")
            priors = find_prior_initializations(ast.body[3].value)
            self.assertEqual(len(priors), 2)


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
