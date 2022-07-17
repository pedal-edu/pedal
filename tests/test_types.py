"""
Check pedal.types
"""
import ast
import unittest
import pedal.types.new_types as types
from pedal.types.new_types import is_subtype
from pedal.types.normalize import normalize_type, get_pedal_type_from_value


class TestNormalizeType(unittest.TestCase):
    def assert_is_subtype(self, left, right):
        self.assertTrue(is_subtype(left, right.as_type()),
                        f"{left.singular_name} is (incorrectly) not a subtype of {right.singular_name}")

    def assert_is_not_subtype(self, left, right):
        self.assertFalse(is_subtype(left, right.as_type()),
                        f"{left.singular_name} is (incorrectly) a subtype of {right.singular_name}")

    def test_subtyping(self):
        self.assert_is_subtype(types.LiteralInt(5), normalize_type(int))
        self.assert_is_subtype(get_pedal_type_from_value(5), normalize_type(int))
        self.assert_is_subtype(get_pedal_type_from_value([1, 2]), normalize_type(list))
        self.assert_is_not_subtype(get_pedal_type_from_value({1:2}), normalize_type(dict))

    def test_simple_primitives(self):
        self.assertIsInstance(normalize_type(int), types.IntType)
        self.assertIsInstance(normalize_type(bool), types.BoolType)
        self.assertIsInstance(normalize_type(float), types.FloatType)
        self.assertIsInstance(normalize_type(str), types.StrType)
        self.assertIsInstance(normalize_type(list), types.ListConstructor)
        self.assertIsInstance(normalize_type(type(None)), types.NoneType)

    def test_complex_annotation(self):
        list_int = normalize_type('list[int]')
        self.assertIsInstance(list_int, types.ListConstructor)
        self.assertIsInstance(list_int.type_arguments, types.IntType)

        bad_dict = normalize_type(ast.parse('dict[int]'))
        self.assertIsInstance(bad_dict, types.ImpossibleType)

    def test_literals_normalized(self):
        self.assertIsInstance(normalize_type(5), types.LiteralInt)


if __name__ == '__main__':
    unittest.main(buffer=False)
