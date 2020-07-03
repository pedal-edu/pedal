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
