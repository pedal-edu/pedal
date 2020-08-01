"""
Utilities for working with Abstract Syntax Trees.
"""
import ast

__all__ = ['is_literal']


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
    visit_Expr = _track_lines
    visit_Pass = _track_lines
    visit_Continue = _track_lines
    visit_Break = _track_lines
