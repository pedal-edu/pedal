import ast

from pedal.tifa.type_definitions import (UnknownType, NumType, BoolType,
                                         TupleType, ListType, StrType,
                                         DictType, SetType, GeneratorType,
                                         DayType, TimeType)


def merge_types(left, right):
    # TODO: Check that lists/sets have the same subtypes
    if isinstance(left, (ListType, SetType, GeneratorType)):
        if left.empty:
            return right.subtype
        else:
            return left.subtype.clone()
    elif isinstance(left, TupleType):
        return left.subtypes + right.subtypes


def NumType_any(*x):
    return NumType()


def StrType_any(*x):
    return StrType()


def BoolType_any(*x):
    return BoolType()


def keep_left(left, right):
    return left


def keep_right(left, right):
    return right


VALID_BINOP_TYPES = {
    ast.Add: {NumType: {NumType: NumType_any},
              StrType: {StrType: StrType_any},
              ListType: {ListType: merge_types},
              TupleType: {TupleType: merge_types}},
    ast.Sub: {NumType: {NumType: NumType_any},
              SetType: {SetType: merge_types}},
    ast.Div: {NumType: {NumType: NumType_any}},
    ast.FloorDiv: {NumType: {NumType: NumType_any}},
    ast.Mult: {NumType: {NumType: NumType_any,
                         StrType: StrType_any,
                         ListType: keep_right,
                         TupleType: keep_right},
               StrType: {NumType: StrType_any},
               ListType: {NumType: keep_left},
               TupleType: {NumType: keep_left}},
    ast.Pow: {NumType: {NumType: NumType_any}},
    # TODO: Should we allow old-fashioned string interpolation?
    # Currently, I vote no because it makes the code harder and is bad form.
    ast.Mod: {NumType: {NumType: NumType_any}},
    ast.LShift: {NumType: {NumType: NumType_any}},
    ast.RShift: {NumType: {NumType: NumType_any}},
    ast.BitOr: {NumType: {NumType: NumType_any},
                BoolType: {NumType: NumType_any,
                           BoolType: BoolType_any},
                SetType: {SetType: merge_types}},
    ast.BitXor: {NumType: {NumType: NumType_any},
                 BoolType: {NumType: NumType_any,
                            BoolType: BoolType_any},
                 SetType: {SetType: merge_types}},
    ast.BitAnd: {NumType: {NumType: NumType_any},
                 BoolType: {NumType: NumType_any,
                            BoolType: BoolType_any},
                 SetType: {SetType: merge_types}}
}
VALID_UNARYOP_TYPES = {
    ast.UAdd: {NumType: NumType},
    ast.USub: {NumType: NumType},
    ast.Invert: {NumType: NumType}
}


def are_types_equal(left, right):
    '''
    Determine if two types are equal.

    This could be more Polymorphic - move the code for each type into
    its respective class instead.
    '''
    if left is None or right is None:
        return False
    elif isinstance(left, UnknownType) or isinstance(right, UnknownType):
        return False
    elif type(left) is not type(right):
        return False
    elif isinstance(left, (GeneratorType, ListType)):
        if left.empty or right.empty:
            return True
        else:
            return are_types_equal(left.subtype, right.subtype)
    elif isinstance(left, TupleType):
        if left.empty or right.empty:
            return True
        elif len(left.subtypes) != len(right.subtypes):
            return False
        else:
            for l, r in zip(left.subtypes, right.subtypes):
                if not are_types_equal(l, r):
                    return False
            return True
    elif isinstance(left, DictType):
        if left.empty or right.empty:
            return True
        elif left.literals is not None and right.literals is not None:
            if len(left.literals) != len(right.literals):
                return False
            else:
                for l, r in zip(left.literals, right.literals):
                    if not are_types_equal(l, r):
                        return False
                for l, r in zip(left.values, right.values):
                    if not are_types_equal(l, r):
                        return False
                return True
        elif left.literals is not None or right.literals is not None:
            return False
        else:
            keys_equal = are_types_equal(left.keys, right.keys)
            values_equal = are_types_equal(left.values, right.values)
            return keys_equal and values_equal
    else:
        return True


ORDERABLE_TYPES = (NumType, BoolType, StrType, ListType, DayType, TimeType,
                   SetType, TupleType)
INDEXABLE_TYPES = (StrType, ListType, SetType, TupleType, DictType)
