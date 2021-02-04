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


def get_extension(filename: str, default_extension="py") -> str:
    """ Get a file's extension (assumed to be after a period) """
    if not filename:
        return default_extension
    return filename.lower().split(".")[-1]


def find_possible_filenames(filenames, wildcard="*.py", alt_separator=";"):
    """ Yield all possible filenames that we could get from the given single/list of semicolon-separated string."""
    if isinstance(filenames, str):
        if alt_separator in filenames:
            filenames = filenames.split(alt_separator)
        else:
            filenames = [filenames]
    for a_filename in filenames:
        if a_filename.lower().strip().endswith(wildcard):
            a_filename = a_filename[:-len(wildcard)] or "."
            potentials = [f for f in os.listdir(a_filename) if f.endswith(wildcard)]
            if not potentials:
                continue
            a_filename = os.path.join(a_filename, potentials[0])
            yield a_filename
        else:
            yield a_filename

