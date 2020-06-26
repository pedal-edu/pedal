"""
Utilities for making type names more readable.
"""


def humanize_type(t: type) -> str:
    """
    Creates a human readable string name for a type.

    Args:
        t: Any type

    Returns:
        str: Human readable string
    """
    if hasattr(t, '__name__'):
        return t.__name__
    else:
        return str(t)


def humanize_types(types) -> str:
    """
    Convert a tuple of multiple types into a human readable representation.
    Also handles individual types by falling back to humanize_type.

    Args:
        types: A tuple of types, or an individual type.

    Returns:
        str: Human readable type name.
    """
    if isinstance(types, tuple):
        return ', '.join(humanize_type(t) for t in types)
    return humanize_type(types)
