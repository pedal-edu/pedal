"""
Utilities for working with Abstract Syntax Trees.
"""
import ast

from pedal.utilities.system import IS_AT_LEAST_PYTHON_38, IS_AT_LEAST_PYTHON_39, IS_SKULPT

__all__ = ['is_literal', 'FindExecutableLines',
           'is_constant_node', 'get_constant_value',
           'is_index_subscript', 'is_extslice_subscript', 'is_slice_subscript']

# Python 3.8 folded ``Num``, ``Str``, ``Bytes``, ``NameConstant`` and ``Ellipsis``
# into ``ast.Constant``; Python 3.14 removed the old classes outright (and 3.12/3.13
# warn whenever they are touched). We therefore only look the legacy classes up on
# interpreters that actually still produce them (pre-3.8 CPython and Skulpt).
USES_LEGACY_CONSTANT_NODES = not IS_AT_LEAST_PYTHON_38 or IS_SKULPT


def _legacy_nodes(*names):
    """ Collect whichever of the deprecated AST classes still exist, or nothing on modern Pythons. """
    if not USES_LEGACY_CONSTANT_NODES:
        return ()
    return tuple(getattr(ast, name) for name in names if hasattr(ast, name))


LEGACY_NUM_NODES = _legacy_nodes('Num')
LEGACY_STR_NODES = _legacy_nodes('Str', 'Bytes')
LEGACY_NAME_CONSTANT_NODES = _legacy_nodes('NameConstant')
LEGACY_ELLIPSIS_NODES = _legacy_nodes('Ellipsis')
LEGACY_CONSTANT_NODES = (LEGACY_NUM_NODES + LEGACY_STR_NODES +
                         LEGACY_NAME_CONSTANT_NODES + LEGACY_ELLIPSIS_NODES)
# ``ast.Constant`` has existed since 3.6, but Skulpt may not provide it.
_CONSTANT_NODE = getattr(ast, 'Constant', None)
CONSTANT_NODES = ((_CONSTANT_NODE,) if _CONSTANT_NODE is not None else ()) + LEGACY_CONSTANT_NODES

# Python 3.9 removed the ``Index`` and ``ExtSlice`` wrapper nodes: a Subscript's
# ``slice`` field now holds the index expression (or a Slice/Tuple) directly.
USES_LEGACY_SUBSCRIPTS = not IS_AT_LEAST_PYTHON_39 or IS_SKULPT


def is_constant_node(node) -> bool:
    """
    Determines whether the node is a literal constant (number, string, bytes,
    boolean, None, or Ellipsis), regardless of the Python version's AST layout.

    Args:
        node (ast.AST): The AST node to check.

    Returns:
        bool: Whether this node is a constant.
    """
    return isinstance(node, CONSTANT_NODES)


def get_constant_value(node):
    """
    Retrieves the Python value held by a constant node, regardless of the
    Python version's AST layout (``ast.Constant`` vs the legacy
    ``Num``/``Str``/``Bytes``/``NameConstant``/``Ellipsis`` classes).

    Args:
        node (ast.AST): A constant AST node (see :func:`is_constant_node`).

    Returns:
        Any: The literal Python value.

    Raises:
        TypeError: If the node is not a constant node.
    """
    if _CONSTANT_NODE is not None and isinstance(node, _CONSTANT_NODE):
        return node.value
    if isinstance(node, LEGACY_NUM_NODES):
        return node.n
    if isinstance(node, LEGACY_STR_NODES):
        return node.s
    if isinstance(node, LEGACY_NAME_CONSTANT_NODES):
        return node.value
    if isinstance(node, LEGACY_ELLIPSIS_NODES):
        return Ellipsis
    raise TypeError(f"Expected a constant AST node, but got {type(node).__name__}")


def _is_extslice_expression(slice_node) -> bool:
    """ A tuple of dimensions where at least one dimension is a slice (``a[1:2, 3]``). """
    return (isinstance(slice_node, ast.Tuple) and
            any(isinstance(dim, ast.Slice) for dim in slice_node.elts))


def is_slice_subscript(node) -> bool:
    """ Whether the node is a Subscript performing a simple slice (``a[1:2]``). """
    return isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Slice)


def is_extslice_subscript(node) -> bool:
    """
    Whether the node is a Subscript performing a multi-dimensional slice
    (``a[1:2, 3]``), which older Pythons represented with an ``ExtSlice`` node.
    """
    if not isinstance(node, ast.Subscript):
        return False
    if USES_LEGACY_SUBSCRIPTS:
        return isinstance(node.slice, ast.ExtSlice)
    return _is_extslice_expression(node.slice)


def is_index_subscript(node) -> bool:
    """
    Whether the node is a Subscript performing a plain index (``a[0]``,
    ``d["key"]``, ``a[1, 2]``) rather than a slice. Older Pythons represented
    this with an ``Index`` node wrapping the expression; 3.9+ stores the
    expression directly in the Subscript's ``slice`` field.
    """
    if not isinstance(node, ast.Subscript):
        return False
    if USES_LEGACY_SUBSCRIPTS:
        return isinstance(node.slice, ast.Index)
    return not (isinstance(node.slice, ast.Slice) or _is_extslice_expression(node.slice))

AST_NODE_NAMES = {
    "Add": "an addition operator",
    "And": "a boolean AND operator",
    "AnnAssign": "an annotated assignment",
    "Assert": "an assert statement",
    "Assign": "an assignment statement",
    "AsyncFor": "an asychronous for loop",
    "AsyncFunctionDef": "an asychronous function definition",
    "AsyncWith": "an asychronous with statement",
    "Attribute": "an attribute lookup (access a field)",
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
    # Simple primitive constant (ast.Constant, or the legacy Num/Str/etc. nodes)?
    if is_constant_node(node):
        return True
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
