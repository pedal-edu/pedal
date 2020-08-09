""" Utilities related to file handling """
import os


def normalize_path(first: str, second: str):
    """
    If the `first` path is relative, creates an absolute path relative to the `second` folder.

    Args:
        first: The path to normalize
        second: The path to normalize in regards to.

    Returns:
        str: A new path.
    """
    if os.path.isabs(first):
        return first
    else:
        return os.path.join(os.path.dirname(second), first)
