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
from pedal.types.definitions import (Type, UnknownType, NumType, BoolType,
                                     TupleType, ListType, StrType,
                                     DictType, SetType, GeneratorType,
                                     ModuleType, NoneType, FrozenSetType,
                                     FunctionType, TYPE_STRINGS,
                                     LiteralStr, LiteralNum, LiteralBool, CustomType)
from pedal.utilities.system import IS_PYTHON_39


def normalize_type(type_expression, type_space=None):
    """
    Converts the given ``type_expression`` into a normalized Pedal Type.

    Args:
        type_expression (Any): Any kind of supported "Type Expression". This
            includes builtin Python types, string representations, AST nodes,
            JSON-Encoded representations.

    Returns:
        :py:class:`pedal.types.definitions.Type`: A normalized Pedal Type.
    """
    # Already a Pedal Type
    if isinstance(type_expression, Type):
        return type_expression
    # What if it's a builtin type function?
    if isinstance(type_expression, type):
        return normalize_type(type_expression.__name__, type_space=type_space)
    # Might be a string, can we evaluate?
    if isinstance(type_expression, str):
        result = get_pedal_type_from_str(type_expression, type_space)
        if not isinstance(result, (UnknownType, CustomType)):
            return result
        try:
            first_line = ast.parse(type_expression).body[0].value
        except SyntaxError as e:
            raise ValueError(f"Could not parse string {type_expression!r} into "
                             f"a Pedal type:\n {e}")
        except AttributeError as e:
            raise ValueError(f"Could not parse string {type_expression!r} into "
                             f"a Pedal type:\n This was not an expression.")
        try:
            return normalize_type(first_line, type_space=type_space)
        except:
            return result
    # Might be a JSON-Encoded dictionary
    if isinstance(type_expression, dict):
        try:
            return get_pedal_type_from_json(type_expression)
        except KeyError:
            return get_pedal_type_from_type_literal(type_expression, type_space)
    # Perhaps it is an AST node
    if isinstance(type_expression, ast.AST):
        return get_pedal_type_from_ast(type_expression, type_space=type_space)
    if isinstance(type_expression, list):
        return get_pedal_type_from_type_literal(type_expression, type_space)
    raise ValueError(f"Could not normalize {type_expression!r} into a Pedal type.")


def get_pedal_type_from_json(val):
    """

    Args:
        val:

    Returns:

    """
    if val['type'] == 'DictType':
        values = [get_pedal_type_from_json(v) for v in val['values']]
        empty = val.get('empty', None)
        if 'literals' in val:
            literals = [get_pedal_literal_from_json(l) for l in val['literals']]
            return DictType(empty, literals=literals, values=values)
        else:
            keys = [get_pedal_type_from_json(k) for k in val['keys']]
            return DictType(empty, keys=keys, values=values)
    elif val['type'] == 'ListType':
        return ListType(get_pedal_type_from_json(val.get('subtype', None)),
                        val.get('empty', None))
    elif val['type'] == 'StrType':
        return StrType(val.get('empty', None))
    elif val['type'] == 'BoolType':
        return BoolType()
    elif val['type'] == 'NoneType':
        return NoneType()
    elif val['type'] == 'NumType':
        return NumType()
    elif val['type'] == 'ModuleType':
        submodules = {name: get_pedal_type_from_json(m)
                      for name, m in val.get('submodules', {}).items()}
        fields = {name: get_pedal_type_from_json(m)
                  for name, m in val.get('fields', {}).items()}
        return ModuleType(name=val.get('name'), submodules=submodules,
                          fields=fields)
    elif val['type'] == 'FunctionType':
        returns = get_pedal_type_from_json(val.get('returns', {'type': 'NoneType'}))
        return FunctionType(name=val.get('name'), returns=returns)


def get_pedal_literal_from_json(val):
    """

    Args:
        val:

    Returns:

    """
    if val['type'] == 'LiteralStr':
        return LiteralStr(val['value'])
    elif val['type'] == 'LiteralNum':
        return LiteralNum(val['value'])
    elif val['type'] == 'LiteralBool':
        return LiteralBool(val['value'])


def get_pedal_literal_from_pedal_type(type):
    """

    Args:
        type:

    Returns:

    """
    if isinstance(type, NumType):
        return LiteralNum(0)
    elif isinstance(type, StrType):
        return LiteralStr("")
    else:
        # TODO: Finish the mapping
        return LiteralStr("")


def get_pedal_type_from_str(value, tifa_instance=None):
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
    elif tifa_instance:
        variable = tifa_instance.find_variable_scope(value)
        if variable.exists:
            state = tifa_instance.load_variable(value)
            return state.type
        # custom_types.add(value)
    return CustomType(value)
    # TODO: handle custom types


def get_pedal_type_from_annotation(v, tifa_instance=None):
    """

    Attempts to intelligently parse the type, which might be a variable or
    a string node.

    Args:
        v:
        tifa_instance:

    Returns:

    """
    if isinstance(v, ast.Str):
        return get_pedal_type_from_str(v.s, tifa_instance)
    elif isinstance(v, ast.Name):
        return get_pedal_type_from_str(v.id, tifa_instance)
    # Fall back to default AST behavior
    return get_pedal_type_from_ast(v, tifa_instance)


