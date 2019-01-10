import string
import re

punctuation_table = str.maketrans(string.punctuation, ' ' * len(string.punctuation))


def _normalize_string(a_string, numeric_endings=False):
    # Lower case
    a_string = a_string.lower()
    # Remove trailing decimals (TODO: How awful!)
    if numeric_endings:
        a_string = re.sub(r"(\s*[0-9]+)\.[0-9]+(\s*)", r"\1\2", a_string)
    # Remove punctuation
    a_string = a_string.translate(punctuation_table)
    # Split lines
    lines = a_string.split("\n")
    normalized = [[piece
                   for piece in line.split()]
                  for line in lines]
    normalized = [[piece for piece in line if piece]
                  for line in normalized
                  if line]
    return sorted(normalized)


def equality_test(actual, expected, _exact_strings, _delta, _test_output):
    return (  # Float comparison
            (isinstance(expected, float) and
             isinstance(actual, (float, int)) and
             abs(actual - expected) < _delta) or
            # Exact Comparison
            actual == expected or
            # Inexact string comparison
            (_exact_strings and isinstance(expected, str) and
             isinstance(actual, str) and
             _normalize_string(actual) == _normalize_string(expected)) or
            # Inexact output comparison
            (_test_output and isinstance(expected, str) and
             _normalize_string(expected) in [_normalize_string(line)
                                             for line in actual]) or
            # Exact output comparison
            (_test_output and isinstance(expected, list) and
             [_normalize_string(line) for line in expected] ==
             [_normalize_string(line) for line in actual])
    )


def contextualize_calls():
    pass


def try_all():
    pass


# Unittest Asserts
# noinspection PyUnusedLocal
def assertEqual(left, right, score=None, message=None):
    pass


# noinspection PyUnusedLocal
def assertNotEqual(left, right, score=None, message=None):
    pass


# noinspection PyUnusedLocal
def assertTrue(something, score=None, message=None):
    pass


# noinspection PyUnusedLocal
def assertFalse(something, score=None, message=None):
    pass


# noinspection PyUnusedLocal
def assertIs(left, right, score=None, message=None):
    pass


# noinspection PyUnusedLocal
def assertIsNot(left, right, score=None, message=None):
    pass


# noinspection PyUnusedLocal
def assertIsNone(something):
    pass


# noinspection PyUnusedLocal
def assertIsNotNone(something):
    pass


# noinspection PyUnusedLocal
def assertIn(needle, haystack):
    pass


# noinspection PyUnusedLocal
def assertNotIn(needle, haystack):
    pass


# noinspection PyUnusedLocal
def assertIsInstance(value, types):
    pass


# noinspection PyUnusedLocal
def assertNotIsInstance(value, types):
    pass


# noinspection PyUnusedLocal
def assertRaises(exception):
    pass


# noinspection PyUnusedLocal
def assertRaisesRegexp(exception):
    pass


# noinspection PyUnusedLocal
def assertAlmostEqual(left, right):
    pass


# noinspection PyUnusedLocal
def assertNotAlmostEqual(left, right):
    pass


# noinspection PyUnusedLocal
def assertGreater(left, right):
    pass


# noinspection PyUnusedLocal
def assertGreaterEqual(left, right):
    pass


# noinspection PyUnusedLocal
def assertLess(left, right):
    pass


# noinspection PyUnusedLocal
def assertLessEqual(left, right):
    pass


# noinspection PyUnusedLocal
def assertRegexpMatches(text, pattern):
    pass


# noinspection PyUnusedLocal
def assertNotRegexpMatches(text, pattern):
    pass


# noinspection PyUnusedLocal
def assertItemsEqual(left, right):
    pass


# noinspection PyUnusedLocal
def assertDictContainsSubset(left, right):
    pass


# noinspection PyUnusedLocal
def assertMultiLineEqual(left, right):
    pass


# noinspection PyUnusedLocal
def assertSequenceEqual(left, right):
    pass


# Speciality Asserts
# noinspection PyUnusedLocal
def assertPrints(sandbox, strings):
    pass


# noinspection PyUnusedLocal
def assertHasFunction(obj, function, args=None, returns=None):
    # If object is a sandbox, will check the .data[variable] attribute
    # Otherwise, check it directly
    pass


# noinspection PyUnusedLocal
def assertHasClass(sandbox, class_name, attrs=None):
    pass


# noinspection PyUnusedLocal
def assertHas(obj, variable, types=None, value=None):
    # If object is a sandbox, will check the .data[variable] attribute
    # Otherwise, check it directly
    pass

# Allow addition of new assertions
# e.g., assertGraphType, assertGraphValues
