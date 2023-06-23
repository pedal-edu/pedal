"""
Utility function for taking various kinds of "type expressions" and turning
them into a canonical Pedal type.

* Pedal Type
* Python builtin type (e.g., `list`, `int`)
    get_pedal_type_from_builtin
* Python literal value (e.g., `5`, `"Hello World!"`)
    get_pedal_type_from_value
* AST Nodes (e.g., `ast.Num`)
    get_pedal_type_from_ast
* JSON-Encoded representation of a type (e.g., from CORGIS datasets)
    get_pedal_type_from_json
* String representation of parseable Python code
    get_pedal_type_from_str
* Python Typing module type (e.g., `List`, `Generic`)
    TODO: Implement get_pedal_type_from_typing
"""
import ast

from pedal.types.new_types import (Type, AnyType, ImpossibleType, NumType, BoolType,
                                   TupleType, ListType, StrType,
                                   DictType, SetType, GeneratorType,
                                   ModuleType, NoneType, FrozenSetType,
                                   FunctionType, TYPE_STRINGS,
                                   LiteralStr, LiteralInt, LiteralFloat, LiteralBool, ClassType, InstanceType,
                                   widest_type, LiteralValue, TypeUnion, PEDAL_TYPE_NAMES, specify_subtype)
from pedal.utilities.system import IS_AT_LEAST_PYTHON_39

import types as dynamic_python_types

try:
    from dataclasses import fields
except:
    fields = None


def get_generic_type(type_expression, evaluate_name=None) -> Type:
    if not hasattr(type_expression, '__args__'):
        return TYPE_STRINGS[type_expression.__name__]()
    base_type = TYPE_STRINGS[type_expression.__name__]()
    arg_type = type_expression.__args__
    arg_type = tuple((normalize_type(at, evaluate_name) for at in arg_type))
    base_type.add_type_arguments(arg_type)
    return base_type


def unbox_sandbox_if_needed(value):
    """ TODO: Redefined here to avoid imports. Need a better solution! """
    if hasattr(value, "__actual_class__"):
        if value.__actual_class__.__name__ == 'SandboxResult':
            return value._actual_value
    return value


def normalize_type(type_expression, evaluate_name=None) -> Type:
    """
    Converts the given ``type_expression`` into a normalized Pedal Type.

    Args:
        type_expression (Any): Any kind of supported "Type Expression". This
            includes builtin Python types, string representations, AST nodes,
            JSON-Encoded representations.

    Returns:
        :py:class:`pedal.types.new_types.Type`: A normalized Pedal Type.
    """
    # Already a Pedal Type
    if isinstance(type_expression, str) and type_expression in PEDAL_TYPE_NAMES:
        return PEDAL_TYPE_NAMES[type_expression]()
    if isinstance(type_expression, Type):
        return type_expression
    # What if it's a builtin type function?
    if isinstance(type_expression, type) or (IS_AT_LEAST_PYTHON_39 and isinstance(type_expression, dynamic_python_types.GenericAlias)):
        if type_expression.__name__ in TYPE_STRINGS:
            return get_generic_type(type_expression, evaluate_name)
        if evaluate_name:
            type_object = unbox_sandbox_if_needed(evaluate_name(type_expression.__name__))
            if isinstance(type_object, type) or (IS_AT_LEAST_PYTHON_39 and isinstance(type_object, dynamic_python_types.GenericAlias)):
                if fields and hasattr(type_object, '__dataclass_fields__'):
                    return ClassType(type_object.__name__, {
                        field.name: normalize_type(field.type, evaluate_name)
                        for field in fields(type_object)
                    })
                # TODO: Fix this ugly ugly hack!
                try:
                    vars(type_object)
                    has_vars = True
                except:
                    has_vars = False
                if has_vars:
                    return ClassType(type_object.__name__, {
                        f: normalize_type(v, evaluate_name)
                        for f, v in vars(type_object).items()
                        if not f.startswith('___')
                    })
                return ClassType(type_object.__name__, {})
            return type_object
        return normalize_type(type_expression.__name__, evaluate_name=evaluate_name)
    # Might be a string, can we evaluate?
    if isinstance(type_expression, str):
        # return get_pedal_type_from_str(type_expression, evaluate_name)
        try:
            first_line = ast.parse(type_expression).body[0].value
        except SyntaxError as e:
            raise ValueError(f"Could not parse string {type_expression!r} into "
                             f"a Pedal type:\n {e}")
        except AttributeError as e:
            raise ValueError(f"Could not parse string {type_expression!r} into "
                             f"a Pedal type:\n This was not an expression.")
        try:
            return normalize_type(first_line, evaluate_name=evaluate_name)
        except:
            return ImpossibleType()
    # Might be a JSON-Encoded dictionary
    if isinstance(type_expression, dict):
        try:
            return get_pedal_type_from_json(type_expression, evaluate_name)
        except KeyError:
            return get_pedal_type_from_type_literal(type_expression, evaluate_name)
    # Perhaps it is an AST node
    if isinstance(type_expression, ast.AST):
        return get_pedal_type_from_ast(type_expression, evaluate_name)
    if isinstance(type_expression, (set, list, tuple, frozenset)):
        return get_pedal_type_from_type_literal(type_expression, evaluate_name)
    if isinstance(type_expression, dynamic_python_types.ModuleType):
        return ModuleType(type_expression.__name__, {
            field: normalize_type(getattr(type_expression, field), evaluate_name)
            for field in dir(type_expression)
            if not field.startswith('__')
        })
    return get_pedal_type_from_value(type_expression)
    # raise ValueError(f"Could not normalize {type_expression!r} into a Pedal type.")


