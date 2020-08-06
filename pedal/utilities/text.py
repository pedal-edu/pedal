"""
Utilities for handling English Language rules.

"""


def add_indefinite_article(phrase):
    """
    Given a word, choose the appropriate indefinite article (e.g., "a" or "an")
    and add it the front of the word. Matches the original word's
    capitalization.

    Args:
        phrase (str): The phrase to get the appropriate definite article
            for.

    Returns:
        str: Either "an" or "a".
    """
    if phrase[0] in "aeiou":
        return "an "+phrase
    elif phrase[0] in "AEIOU":
        return "An "+phrase
    elif phrase[0].lower() == phrase[0]:
        return "a "+phrase
    else:
        return "A "+phrase


def escape_curly_braces(result):
    """ Replaces all occurrences of curly braces with double curly braces. """
    return result.replace("{", "{{").replace("}", "}}")


def safe_repr(obj, short=False, max_length=80) -> str:
    """
    Create a string representation of this object using :py:func:`repr`. If the
    object doesn't have a repr defined, then falls back onto the default
    :py:func:`object.__repr__`. Finally, if ``short`` is true, then the string
    will be truncated to the max_length value.

    Args:
        obj (Any): Any object to repr.
        short (bool): Whether or not to truncate to the max_length.
        max_length (int): How many maximum characters to use, if short is True.
    """
    try:
        result = repr(obj)
    except Exception:
        result = object.__repr__(obj)
    if short and len(result) >= max_length:
        result = result[:max_length] + ' [truncated]...'
    result = result
    return result


def chomp(text):
    """ Removes the trailing newline character, if there is one. """
    if not text:
        return text
    if text[-2:] == '\n\r':
        return text[:-2]
    if text[-1] == '\n':
        return text[:-1]
    return text
