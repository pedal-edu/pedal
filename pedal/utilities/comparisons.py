import string
import re

# Number encapsulates bool, int, float, complex, decimal.Decimal, etc.
try:
    from numbers import Number
except:
    Number = (bool, int, float, complex)

try:
    bytes
except NameError:
    bytes = str

try:
    frozenset()
except:
    frozenset = tuple()

try:
    punctuation_table = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
except AttributeError:
    punctuation_table = None

if punctuation_table is None:
    def strip_punctuation(a_string):
        """

        Args:
            a_string:

        Returns:

        """
        return ''.join(ch for ch in a_string if ch not in set(string.punctuation))
else:
    def strip_punctuation(a_string):
        """

        Args:
            a_string:

        Returns:

        """
        return a_string.translate(punctuation_table)

SET_GENERATOR_TYPES = (type({}.keys()), type({}.values()), type({}.items()))

LIST_GENERATOR_TYPES = (type(map(bool, [])), type(filter(bool, [])),
                        type(range(0)), type(reversed([])), type(zip()),
                        type(enumerate([])))


def _split_into_lolos(a_string) -> 'List[List[str]]':
    """
    Splits the given string into a list of list of strings, based on new lines.

    Args:
        a_string: The string to split

    Returns: The list of list of strings
    """
    return [list(line) for line in a_string.split("\n")]


def _normalize_string(a_string, numeric_endings=False):
    # Lower case
    a_string = a_string.lower()
    # Remove trailing decimals (TODO: How awful!)
    if numeric_endings:
        a_string = re.sub(r"(\s*[0-9]+)\.[0-9]+(\s*)", r"\1\2", a_string)
    # Remove punctuation
    a_string = strip_punctuation(a_string)
    # Split lines
    lines = a_string.split("\n")
    normalized = [[piece for piece in line.split()]
                  for line in lines]
    normalized = [[piece for piece in line if piece]
                  for line in normalized if line]
    return sorted(normalized)


def output_test(actual, expected, _exact_strings):
    """

    Args:
        actual:
        expected:
        _exact_strings: Force capitalization/whitespace/symbols to match exactly.

    Returns:

    """
    normalizer = _normalize_string if not _exact_strings else _split_into_lolos
    normalized_actual = [normalizer(line) for line in actual]
    if isinstance(expected, (str, bytes)):
        return normalizer(expected) in normalized_actual
    else:
        normalized_expected = [normalizer(line) for line in expected]
        return all(each_actual in normalized_expected for each_actual in normalized_actual)


def equality_test(actual, expected, _exact_strings, _delta):
    """

    Args:
        actual:
        expected:
        _exact_strings:
        _delta:

    Returns:

    """
    # Check if generators
    if isinstance(expected, LIST_GENERATOR_TYPES):
        expected = list(expected)
    elif isinstance(expected, SET_GENERATOR_TYPES):
        expected = set(expected)
    if isinstance(actual, LIST_GENERATOR_TYPES):
        actual = list(actual)
    elif isinstance(actual, SET_GENERATOR_TYPES):
        actual = set(actual)

    # Float comparison
    if isinstance(expected, float) and isinstance(actual, (float, int)):
        error = 10 ** (-_delta)
        return abs(expected - actual) < error
    # Other numerics
    elif isinstance(expected, Number) and isinstance(actual, Number) and isinstance(expected, type(actual)):
        return expected == actual
    # String comparisons
    elif ((isinstance(expected, str) and isinstance(actual, str)) or
          (isinstance(expected, bytes) and isinstance(actual, bytes))):
        if _exact_strings:
            return expected == actual
        else:
            return _normalize_string(expected) == _normalize_string(actual)
    # Exact Comparison
    elif actual == expected:
        return True
    # Sequence comparisons
    elif isinstance(expected, list) and isinstance(actual, list):
        return _are_sequences_equal(actual, expected, _exact_strings, _delta)
    elif isinstance(expected, tuple) and isinstance(actual, tuple):
        return _are_sequences_equal(actual, expected, _exact_strings, _delta)
    elif isinstance(expected, set) and isinstance(actual, set):
        return _are_sets_equal(actual, expected, _exact_strings, _delta)
    elif isinstance(expected, frozenset) and isinstance(actual, frozenset):
        return _are_sets_equal(actual, expected, _exact_strings, _delta)
    elif isinstance(expected, dict) and isinstance(actual, dict):
        primary_keys = set(expected.keys())
        if not _are_sets_equal(primary_keys, set(actual.keys()), _exact_strings, _delta):
            return False
        for key in primary_keys:
            if not equality_test(expected[key], actual[key], _exact_strings, _delta):
                return False
        return True
    # Else
    return False


def _are_sequences_equal(x, y, _exact_strings, _delta):
    """
    For sequences that support __len__, __iter__, and should have the same
    order.
    """
    if len(x) != len(y):
        return False
    for x_element, y_element in zip(x, y):
        if not equality_test(x_element, y_element, _exact_strings, _delta):
            return False
    return True


def _set_contains(needle, haystack, _exact_strings, _delta):
    """
    Tests if the given needle is one of the elements of haystack, using
    the _is_equal function.
    """
    for element in haystack:
        if equality_test(element, needle, _exact_strings, _delta):
            return True
    return False


def _are_sets_equal(x, y, _exact_strings, _delta):
    """
    For sequences that support __len__, __iter__, but order does not matter.
    """
    if len(x) != len(y):
        return False
    for x_element in x:
        if not _set_contains(x_element, y, _exact_strings, _delta):
            return False
    return True


def iterable(obj) -> bool:
    """
    Determines if this object satisfies the iterable interface, which
    requires it to support either ``__iter__`` or ``__getitem__``.
    """
    return hasattr(obj, '__iter__') or hasattr(obj, '__getitem__')
