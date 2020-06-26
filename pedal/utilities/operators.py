"""
Human-readable names for operators.
"""
import ast

OPERATION_DESCRIPTION = {
    ast.Pow: "an exponent",
    ast.Add: "an addition",
    ast.Mult: "a multiplication",
    ast.Sub: "a subtraction",
    ast.Div: "a division",
    ast.FloorDiv: "a division",
    ast.Mod: "a modulo",
    ast.LShift: "a left shift",
    ast.RShift: "a right shift",
    ast.BitOr: "a bit or",
    ast.BitAnd: "a bit and",
    ast.BitXor: "a bit xor",
    ast.And: "an and",
    ast.Or: "an or",
    ast.Eq: "an ==",
    ast.NotEq: "a !=",
    ast.Lt: "a <",
    ast.LtE: "a <=",
    ast.Gt: "a >",
    ast.GtE: "a >=",
    ast.Is: "an is",
    ast.IsNot: "an is not",
    ast.In: "an in",
    ast.NotIn: "an not in",
}

COMPARE_OP_NAMES = {
    "==": "Eq",
    "<": "Lt",
    "<=": "Lte",
    ">=": "Gte",
    ">": "Gt",
    "!=": "NotEq",
    "is": "Is",
    "is not": "IsNot",
    "in": "In",
    "not in": "NotIn",
}

BOOL_OP_NAMES = {"and": "And", "or": "Or"}

BIN_OP_NAMES = {
    "+": "Add",
    "-": "Sub",
    "*": "Mult",
    "/": "Div",
    "//": "FloorDiv",
    "%": "Mod",
    "**": "Pow",
    ">>": "LShift",
    "<<": "RShift",
    "|": "BitOr",
    "^": "BitXor",
    "&": "BitAnd",
    "@": "MatMult",
}

UNARY_OP_NAMES = {
    # "+": "UAdd",
    # "-": "USub",
    "not": "Not",
    "~": "Invert",
}
