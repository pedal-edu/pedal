import ast

from pedal.types.new_types import (AnyType, ImpossibleType,
                                   NumType, BoolType,
                                   TupleType, ListType, StrType,
                                   DictType, SetType, GeneratorType,
                                   FunctionType,
                                   InstanceType, ClassType, LiteralValue,
                                   IntType, FloatType)


def add_tuples(left, right):
    """ Literally just concatenate the types """
    return tuple(left.element_types) + tuple(right.element_types)


def add_element_container_types(left, right):
    """ Use whichever type is not empty """
    if left.is_empty:
        return right.clone()
    else:
        return left.clone()
    #return right.element_type.clone() if left.is_empty else left.element_type.clone()


def NumType_any(*x):
    """ Ignores all parameters to return a NumType """
    return NumType()


def FloatType_any(*x):
    return FloatType()


def IntType_any(*x):
    return IntType()


def StrType_any(*x):
    """ Ignores all parameters to return a StrType """
    return StrType(False)


def BoolType_any(*x):
    """ Ignores all parameters to return a BoolType """
    return BoolType()


def keep_left(left, right):
    """ Returns the left parameter """
    return left


def keep_right(left, right):
    """ Returns the right parameter """
    return right


# Maps the operations to their return types, based on the values.
# The *_any functions don't use the parameters, they return values unconditionally.
VALID_BINOP_TYPES = {
    ast.Add: {NumType: {NumType: NumType_any,
                        IntType: NumType_any,
                        FloatType: FloatType_any},
              IntType: {NumType: NumType_any,
                        IntType: IntType_any,
                        FloatType: FloatType_any},
              FloatType: {NumType: NumType_any,
                          IntType: FloatType_any,
                          FloatType: FloatType_any},
              StrType: {StrType: StrType_any},
              ListType: {ListType: add_element_container_types},
              TupleType: {TupleType: add_tuples}},
    ast.Sub: {NumType: {NumType: NumType_any,
                        IntType: NumType_any,
                        FloatType: FloatType_any},
              IntType: {NumType: NumType_any,
                        IntType: IntType_any,
                        FloatType: FloatType_any},
              FloatType: {NumType: NumType_any,
                          IntType: FloatType_any,
                          FloatType: FloatType_any},
              SetType: {SetType: add_element_container_types}},
    ast.Div: {NumType: {NumType: NumType_any,
                        IntType: NumType_any,
                        FloatType: FloatType_any},
              IntType: {NumType: NumType_any,
                        IntType: FloatType_any,
                        FloatType: FloatType_any},
              FloatType: {NumType: NumType_any,
                          IntType: FloatType_any,
                          FloatType: FloatType_any}},
    ast.FloorDiv: {NumType: {NumType: IntType_any,
                             IntType: IntType_any,
                             FloatType: IntType_any},
                   IntType: {NumType: IntType_any,
                             IntType: IntType_any,
                             FloatType: IntType_any},
                   FloatType: {NumType: IntType_any,
                               IntType: IntType_any,
                               FloatType: IntType_any}},
    ast.Mult: {NumType: {NumType: NumType_any,
                         IntType: NumType_any,
                         FloatType: NumType_any,
                         StrType: StrType_any,
                         ListType: keep_right,
                         TupleType: keep_right},
               FloatType: {NumType: NumType_any,
                           IntType: FloatType_any,
                           FloatType: FloatType_any},
               IntType: {NumType: NumType_any,
                         IntType: IntType_any,
                         FloatType: FloatType_any,
                         StrType: keep_right,
                         ListType: keep_right,
                         TupleType: keep_right},
               StrType: {NumType: keep_left,
                         IntType: keep_left},
               ListType: {NumType: keep_left},
               TupleType: {NumType: keep_left}},
    ast.Pow: {NumType: {NumType: NumType_any,
                        IntType: NumType_any,
                        FloatType: NumType_any},
              IntType: {NumType: NumType_any,
                        IntType: IntType_any,
                        FloatType: FloatType_any},
              FloatType: {NumType: NumType_any,
                          IntType: FloatType_any,
                          FloatType: FloatType_any}},
    # TODO: Should we allow old-fashioned string interpolation?
    # Currently, I vote no because it makes the code harder and is bad form.
    ast.Mod: {NumType: {NumType: NumType_any,
                        IntType: NumType_any,
                        FloatType: NumType_any},
              IntType: {NumType: NumType_any,
                        IntType: IntType_any,
                        FloatType: FloatType_any},
              FloatType: {NumType: NumType_any,
                          IntType: FloatType_any,
                          FloatType: FloatType_any}},
    ast.LShift: {NumType: {NumType: NumType_any,
                           IntType: NumType_any},
                 IntType: {NumType: NumType_any,
                           IntType: IntType_any}},
    ast.RShift: {NumType: {NumType: NumType_any,
                           IntType: NumType_any},
                 IntType: {NumType: NumType_any,
                           IntType: IntType_any}},
    ast.BitOr: {NumType: {NumType: NumType_any,
                           IntType: NumType_any},
                 IntType: {NumType: NumType_any,
                           IntType: IntType_any},
                BoolType: {NumType: NumType_any,
                           BoolType: BoolType_any},
                SetType: {SetType: add_element_container_types}},
    ast.BitXor: {NumType: {NumType: NumType_any,
                           IntType: NumType_any},
                 IntType: {NumType: NumType_any,
                           IntType: IntType_any},
                 BoolType: {NumType: NumType_any,
                            BoolType: BoolType_any},
                 SetType: {SetType: add_element_container_types}},
    ast.BitAnd: {NumType: {NumType: NumType_any,
                           IntType: NumType_any},
                 IntType: {NumType: NumType_any,
                           IntType: IntType_any},
                 BoolType: {NumType: NumType_any,
                            BoolType: BoolType_any},
                 SetType: {SetType: add_element_container_types}}
}

VALID_UNARYOP_TYPES = {
    ast.UAdd: {NumType: NumType, IntType: IntType, FloatType: FloatType},
    ast.USub: {NumType: NumType, IntType: IntType, FloatType: FloatType},
    ast.Invert: {NumType: NumType, IntType: IntType, FloatType: FloatType}
}


def apply_unary_operation(operation, operand):
    if isinstance(operation, ast.Not):
        return BoolType()
    elif isinstance(operand, AnyType):
        return AnyType()
    operand = operand.promote() if isinstance(operand, LiteralValue) else operand
    if type(operation) in VALID_UNARYOP_TYPES:
        op_lookup = VALID_UNARYOP_TYPES[type(operation)]
        if type(operand) in op_lookup:
            return op_lookup[type(operand)]()
    return ImpossibleType()


def apply_binary_operation(operation, left, right):
    if isinstance(left, AnyType):
        return right
    elif isinstance(right, AnyType):
        return left
    left = left.promote() if isinstance(left, LiteralValue) else left
    right = right.promote() if isinstance(right, LiteralValue) else right
    if type(operation) in VALID_BINOP_TYPES:
        op_lookup = VALID_BINOP_TYPES[type(operation)]
        if type(left) in op_lookup:
            op_lookup = op_lookup[type(left)]
            if type(right) in op_lookup:
                op_lookup = op_lookup[type(right)]
                result_type = op_lookup(left, right)
                return result_type
    return ImpossibleType()
