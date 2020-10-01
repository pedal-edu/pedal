"""
Utilities for working with Abstract Syntax Trees.
"""
import ast

__all__ = ['is_literal', 'FindExecutableLines']

AST_NODE_NAMES = {
    "Add": "an addition operator",
    "And": "a boolean AND operator",
    "AnnAssign": "an annotated assignment",
    "Assert": "an assert statement",
    "Assign": "an assignment statement",
    "AsyncFor": "an asychronous for loop",
    "AsyncFunctionDef": "an asychronous function definition",
    "AsyncWith": "an asychronous with statement",
    "Attribute": "an attribute lookup",
    "AugAssign": "an augmented assignment",
    "AugLoad": "an augmented load",
    "AugStore": "an augmented store",
    "Await": "an await statement",
    "BinOp": "a binary operator",
    "BitAnd": "a bitwise AND operator",
    "BitOr": "a bitwise OR operator",
    "BitXor": "a bitwise XOR operator",
    "BoolOp": "a boolean operator",
    "Break": "a break statement",
    "Bytes": "a literal bytes string",
    "Call": "a function call",
    "ClassDef": "a class definition",
    "Compare": "a boolean comparison",
    "Constant": "a literal value",
    "Continue": "a continue statement",
    "Del": "a delete statement",
    "Delete": "a deletion",
    "Dict": "a dictionary literal",
    "DictComp": "a dictionary comprehension",
    "Div": "a division operator",
    "Ellipsis": "an ellipsis",
    "Eq": "an equality comparison operator",
    "ExceptHandler": "an except handler",
    "Expr": "an expression used as a statement",
    "Expression": "an evaluated expression",
    "ExtSlice": "a multi-dimensional slice",
    "FloorDiv": "an integer division operator",
    "For": "a FOR loop",
    "FormattedValue": "a formatted value in an f-string",
    "FunctionDef": "a function definition",
    "GeneratorExp": "a generator expression",
    "Global": "a global statement",
    "Gt": "a greater than comparison operator",
    "GtE": "a greater than or equal to comparison operator",
    "If": "an IF statement",
    "IfExp": "an IF expression",
    "Import": "an import statement",
    "ImportFrom": "an import/from statement",
    "In": "an IN operator",
    "Index": "an index",
    "Interactive": "an interactive expression",
    "Invert": "an invert operator",
    "Is": "an IS operator",
    "IsNot": "an IS NOT operator",
    "JoinedStr": "an f-string",
    "LShift": "a left shift operator",
    "Lambda": "a lambda expression",
    "List": "a list literal",
    "ListComp": "a list comprehension",
    "Load": "a load",
    "Lt": "a less than comparison operator",
    "LtE": "a less than or equal to comparison operator",
    "MatMult": "a matrix multiplication operator",
    "Mod": "a modulo operator",
    "Module": "a module",
    "Mult": "a multiplication operator",
    "Name": "a name",
    "NameConstant": "a name constant",
    "Nonlocal": "a nonlocal statement",
    "Not": "a not operator",
    "NotEq": "a not equal to comparison operator",
    "NotIn": "a NOT IN operator",
    "Num": "a numeric literal",
    "Or": "a boolean OR operator",
    "Param": "a parameter",
    "Pass": "a pass statement",
    "Pow": "a power operator",
    "RShift": "a right shift operator",
    "Raise": "a raise statement",
    "Return": "a return statement",
    "Set": "a set literal",
    "SetComp": "a set comprehension",
    "Slice": "a slice",
    "Starred": "a starred argument",
    "Store": "a store",
    "Str": "a string literal",
    "Sub": "a subtraction operator",
    "Subscript": "a subscript",
    "Suite": "a suite",
    "Try": "a try statement",
    "Tuple": "a tuple literal",
    "TypeIgnore": " a type ignore",
    "UAdd": "a unary addition operator",
    "USub": "a unary subtraction operator",
    "UnaryOp": "a unary operator",
    "While": "a while loop",
    "With": "a with statement",
    "Yield": "a yield statement",
    "YieldFrom": "a yield/from statement"
}


def is_literal(node: ast.AST) -> bool:
    """
    Consumes an AST Node and produces whether or not it is a literal value.
    Args:
        node (AST): The AST node to check

    Returns:
        bool: Whether or not this is an AST Node
    """
    # Simple primitive constant?
    if isinstance(node, (ast.Num, ast.Str, ast.Bytes, ast.Ellipsis,
                         ast.NameConstant)):
        return True
    # V3.8 Constant?
    try:
        if isinstance(node, ast.Constant):
            return True
    except AttributeError:
        pass
    # V3.6 FormattedValue?
    try:
        if isinstance(node, ast.FormattedValue):
            return True
    except AttributeError:
        pass
    # Iterable elts?
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return all(is_literal(elt) for elt in node.elts)
    # Dictionary?
    if isinstance(node, ast.Dict):
        return all(is_literal(key) and is_literal(value)
                   for key, value in zip(node.keys, node.values))
    # Nope, not a literal
    return False


class FindExecutableLines(ast.NodeVisitor):
    """
    NodeVisitor subclass that visits every statement of a program and tracks
    their line numbers in a list.

    Attributes:
        lines (list[int]): The list of lines that were visited.
    """

    def __init__(self):
        self.lines = []

    def _track_lines(self, node):
        self.lines.append(node.lineno)
        self.generic_visit(node)

    def _track_expr_line(self, node):
        """ Skips over string Expr nodes (which are docstrings) """
        try:
            node.value.s
        except AttributeError:
            self._track_lines(node)

    visit_FunctionDef = _track_lines
    visit_AsyncFunctionDef = _track_lines
    visit_ClassDef = _track_lines
    visit_Return = _track_lines
    visit_Delete = _track_lines
    visit_Assign = _track_lines
    visit_AugAssign = _track_lines
    visit_AnnAssign = _track_lines
    visit_For = _track_lines
    visit_AsyncFor = _track_lines
    visit_While = _track_lines
    visit_If = _track_lines
    visit_With = _track_lines
    visit_AsyncWith = _track_lines
    visit_Raise = _track_lines
    visit_Try = _track_lines
    visit_Assert = _track_lines
    visit_Import = _track_lines
    visit_ImportFrom = _track_lines
    visit_Global = _track_lines
    visit_Nonlocal = _track_lines
    visit_Expr = _track_expr_line
    visit_Pass = _track_lines
    visit_Continue = _track_lines
    visit_Break = _track_lines
