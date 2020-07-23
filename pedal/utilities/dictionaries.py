"""
Various helper functions related to dictionaries.
"""


def extend_dictionary(d1, d2):
    """
    Helper function to create a new dictionary with the contents of the two
    given dictionaries. Does not modify either dictionary, and the values are
    copied shallowly. If there are repeats, the second dictionary wins ties.

    The function is written to ensure Skulpt compatibility.

    Args:
        d1 (dict): The first dictionary
        d2 (dict): The second dictionary
    Returns:
        dict: The new dictionary
    """
    d3 = {}
    for key, value in d1.items():
        d3[key] = value
    for key, value in d2.items():
        d3[key] = value
    return d3
