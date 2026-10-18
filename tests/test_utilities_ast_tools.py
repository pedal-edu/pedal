"""
Tests for pedal.utilities.ast_tools, especially the helpers that smooth over
differences between Python versions' AST layouts.
"""
import ast
import unittest

from pedal.utilities.ast_tools import (is_literal, is_constant_node, get_constant_value,
                                       is_index_subscript, is_slice_subscript,
                                       is_extslice_subscript)


def parse_expression(code):
    return ast.parse(code).body[0].value


class TestConstantHelpers(unittest.TestCase):
    CONSTANTS = {
        '5': 5,
        '5.5': 5.5,
        '5j': 5j,
        '"hello"': "hello",
        'b"bytes"': b"bytes",
        'True': True,
        'False': False,
        'None': None,
        '...': Ellipsis,
    }

    def test_is_constant_node(self):
        for code in self.CONSTANTS:
            self.assertTrue(is_constant_node(parse_expression(code)), code)
        for code in ['x', '[1]', '(1, 2)', '{1: 2}', '-1', 'f"{x}"', 'x[0]']:
            self.assertFalse(is_constant_node(parse_expression(code)), code)

    def test_get_constant_value(self):
        for code, expected in self.CONSTANTS.items():
            value = get_constant_value(parse_expression(code))
            self.assertEqual(value, expected, code)
            # Type matters too: True must not come back as 1
            self.assertIs(type(value), type(expected), code)

    def test_get_constant_value_rejects_non_constants(self):
        with self.assertRaises(TypeError):
            get_constant_value(parse_expression('x'))

    def test_is_literal_constants(self):
        for code in self.CONSTANTS:
            self.assertTrue(is_literal(parse_expression(code)), code)

    def test_is_literal_containers(self):
        self.assertTrue(is_literal(parse_expression('[1, "a", None]')))
        self.assertTrue(is_literal(parse_expression('(1, 2.0)')))
        self.assertTrue(is_literal(parse_expression('{1, 2}')))
        self.assertTrue(is_literal(parse_expression('{"a": 1, "b": [2]}')))
        self.assertFalse(is_literal(parse_expression('[1, x]')))
        self.assertFalse(is_literal(parse_expression('{"a": x}')))
        self.assertFalse(is_literal(parse_expression('{x: 1}')))

    def test_is_literal_non_literals(self):
        for code in ['x', 'x + 1', 'f(1)', 'x[0]', '[y for y in z]']:
            self.assertFalse(is_literal(parse_expression(code)), code)


class TestSubscriptHelpers(unittest.TestCase):
    def test_index_subscripts(self):
        for code in ['a[0]', 'a["key"]', 'a[x]', 'a[1, 2]', 'a[-1]', 'a[b[0]]', 'a[0][1]']:
            node = parse_expression(code)
            self.assertTrue(is_index_subscript(node), code)
            self.assertFalse(is_slice_subscript(node), code)
            self.assertFalse(is_extslice_subscript(node), code)

    def test_slice_subscripts(self):
        for code in ['a[1:2]', 'a[:]', 'a[::2]', 'a[1:]', 'a[:-1]']:
            node = parse_expression(code)
            self.assertTrue(is_slice_subscript(node), code)
            self.assertFalse(is_index_subscript(node), code)
            self.assertFalse(is_extslice_subscript(node), code)

    def test_extslice_subscripts(self):
        for code in ['a[1:2, 3]', 'a[:, 0]', 'a[1:2, 3:4]']:
            node = parse_expression(code)
            self.assertTrue(is_extslice_subscript(node), code)
            self.assertFalse(is_index_subscript(node), code)
            self.assertFalse(is_slice_subscript(node), code)

    def test_non_subscripts(self):
        for code in ['a', 'a.b', 'a(0)', '[0]', '0']:
            node = parse_expression(code)
            self.assertFalse(is_index_subscript(node), code)
            self.assertFalse(is_slice_subscript(node), code)
            self.assertFalse(is_extslice_subscript(node), code)


if __name__ == '__main__':
    unittest.main()
