"""
Check pedal.types
"""
import ast
import unittest
import pedal.types.definitions as types
from pedal.types.normalize import normalize_type


class TestNormalizeType(unittest.TestCase):
    def test_simple_primitives(self):
        self.assertIsInstance(normalize_type(int), types.NumType)
        self.assertIsInstance(normalize_type(bool), types.BoolType)
        self.assertIsInstance(normalize_type(float), types.NumType)
        self.assertIsInstance(normalize_type(str), types.StrType)
        self.assertIsInstance(normalize_type(list), types.ListType)
        self.assertIsInstance(normalize_type(type(None)), types.NoneType)

    def test_complex_annotation(self):
        list_int = normalize_type(ast.parse('list[int]'))
        self.assertIsInstance(list_int, types.ListType)
        self.assertIsInstance(list_int.subtype, types.NumType)

        bad_dict = normalize_type(ast.parse('dict[int]'))
        self.assertIsInstance(bad_dict, types.UnknownType)

    def test_literals_not_normalized(self):
        with self.assertRaises(ValueError):
            normalize_type(5)


if __name__ == '__main__':
    unittest.main(buffer=False)
