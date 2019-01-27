from pedal.report.imperative import MAIN_REPORT
from pedal.sandbox.result import SandboxResult
import string
import re

from pedal.assertions.setup import _setup_assertions

_MAX_LENGTH = 80

def safe_repr(obj, short=False):
    try:
        result = repr(obj)
    except Exception:
        result = object.__repr__(obj)
    if not short or len(result) < _MAX_LENGTH:
        return result
    return result[:_MAX_LENGTH] + ' [truncated]...'

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
    # Float comparison
    if (isinstance(expected, float) and
        isinstance(actual, (float, int)) and
        abs(actual - expected) < _delta):
        return True
    # Exact Comparison
    if actual == expected:
        return True
    # Inexact string comparison
    if (_exact_strings and isinstance(expected, str) and
        isinstance(actual, str) and
        _normalize_string(actual) == _normalize_string(expected)):
        return True
    # Output comparison
    if _test_output:
        # Inexact output comparison
        normalized_actual = [_normalize_string(line) for line in actual]
        if (isinstance(expected, str) and
            _normalize_string(expected) in normalized_actual):
            return True
        # Exact output comparison
        normalized_expected = [_normalize_string(line) for line in expected]
        if (isinstance(expected, list) and
            normalized_expected == normalized_actual):
            return True
    # Else
    return False

class AssertionException(Exception):
    pass

# Unittest Asserts
DELTA = .001
def _fail(code_message, hc_message, hc_message_past, *values):
    contextualized_values = []
    for value in values:
        if is_sandbox_result(value):
            value, code_message = _build_context(value, hc_message, hc_message_past)
        else:
            value = safe_repr(value)
        contextualized_values.append(value)
    return AssertionException(code_message.format(*values))
    
def _build_context(result, hc_message, hc_message_past):
    left = result._actual_value
    left_call_id = result._actual_call_id
    left_sandbox = result._actual_sandbox
    outputs = left_sandbox.output_contexts[left_call_id]
    calls = left_sandbox.call_contexts[left_call_id]
    inputs = left_sandbox.input_contexts[left_call_id]
    context = ""
    if calls:
        context += "I ran:<br>\n"
        context += '<br>\n'.join('<pre>{}</pre>'.format(call) for call in calls)
        context += "\n"
    if inputs:
        context += "I entered as input:<br>\n"
        context += '<br>\n'.join('<pre>{}</pre>'.format(i) for i in inputs)
        context += "\n"
    context += "The result "+hc_message_past+":\n"
    context += "<pre>{}</pre>\n"
    context += "But I expected the result "+hc_message+":\n"
    context += "<pre>{}</pre>"
    return left, context

def is_sandbox_result(value):
    if hasattr(value, "__actual_class__"):
        if value.__actual_class__ == SandboxResult:
            return True
    return False
    
def _basic_assertion(left, right, operator, code_comparison_message,
                     hc_message, hc_message_past, message, report, contextualize):
    if report is None:
        report = MAIN_REPORT
    _setup_assertions(report)
    context = ""
    # TODO: Handle right-side sandbox result
    #if is_sandbox_result(right):
    #    right = right._actual_value
    if not operator(left, right):
        failure = _fail(code_comparison_message, hc_message, hc_message_past, left, right)
        report['assertions']['collected'].append(failure)
        report.attach('Instructor Test', category='Instructor', tool='Assertions',
                      mistake={'message': "Student code failed instructor test.<br>\n"+
                                          context+str(failure)})
        if report['assertions']['exceptions']:
            raise failure
        else:
            return False
    return True

def assertEqual(left, right, score=None, message=None, report=None,
                contextualize=True):
    return _basic_assertion(left, right,
                            lambda l, r: equality_test(l, r, True, DELTA, False),
                            "{} != {}",
                            "to be equal to",
                            "was equal to",
                            message, report, contextualize)
    
    

    
assert_equal = assertEqual


def assertNotEqual(left, right, score=None, message=None):
    if isinstance(left, SandboxResult):
        left = left._actual_value
    if isinstance(right, SandboxResult):
        right = right._actual_value
    if not equality_test(left, right, True, DELTA, False):
        _fail("{} == {}", left, right)


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