def get_pedal_type_from_value(value, type_space=None) -> Type:
    """ Converts the Python value to a Pedal Type """
    if isinstance(value, bool):
        return BoolType()
    if isinstance(value, (int, float, complex)):
        return NumType()
    if isinstance(value, str):
        return StrType()
    if isinstance(value, type(None)):
        return NoneType()
    if isinstance(value, tuple):
        return TupleType((get_pedal_type_from_value(t, type_space) for t in value))
    if isinstance(value, set):
        return SetType((get_pedal_type_from_value(t, type_space) for t in value))
    if isinstance(value, frozenset):
        return FrozenSetType((get_pedal_type_from_value(t, type_space) for t in value))
    if isinstance(value, list):
        if value:
            return ListType(empty=False, subtype=get_pedal_type_from_value(value[0]))
        else:
            return ListType(empty=True)
    if isinstance(value, dict):
        if not value:
            return DictType(empty=True)
        if all(isinstance(value, str) for k in value.keys()):
            return DictType(literals=[LiteralStr(s) for s in value.keys()],
                            values=[get_pedal_type_from_value(vv, type_space)
                                    for vv in value.values()])
        return DictType(keys=[get_pedal_type_from_ast(k, type_space)
                              for k in value.keys()],
                        values=[get_pedal_type_from_ast(vv, type_space)
                                for vv in value.values()])
    return UnknownType()


def get_pedal_type_from_ast(value: ast.AST, type_space=None) -> Type:
    """
    Determines the Pedal Type from this ast node.
    Args:
        value (ast.AST): An AST node.

    Returns:
        Type: A Pedal Type
    """
    try:
        if isinstance(value, ast.Constant):
            return get_pedal_type_from_value(value.value, type_space)
    except AttributeError as e:
        pass
    if isinstance(value, ast.Name):
        return get_pedal_type_from_str(value.id, type_space)
    elif isinstance(value, ast.Str):
        return StrType(bool(value.s))
    elif isinstance(value, ast.List):
        return ListType(subtype=(get_pedal_type_from_ast(value.elts[0], type_space)
                                 if value.elts else None),
                        empty=not bool(value.elts))
    elif isinstance(value, ast.Set):
        return SetType(subtype=(get_pedal_type_from_ast(value.elts[0], type_space)
                                if value.elts else None),
                       empty=not bool(value.elts))
    elif isinstance(value, ast.Tuple):
        return TupleType(subtypes=[get_pedal_type_from_ast(e, type_space)
                                   for e in value.elts])
    elif isinstance(value, ast.Dict):
        if not value.keys:
            return DictType(empty=True)
        if all(isinstance(k, ast.Str) for k in value.keys):
            return DictType(literals=[LiteralStr(s.s) for s in value.keys],
                            values=[get_pedal_type_from_ast(vv, type_space)
                                    for vv in value.values])
        return DictType(keys=[get_pedal_type_from_ast(k, type_space)
                              for k in value.keys],
                        values=[get_pedal_type_from_ast(vv, type_space)
                                for vv in value.values])
    # Support new style subscripts (e.g., ``list[int]``)
    elif ((IS_PYTHON_39 and isinstance(value, ast.Subscript)) or
          isinstance(value, ast.Subscript) and isinstance(value.slice, ast.Index)):
        if IS_PYTHON_39:
            slice = value.slice
        else:
            slice = value.slice.value
        if isinstance(value.value, ast.Name):
            if isinstance(slice, ast.Name):
                subtype = get_pedal_type_from_str(slice.id)
                if value.value.id == "list":
                    return ListType(subtype=subtype, empty=False)
                if value.value.id == "set":
                    return SetType(subtype=subtype, empty=False)
                if value.value.id == "tuple":
                    return TupleType(subtypes=(subtype,))
                if value.value.id == "frozenset":
                    return FrozenSetType(subtype=subtype, empty=False)
            elif isinstance(slice, ast.Tuple):
                subtypes = [get_pedal_type_from_ast(e, type_space)
                            for e in slice.elts]
                if value.value.id == "tuple":
                    return TupleType(subtypes=subtypes)
                elif value.value.id == "dict" and len(subtypes) == 2:
                    return DictType(keys=subtypes[0], values=subtypes[1])
    # Top-level Module, parse it and get it back
    if isinstance(value, ast.Module) and value.body:
        if isinstance(value.body[0], ast.Expr):
            return get_pedal_type_from_ast(value.body[0].value, type_space)
    return UnknownType()


def get_pedal_type_from_type_literal(value, type_space=None) -> Type:
    if value == list:
        return ListType(empty=False)
    elif value == dict:
        return DictType(empty=False)
    elif isinstance(value, list):
        if value:
            return ListType(empty=False, subtype=get_pedal_type_from_type_literal(value[0], type_space))
        else:
            return ListType(empty=True)
    elif isinstance(value, dict):
        if not value:
            return DictType(empty=True)
        if all(isinstance(value, str) for k in value.keys()):
            return DictType(literals=[LiteralStr(s) for s in value.keys()],
                            values=[get_pedal_type_from_type_literal(vv, type_space)
                                    for vv in value.values()])
        return DictType(keys=[get_pedal_type_from_type_literal(k, type_space)
                              for k in value.keys()],
                        values=[get_pedal_type_from_type_literal(vv, type_space)
                                for vv in value.values()])
    elif isinstance(value, type):
        return get_pedal_type_from_str(value.__name__)
    else:
        return get_pedal_type_from_str(str(value))
