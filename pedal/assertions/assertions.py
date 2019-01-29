from pedal.report.imperative import MAIN_REPORT
from pedal.sandbox.result import SandboxResult
from pedal.sandbox.exceptions import SandboxException
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
def _fail(code_message, actual_message, expected_message, show_expected_value,
          *values):
    normal_values = []
    sandboxed_values = []
    sandboxed_results = []
    for value in values:
        if is_sandbox_result(value):
            sandboxed_results.append(value)
            value = value._actual_value
            sandboxed_values.append(safe_repr(value))
        else:
            normal_values.append(safe_repr(value))
    if sandboxed_results:
        code_message = _build_context(sandboxed_results, actual_message, expected_message,
                                      show_expected_value)
    return AssertionException(code_message.format(*sandboxed_values, *normal_values))

def _build_result_from_target(target, index, quantity):
    if target == "_":
        if quantity == 1:
            return "the result"
        elif index == 0:
            return "the first result"
        else:
            return "the second result"
    return "<code>"+target+"</code>"
    
def _build_context(sandboxed_results, actual_message, expected_message,
                   show_expected_value):
    context = []
    calls = []
    inputs = []
    outputs = []
    targets = []
    for result in sandboxed_results:
        # Look up info
        call_id = result._actual_call_id
        sandbox = result._actual_sandbox
        outputs.extend(sandbox.output_contexts[call_id])
        calls.extend(sandbox.call_contexts[call_id])
        inputs.extend(sandbox.input_contexts[call_id])
        targets.append(sandbox.target_contexts[call_id])
    # Actual rendering of text
    if calls:
        context.append("I ran:<pre>"+ "\n".join(map(str, calls))+ "</pre>")
    if inputs:
        context.append("I entered as input:<pre>"+ "\n".join(map(str, inputs))+ "</pre>")
    actual_message += ":<pre>{}</pre>"
    for i, target in enumerate(targets):
        named_target = _build_result_from_target(target, i, len(targets))
        if target == '_':
            context.append(named_target.capitalize() + " "+actual_message)
        else:
            context.append("The value of "+named_target+" "+actual_message)
    expected_context = "But I expected "
    if len(targets) == 2:
        expected_context += _build_result_from_target(targets[0], 0, 2)
        expected_context += " " +expected_message + " "
        expected_context += _build_result_from_target(targets[1], 1, 2)
    else:
        expected_context += _build_result_from_target(targets[0], 0, 1)
        expected_context += " " + expected_message
        if show_expected_value:
            expected_context += ":<pre>{}</pre>"
    context.append(expected_context)
    return "\n".join(context)

def is_sandbox_result(value):
    if hasattr(value, "__actual_class__"):
        if value.__actual_class__ == SandboxResult:
            return True
    return False
    
def _basic_assertion(left, right, operator, code_comparison_message,
                     hc_message, hc_message_past, message, report, contextualize,
                     show_expected_value=True):
    if report is None:
        report = MAIN_REPORT
    _setup_assertions(report)
    context = ""
    # TODO: Handle right-side sandbox result
    #if is_sandbox_result(right):
    #    right = right._actual_value
    if isinstance(left, Exception):
        return False
    if isinstance(right, Exception):
        return False
    if not operator(left, right):
        failure = _fail(code_comparison_message, hc_message, hc_message_past,
                        show_expected_value, left, right)
        report['assertions']['collected'].append(failure)
        report.attach('Instructor Test', category='Instructor', tool='Assertions',
                      mistake={'message': "Student code failed instructor test.<br>\n"+
                                          context+str(failure)})
        if report['assertions']['exceptions']:
            raise failure
        else:
            return False
    return True
    
PRE_VAL = ""

def assertEqual(left, right, score=None, message=None, report=None,
                contextualize=True, exact=False):
    return _basic_assertion(left, right,
                            lambda l, r: equality_test(l, r, False, DELTA, False),
                            "{} != {}",
                            "was"+PRE_VAL,
                            "to be equal to",
                            message, report, contextualize)
    
    

    
assert_equal = assertEqual


def assertNotEqual(left, right, score=None, message=None):
    pass


def assertTrue(something, score=None, message=None, report=None,
                contextualize=True):
    return _basic_assertion(something, True,
                            lambda l, r: bool(l),
                            "{} is true",
                            "was false"+PRE_VAL,
                            "to be true",
                            message, report, contextualize,
                            show_expected_value=False)


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


def assertIn(needle, haystack, score=None, message=None, report=None,
                contextualize=True):
    expected_message = "to be in"
    if not is_sandbox_result(needle) and is_sandbox_result(haystack):
        expected_message = "to contain"
    return _basic_assertion(needle, haystack,
                            lambda n, h: n in h,
                            "{} not in {}",
                            "was"+PRE_VAL,
                            expected_message,
                            message, report, contextualize)


def assertNotIn(needle, haystack, score=None, message=None, report=None,
                contextualize=True):
    expected_message = "to not be in"
    if not is_sandbox_result(needle) and is_sandbox_result(haystack):
        expected_message = "to not contain"
    return _basic_assertion(needle, haystack,
                            lambda n, h: n not in h,
                            "{} in {}",
                            "was"+PRE_VAL,
                            expected_message,
                            message, report, contextualize)


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