def get_pedal_type_from_json(val, evaluate_name=None):
    if 'version' in val:
        if val['version'] == 2:
            return get_pedal_type_from_json_v2(val, evaluate_name)
    return get_pedal_type_from_json_v1(val, evaluate_name)


def get_pedal_type_from_json_v2(val, evaluate_name=None):
    """ TODO: Finish v2 to make this cleaner """
    return get_pedal_type_from_json_v1(val, evaluate_name)


def get_pedal_type_from_json_v1(val, evaluate_name=None):
    if val['type'] == 'LiteralStr':
        return LiteralStr(val['value'])
    elif val['type'] == 'LiteralNum':
        if isinstance(val['value'], int):
            return LiteralInt(val['value'])
        else:
            return LiteralFloat(val['value'])
    elif val['type'] == 'LiteralBool':
        return LiteralBool(val['value'])
    elif val['type'] == 'DictType':
        values = [get_pedal_type_from_json_v1(v, evaluate_name)
                  for v in val['values']]
        if 'literals' in val:
            keys = [get_pedal_type_from_json_v1(l, evaluate_name)
                    for l in val['literals']]
        else:
            keys = [get_pedal_type_from_json_v1(k, evaluate_name)
                    for k in val['keys']]
        return DictType([(k, v) for k, v in zip(keys, values)])
    elif val['type'] == 'ListType':
        return ListType(val.get('empty', None),
                        get_pedal_type_from_json_v1(val.get('subtype', None),
                                                    evaluate_name))
    elif val['type'] == 'StrType':
        return StrType(val.get('empty', None))
    elif val['type'] == 'BoolType':
        return BoolType()
    elif val['type'] == 'NoneType':
        return NoneType()
    elif val['type'] == 'NumType':
        return NumType()
    elif val['type'] == 'ModuleType':
        submodules = {name: get_pedal_type_from_json_v1(m, evaluate_name)
                      for name, m in val.get('submodules', {}).items()}
        fields = {name: get_pedal_type_from_json_v1(m, evaluate_name)
                  for name, m in val.get('fields', {}).items()}
        return ModuleType(name=val.get('name'), submodules=submodules,
                          fields=fields)
    elif val['type'] == 'FunctionType':
        returns = get_pedal_type_from_json_v1(val.get('returns', {'type': 'NoneType'}),
                                              evaluate_name)
        return FunctionType(name=val.get('name'), returns=lambda: returns)


def get_pedal_type_from_str(value, evaluate_name=None):
    """

    Args:
        value:
        tifa_instance:

    Returns:

    """
    # if value in custom_types:
    #    return custom_types[value]
    if value.lower() in TYPE_STRINGS:
        return TYPE_STRINGS[value.lower()]()
    elif evaluate_name:
        potential = normalize_type(evaluate_name(value), evaluate_name)
        if not isinstance(potential, ImpossibleType):
            return potential
    return ClassType(value)
    # TODO: handle custom types


ELEMENT_TYPES = {
    set: SetType, list: ListType, frozenset: FrozenSetType
}


