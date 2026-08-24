"""
Regression tests for CAIT contaminating the shared ``ast.Load``/``Store``/
``Del`` singletons (CPython >= 3.13) and for ``CaitNode.__getattr__``
recursing forever during ``copy.deepcopy``.
"""
import ast
import copy
import unittest

from pedal.cait.cait_api import parse_program
from pedal.cait.cait_node import CaitNode
from pedal.core.report import MAIN_REPORT
from pedal.source import set_source


class TestCaitCtxSingletons(unittest.TestCase):
    def setUp(self):
        MAIN_REPORT.clear()

    def test_ctx_nodes_are_not_tagged(self):
        set_source("x = 1\nprint(x)\ndel x")
        parse_program()
        tree = ast.parse("y = 2\nprint(y)\ndel y")
        for node in ast.walk(tree):
            if isinstance(node, ast.expr_context):
                self.assertFalse(hasattr(node, 'cait_node'),
                                 "%s singleton was tagged" % type(node).__name__)

    def test_deepcopy_of_unrelated_ast_after_grading(self):
        set_source("x = 1")
        parse_program()
        tree = ast.parse("y = 2")
        copy.deepcopy(tree)  # Previously RecursionError on 3.13+

    def test_deepcopy_of_graded_ast(self):
        set_source("x = 1")
        program = parse_program()
        copy.deepcopy(program.astNode)

    def test_getattr_astnode_does_not_recurse(self):
        node = CaitNode.__new__(CaitNode)
        with self.assertRaises(AttributeError):
            node.astNode
        self.assertFalse(hasattr(node, '__setstate__'))

    def test_ctx_still_accessible_via_cait(self):
        set_source("x = 1\nprint(x)")
        program = parse_program()
        names = program.find_all("Name")
        self.assertEqual(names[0].ctx.astNode.__class__, ast.Store)
        self.assertEqual(names[1].ctx.astNode.__class__, ast.Load)
        self.assertIsInstance(names[0].ctx, CaitNode)


if __name__ == '__main__':
    unittest.main()
