from pedal.report.imperative import MAIN_REPORT
import string
import re

punctuation_table = str.maketrans(string.punctuation, ' ' * len(string.punctuation))

def _setup_assertions(report=None):
    if report is None:
        report = MAIN_REPORT
    if 'assertions' not in report:
        report['assertions'] = {
            'mode': 'stop'
        }

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

# Unittest Asserts

def assertEqual(left, right, score=None, message=None):
    pass


def assertNotEqual(left, right, score=None, message=None):
    pass


def assertTrue(something, score=None, message=None):
    pass


def assertFalse(something, score=None, message=None):
    pass


def assertIs(left, right, score=None, message=None):
    pass


def assertIsNot(left, right, score=None, message=None):
    pass


def assertIsNone(something):
    pass


def assertIsNotNone(something):
    pass


def assertIn(needle, haystack):
    pass


def assertNotIn(needle, haystack):
    pass


def assertIsInstance(value, types):
    pass


def assertNotIsInstance(value, types):
    pass


def assertRaises(exception):
    pass


def assertRaisesRegexp(exception):
    pass


def assertAlmostEqual(left, right):
    pass


def assertNotAlmostEqual(left, right):
    pass


def assertGreater(left, right):
    pass


def assertGreaterEqual(left, right):
    pass


def assertLess(left, right):
    pass


def assertLessEqual(left, right):
    pass


def assertRegexpMatches(text, pattern):
    pass


def assertNotRegexpMatches(text, pattern):
    pass


def assertItemsEqual(left, right):
    pass


def assertDictContainsSubset(left, right):
    pass


def assertMultiLineEqual(left, right):
    pass


def assertSequenceEqual(left, right):
    pass


# Speciality Asserts
def assertPrints(sandbox, strings):
    pass


def assertHasFunction(obj, function, args=None, returns=None):
    # If object is a sandbox, will check the .data[variable] attribute
    # Otherwise, check it directly
    pass


def assertHasClass(sandbox, class_name, attrs=None):
    pass


def assertHas(obj, variable, types=None, value=None):
    # If object is a sandbox, will check the .data[variable] attribute
    # Otherwise, check it directly
    pass

# Allow addition of new assertions
# e.g., assertGraphType, assertGraphValues