def get_pedal_type_from_value(value, evaluate_name=None) -> Type:
    """ Converts the Python value to a Pedal Type """
    if isinstance(value, bool):
        return LiteralBool(value)
    if isinstance(value, int):
        return LiteralInt(value)
    if isinstance(value, float):
        return LiteralFloat(value)
    if isinstance(value, complex):
        return NumType()
    if isinstance(value, str):
        return LiteralStr(value)
    if isinstance(value, type(None)):
        return NoneType()
    if isinstance(value, tuple):
        return TupleType((get_pedal_type_from_value(t, evaluate_name) for t in value))
    if isinstance(value, (list, set, frozenset)):
        container_type = ELEMENT_TYPES.get(type(value), ListType)
        if value:
            element_type = widest_type([get_pedal_type_from_value(v, evaluate_name)
                                        for v in value])
            if element_type is not None:
                return container_type(False, element_type)
            else:
                return container_type(False, get_pedal_type_from_value(value[0], evaluate_name))
        else:
            return container_type(True)
    if isinstance(value, dict):
        if not value:
            return DictType([])
        # All literal keys
        items = [(get_pedal_type_from_value(key, evaluate_name),
                  get_pedal_type_from_value(value, evaluate_name))
                 for key, value in value.items()]
        if all(isinstance(k, LiteralValue) for k, _ in items):
            return DictType(list(items))
        # Find the widest possible single type
        first_key = widest_type([k for k, _ in items])
        first_value = widest_type([v for _, v in items])
        if first_key is not None and first_value is not None:
            return DictType([(first_key, first_value)])
        else:
            # Resort to just matching the types?
            return DictType([(k, v) for k, v in items])
    if evaluate_name:
        new_instance = InstanceType(normalize_type(evaluate_name(type(value).__name__), evaluate_name))
        if fields and hasattr(value, '__dataclass_fields__'):
            for field in fields(value):
                new_instance.add_attr(field.name, get_pedal_type_from_value(getattr(value, field.name), evaluate_name))
        return new_instance
    return AnyType()


def get_pedal_type_from_ast(value: ast.AST, evaluate_name=None) -> Type:
    """
    Determines the Pedal Type from this ast node.
    Args:
        value (ast.AST): An AST node.

    Returns:
        Type: A Pedal Type
    """
    try:
        if isinstance(value, ast.Constant):
            return get_pedal_type_from_value(value.value, evaluate_name)
    except AttributeError as e:
        pass
    if isinstance(value, ast.Name):
        return get_pedal_type_from_str(value.id, evaluate_name)
    elif isinstance(value, ast.Str):
        return LiteralStr(value.s)
    elif isinstance(value, ast.List):
        return ListType(not bool(value.elts),
                        (get_pedal_type_from_ast(value.elts[0], evaluate_name)
                         if value.elts else None))
    elif isinstance(value, ast.Set):
        return SetType(not bool(value.elts),
                       (get_pedal_type_from_ast(value.elts[0], evaluate_name)
                        if value.elts else None))
    elif isinstance(value, ast.Tuple):
        return TupleType([get_pedal_type_from_ast(e, evaluate_name)
                           for e in value.elts])
    elif isinstance(value, ast.Dict):
        if not value.keys:
            return DictType([])
        return DictType([(get_pedal_type_from_ast(k, evaluate_name),
                          get_pedal_type_from_ast(v, evaluate_name))
                         for k, v in zip(value.keys, value.values)])
    # Support new style subscripts (e.g., ``list[int]``)
    elif ((IS_AT_LEAST_PYTHON_39 and isinstance(value, ast.Subscript)) or
          isinstance(value, ast.Subscript) and isinstance(value.slice, ast.Index)):
        if IS_AT_LEAST_PYTHON_39:
            slice = value.slice
        else:
            slice = value.slice.value
        slice_type = get_pedal_type_from_ast(slice, evaluate_name)
        value_type = get_pedal_type_from_ast(value.value, evaluate_name)
        result = value_type.index(slice_type)
        if isinstance(slice, ast.Slice):
            return value_type.shallow_clone()
        else:
            return result
    # Top-level Module, parse it and get it back
    if isinstance(value, ast.Module) and value.body:
        if isinstance(value.body[0], ast.Expr):
            return get_pedal_type_from_ast(value.body[0].value, evaluate_name)
    if isinstance(value, ast.Expr):
        return get_pedal_type_from_ast(value.value, evaluate_name)
    return ImpossibleType()


def get_pedal_type_from_type_literal(value, evaluate_name=None) -> Type:
    if value == list:
        # Handle type annotations if available
        return ListType(False)
    elif value == dict:
        return DictType(False)
    elif isinstance(value, list):
        if value:
            return ListType(False, normalize_type(value[0], evaluate_name))
        else:
            return ListType(True)
    elif isinstance(value, (set, frozenset)):
        return TypeUnion([normalize_type(v, evaluate_name) for v in value])
    elif isinstance(value, tuple):
        return TupleType([normalize_type(v, evaluate_name) for v in value])
    elif isinstance(value, dict):
        if not value:
            return DictType(True)
        if all(isinstance(value, str) for k in value.keys()):
            return DictType([(LiteralStr(s), normalize_type(vv, evaluate_name))
                            for s, vv in value.items()])
        return DictType([(normalize_type(kk, evaluate_name),
                          normalize_type(vv, evaluate_name))
                         for kk, vv in value.items()])
