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
        self.assert_is_subtype(get_pedal_type_from_value({1:2}), normalize_type(dict))

        # Now do not trues
        self.assert_is_not_subtype(get_pedal_type_from_value(5), normalize_type(str))
        self.assert_is_not_subtype(get_pedal_type_from_value(5), normalize_type(list))
        self.assert_is_not_subtype(get_pedal_type_from_value(5), normalize_type(dict))

        self.assert_is_not_subtype(get_pedal_type_from_value([1, 2]), normalize_type(str))
        self.assert_is_not_subtype(get_pedal_type_from_value([1, 2]), normalize_type(int))
        self.assert_is_not_subtype(get_pedal_type_from_value([1, 2]), normalize_type(dict))

        self.assert_is_not_subtype(get_pedal_type_from_value({1:2}), normalize_type(str))
        self.assert_is_not_subtype(get_pedal_type_from_value({1:2}), normalize_type(int))
        self.assert_is_not_subtype(get_pedal_type_from_value({1:2}), normalize_type(list))

    def test_simple_primitives(self):
        self.assertIsInstance(normalize_type(int), types.IntType)
        self.assertIsInstance(normalize_type(bool), types.BoolType)
        self.assertIsInstance(normalize_type(float), types.FloatType)
        self.assertIsInstance(normalize_type(str), types.StrType)
        self.assertIsInstance(normalize_type(list), types.ListConstructor)
        self.assertIsInstance(normalize_type(dict), types.DictConstructor)
        self.assertIsInstance(normalize_type(type(None)), types.NoneType)

    def test_complex_annotation(self):
        list_generic = normalize_type('list')
        self.assertIsInstance(list_generic, types.ListConstructor)
        self.assert_is_subtype(get_pedal_type_from_value([1, 2]), list_generic)
        self.assert_is_subtype(get_pedal_type_from_value(["hello", "world"]), list_generic)
        self.assert_is_not_subtype(get_pedal_type_from_value(5), list_generic)

        list_int = normalize_type('list[int]')
        self.assertIsInstance(list_int, types.ListConstructor)
        self.assertIsInstance(list_int.type_arguments, types.IntType)
        self.assert_is_subtype(get_pedal_type_from_value([1, 2]), list_int)
        self.assert_is_not_subtype(get_pedal_type_from_value(["hello", "world"]), list_int)
        self.assert_is_not_subtype(get_pedal_type_from_value(5), list_int)

        dict_generic = normalize_type('dict')
        self.assertIsInstance(dict_generic, types.DictConstructor)
        self.assert_is_subtype(get_pedal_type_from_value({1: 2}), dict_generic)
        self.assert_is_subtype(get_pedal_type_from_value({1: "hello"}), dict_generic)
        self.assert_is_not_subtype(get_pedal_type_from_value([1, 2]), dict_generic)

        bad_dict = normalize_type(ast.parse('dict[int]'))
        self.assertIsInstance(bad_dict, types.DictConstructor)
        self.assertIsInstance(bad_dict.type_arguments, types.IntType)

        dict_int_str = normalize_type('dict[int, str]')
        self.assertIsInstance(dict_int_str, types.DictConstructor)
        key_type = dict_int_str.type_arguments.index(0)
        value_type = dict_int_str.type_arguments.index(1)
        self.assertIsInstance(key_type, types.IntType)
        self.assertIsInstance(value_type, types.StrType)
        self.assert_is_subtype(get_pedal_type_from_value({1: 'hello'}), dict_int_str)
        self.assert_is_subtype(get_pedal_type_from_value({1: 'hello', 2: 'world'}), dict_int_str)
        self.assert_is_not_subtype(get_pedal_type_from_value({1: 2}), dict_int_str)
        self.assert_is_not_subtype(get_pedal_type_from_value({1: "hello", "world": 2}), dict_int_str)



    def test_literals_normalized(self):
        self.assertIsInstance(normalize_type(5), types.LiteralInt)


    def test_complex_dims(self):
        nested_dict = normalize_type('dict[int, dict[int, str]]')
        self.assertIsInstance(nested_dict, types.DictConstructor)
        key_type = nested_dict.type_arguments.index(0)
        value_type = nested_dict.type_arguments.index(1)
        self.assertIsInstance(key_type, types.IntType)
        self.assertIsInstance(value_type, types.DictConstructor)
        inner_key_type = value_type.type_arguments.index(0)
        inner_value_type = value_type.type_arguments.index(1)
        self.assertIsInstance(inner_key_type, types.IntType)
        self.assertIsInstance(inner_value_type, types.StrType)

        self.assert_is_subtype(get_pedal_type_from_value({1: {2: 'hello'}}), nested_dict)
        self.assert_is_not_subtype(get_pedal_type_from_value({1: {"Ooops": 'hello'}}), nested_dict)

    def test_slice_style_dict(self):
        nested_dict = normalize_type('dict[int: dict[int: str]]')
        self.assertIsInstance(nested_dict, types.DictConstructor)
        key_type = nested_dict.type_arguments.index(0)
        value_type = nested_dict.type_arguments.index(1)
        self.assertIsInstance(key_type, types.IntType)
        self.assertIsInstance(value_type, types.DictConstructor)
        inner_key_type = value_type.type_arguments.index(0)
        inner_value_type = value_type.type_arguments.index(1)
        self.assertIsInstance(inner_key_type, types.IntType)
        self.assertIsInstance(inner_value_type, types.StrType)

        self.assert_is_subtype(get_pedal_type_from_value({1: {2: 'hello'}}), nested_dict)
        self.assert_is_not_subtype(get_pedal_type_from_value({1: {"Ooops": 'hello'}}), nested_dict)


if __name__ == '__main__':
    unittest.main(buffer=False)
