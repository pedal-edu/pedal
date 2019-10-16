import string
import re

from pedal.report.imperative import MAIN_REPORT
from pedal.sandbox.result import SandboxResult
from pedal.sandbox.exceptions import SandboxException
from pedal.sandbox.sandbox import DataSandbox
from pedal.assertions.setup import _setup_assertions, AssertionException

# TODO: Allow bundling of assertions to make a table

iterable = lambda obj: hasattr(obj, '__iter__') or hasattr(obj, '__getitem__')

_MAX_LENGTH = 80


def _escape_curly_braces(result):
    return result.replace("{", "{{").replace("}", "}}")


def safe_repr(obj, short=False):
    try:
        result = repr(obj)
    except Exception:
        result = object.__repr__(obj)
    if short and len(result) >= _MAX_LENGTH:
        result = result[:_MAX_LENGTH] + ' [truncated]...'
    result = result
    return result


try:
    punctuation_table = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
except AttributeError:
    punctuation_table = None

if punctuation_table is None:
    def strip_punctuation(a_string):
        return ''.join(ch for ch in a_string if ch not in set(string.punctuation))
else:
    def strip_punctuation(a_string):
        return a_string.translate(punctuation_table)


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


# Unittest Asserts
DELTA = .001


def _fail(code_message, actual_message, expected_message,
          show_expected_value, modify_right, *values):
    normal_values = []
    sandboxed_values = []
    sandboxed_results = []
    if modify_right and values:
        values = values[:-1] + (modify_right(values[-1]),)
    for value in values:
        if is_sandbox_result(value):
            sandboxed_results.append(value)
            value = value._actual_value
            sandboxed_values.append(safe_repr(value))
        else:
            normal_values.append(safe_repr(value))
    if sandboxed_results:
        code_message = _build_context(sandboxed_results, actual_message,
                                      expected_message, show_expected_value)
    return AssertionException(code_message.format(*(sandboxed_values + normal_values)))


def _build_result_from_target(target, index, quantity):
    if target == "_":
        if quantity == 1:
            return "the result"
        elif index == 0:
            return "the first result"
        else:
            return "the second result"
    return "<code>" + target + "</code>"


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
        calls = [_escape_curly_braces(str(call)) for call in calls]
        context.append("I ran:\n<pre>" + "\n".join(calls) + "</pre>")
    if inputs:
        inputs = [_escape_curly_braces(str(inp)) for inp in inputs]
        context.append("I entered as input:\n<pre>" + "\n".join(inputs) + "</pre>")
    actual_message += ":\n<pre>{}</pre>"
    for i, target in enumerate(targets):
        named_target = _build_result_from_target(target, i, len(targets))
        if target == '_':
            context.append(named_target.capitalize() + " " + actual_message)
        else:
            context.append("The value of " + named_target + " " + actual_message)
    expected_context = "But I expected "
    if len(targets) == 2:
        expected_context += _build_result_from_target(targets[0], 0, 2)
        expected_context += " " + expected_message + " "
        expected_context += _build_result_from_target(targets[1], 1, 2)
    else:
        expected_context += _build_result_from_target(targets[0], 0, 1)
        expected_context += " " + expected_message
        if show_expected_value:
            expected_context += ":\n<pre>{}</pre>"
    context.append(expected_context)
    return "\n".join(context)


def is_sandbox_result(value):
    if hasattr(value, "__actual_class__"):
        if value.__actual_class__ == SandboxResult:
            return True
    return False


def _basic_assertion(left, right, operator, code_comparison_message,
                     hc_message, hc_message_past, message, report, contextualize,
                     show_expected_value=True, modify_right=None):
    if report is None:
        report = MAIN_REPORT
    _setup_assertions(report)
    context = ""
    if message:
        message = "\n" + message
    else:
        message = ""
    # TODO: Handle right-side sandbox result
    # if is_sandbox_result(right):
    #    right = right._actual_value
    if isinstance(left, Exception):
        return False
    if isinstance(right, Exception):
        return False
    if not operator(left, right):
        failure = _fail(code_comparison_message, hc_message, hc_message_past,
                        show_expected_value, modify_right, left, right)
        report['assertions']['collected'].append(failure)
        report.attach('Instructor Test', category='student', tool='Assertions',
                      mistake={'message': "Student code failed instructor test.<br>\n" +
                                          context + str(failure) + message})
        report['assertions']['failures'] += 1
        if report['assertions']['exceptions']:
            raise failure
        else:
            return False
    return True


PRE_VAL = ""


def assertEqual(left, right, score=None, message=None, report=None,
                contextualize=True, exact=False, compare_lengths=None):
    if compare_lengths is None:
        compare_lengths = (iterable(left) and isinstance(right, (int, float)))
    if _basic_assertion(left, right,
                        lambda l, r:
                        equality_test(len(l), r, False, DELTA, False) if
                        compare_lengths else
                        equality_test(l, r, False, DELTA, False),
                        "len({}) != {}" if compare_lengths else "{} != {}",
                        "was" + PRE_VAL,
                        "to have its length equal to"
                        if compare_lengths else "to be equal to",
                        message, report, contextualize):
        if report is None:
            report = MAIN_REPORT
        report.give_partial(score)
        return True
    return False


assert_equal = assertEqual


def assertNotEqual(left, right, score=None, message=None, report=None,
                   contextualize=True, exact=False):
    if _basic_assertion(left, right,
                        lambda l, r: not equality_test(l, r, False, DELTA, False),
                        "{} == {}",
                        "was" + PRE_VAL,
                        "to not be equal to",
                        message, report, contextualize):
        if report is None:
            report = MAIN_REPORT
        report.give_partial(score)
        return True
    return False


def assertTrue(something, score=None, message=None, report=None,
               contextualize=True):
    if _basic_assertion(something, True,
                        lambda l, r: bool(l),
                        "{} is true",
                        "was false" + PRE_VAL,
                        "to be true",
                        message, report, contextualize,
                        show_expected_value=False):
        if report is None:
            report = MAIN_REPORT
        report.give_partial(score)
        return True
    return False


def assertFalse(something, score=None, message=None, report=None,
                contextualize=True):
    if _basic_assertion(something, False,
                        lambda l, r: not bool(l),
                        "{} is false",
                        "was true" + PRE_VAL,
                        "to be false",
                        message, report, contextualize,
                        show_expected_value=False):
        if report is None:
            report = MAIN_REPORT
        report.give_partial(score)
        return True
    return False


def assertIs(left, right, score=None, message=None):
    pass


def assertIsNot(left, right, score=None, message=None):
    pass


def _actually_is_none(l, r):
    if is_sandbox_result(l):
        return l._actual_value is None
    return l is None


def assertIsNone(something, score=None, message=None, report=None,
                 contextualize=True):
    if _basic_assertion(something, None,
                        _actually_is_none,
                        "{} is none",
                        "was" + PRE_VAL,
                        "to be none",
                        message, report, contextualize,
                        show_expected_value=False):
        if report is None:
            report = MAIN_REPORT
        report.give_partial(score)
        return True
    return False


def _actually_is_not_none(l, r):
    if is_sandbox_result(l):
        return l._actual_value is not None
    return l is not None


def assertIsNotNone(something, score=None, message=None, report=None,
                    contextualize=True):
    if _basic_assertion(something, None,
                        _actually_is_not_none,
                        "{} is not none",
                        "was" + PRE_VAL,
                        "to not be none",
                        message, report, contextualize,
                        show_expected_value=False):
        if report is None:
            report = MAIN_REPORT
        report.give_partial(score)
        return True
    return False


def assertIn(needle, haystack, score=None, message=None, report=None,
             contextualize=True):
    expected_message = "to be in"
    if not is_sandbox_result(needle) and is_sandbox_result(haystack):
        expected_message = "to contain"
    if _basic_assertion(needle, haystack,
                        lambda n, h: n in h,
                        "{} not in {}",
                        "was" + PRE_VAL,
                        expected_message,
                        message, report, contextualize):
        if report is None:
            report = MAIN_REPORT
        report.give_partial(score)
        return True
    return False


def assertNotIn(needle, haystack, score=None, message=None, report=None,
                contextualize=True):
    expected_message = "to not be in"
    if not is_sandbox_result(needle) and is_sandbox_result(haystack):
        expected_message = "to not contain"
    if _basic_assertion(needle, haystack,
                        lambda n, h: n not in h,
                        "{} in {}",
                        "was" + PRE_VAL,
                        expected_message,
                        message, report, contextualize):
        if report is None:
            report = MAIN_REPORT
        report.give_partial(score)
        return True
    return False


def _humanize_types(types):
    if isinstance(types, tuple):
        return ', '.join([t.__name__ for t in types])
    return types.__name__


def assertIsInstance(value, types, score=None, message=None, report=None,
                     contextualize=True):
    if _basic_assertion(value, types,
                        lambda v, t: isinstance(v, t),
                        "isinstance({}, {})",
                        "was" + PRE_VAL,
                        "to be of type",
                        message, report, contextualize,
                        modify_right=_humanize_types):
        if report is None:
            report = MAIN_REPORT
        report.give_partial(score)
        return True
    return False


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


def assertGreater(left, right, score=None, message=None, report=None,
                  contextualize=True, compare_lengths=None):
    if compare_lengths is None:
        compare_lengths = (iterable(left) and isinstance(right, (int, float)))
    if _basic_assertion(left, right,
                        lambda l, r:
                        len(l) > r if
                        compare_lengths else
                        l > r,
                        "len({}) <= {}" if compare_lengths else "{} <= {}",
                        "was" + PRE_VAL,
                        "to have its length greater than"
                        if compare_lengths else
                        "to be greater than",
                        message, report, contextualize):
        if report is None:
            report = MAIN_REPORT
        report.give_partial(score)
        return True
    return False


def assertGreaterEqual(left, right, score=None, message=None, report=None,
                       contextualize=True, compare_lengths=None):
    if compare_lengths is None:
        compare_lengths = (iterable(left) and isinstance(right, (int, float)))
    if _basic_assertion(left, right,
                        lambda l, r:
                        len(l) >= r if
                        compare_lengths else
                        l >= r,
                        "len({}) < {}" if compare_lengths else "{} < {}",
                        "was" + PRE_VAL,
                        "to have its length greater than or equal to" if compare_lengths else
                        "to be greater than or equal to",
                        message, report, contextualize):
        if report is None:
            report = MAIN_REPORT
        report.give_partial(score)
        return True
    return False


def assertLess(left, right, score=None, message=None, report=None,
               contextualize=True, compare_lengths=None):
    if compare_lengths is None:
        compare_lengths = (iterable(left) and isinstance(right, (int, float)))
    if _basic_assertion(left, right,
                        lambda l, r:
                        len(l) < r if
                        compare_lengths else
                        l < r,
                        "len({}) >= {}" if compare_lengths else "{} >= {}",
                        "was" + PRE_VAL,
                        "to have its length less than"
                        if compare_lengths else
                        "to be less than",
                        message, report, contextualize):
        if report is None:
            report = MAIN_REPORT
        report.give_partial(score)
        return True
    return False


def assertLessEqual(left, right, score=None, message=None, report=None,
                    contextualize=True, compare_lengths=None):
    if compare_lengths is None:
        compare_lengths = (iterable(left) and isinstance(right, (int, float)))
    if _basic_assertion(left, right,
                        lambda l, r:
                        len(l) <= r if
                        compare_lengths else
                        l <= r,
                        "len({}) > {}" if compare_lengths else "{} > {}",
                        "was" + PRE_VAL,
                        "to have its length less than or equal to" if compare_lengths else
                        "to be less than or equal to",
                        message, report, contextualize):
        if report is None:
            report = MAIN_REPORT
        report.give_partial(score)
        return True
    return False


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


# TODO: assertPrintIncludes

# Speciality Asserts
def assertPrints(result, expected_output, args=None, returns=None,
                 score=None, message=None, report=None,
                 contextualize=True, exact=False):
    if not isinstance(result, SandboxResult):
        return False
        raise TypeError("You must pass in a SandboxResult (e.g., using `call`) to assertPrints")
    if report is None:
        report = MAIN_REPORT
    _setup_assertions(report)
    call_id = result._actual_call_id
    sandbox = result._actual_sandbox
    calls = sandbox.call_contexts[call_id]
    inputs = sandbox.input_contexts[call_id]
    actual_output = sandbox.output_contexts[call_id]
    if not equality_test(actual_output, expected_output, exact, DELTA, True):
        context = []
        if calls:
            context.append("I ran:\n<pre>" +
                           "\n".join(map(str, calls)) +
                           "</pre>")
        if inputs:
            context.append("I entered as input:\n<pre>" +
                           "\n".join(map(str, inputs)) +
                           "</pre>")
        if actual_output:
            context.append("The function printed:\n<pre>" +
                           "\n".join(map(str, actual_output)) +
                           "</pre>")
        else:
            context.append("The function printed nothing.")
        context.append("But I expected the output:\n<pre>" + "\n".join(map(str, expected_output)) + "</pre>")
        failure = AssertionException("\n".join(context))
        report['assertions']['collected'].append(failure)
        report.attach('Instructor Test', category='student', tool='Assertions',
                      mistake={'message': "Student code failed instructor test.<br>\n" +
                                          str(failure)})
        report['assertions']['failures'] += 1
        if report['assertions']['exceptions']:
            raise failure
        else:
            return False
    report.give_partial(score)
    return True


def assertHasFunction(obj, function, args=None, returns=None,
                      score=None, message=None, report=None,
                      contextualize=True, exact=False):
    # If object is a sandbox, will check the .data[variable] attribute
    # Otherwise, check it directly
    if isinstance(obj, DataSandbox):
        comparison = lambda o, f: f in o.data
    else:
        def comparison(o, f):
            try:
                return f in o
            except:
                return hasattr(o, f)
    if not _basic_assertion(obj, function,
                            comparison,
                            "Could not find function {}{}",
                            "was" + PRE_VAL,
                            "to have the function",
                            message, report, contextualize):
        return False
    if isinstance(obj, DataSandbox):
        student_function = obj.data[function]
    else:
        try:
            student_function = obj[function]
        except:
            student_function = getattr(obj, function)
    if _basic_assertion(student_function, function,
                        lambda l, r: callable(l),
                        "The value {} is in the variable {}, and that value is not a callable function.",
                        "was callable" + PRE_VAL,
                        "to be callable",
                        message, report, contextualize,
                        show_expected_value=False):
        if report is None:
            report = MAIN_REPORT
        report.give_partial(score)
        return True
    return False


def assertHasClass(sandbox, class_name, attrs=None):
    pass


def assertHas(obj, variable, types=None, value=None, score=None,
              message=None, report=None, contextualize=True):
    # If object is a sandbox, will check the .data[variable] attribute
    # Otherwise, check it directly
    if isinstance(obj, DataSandbox):
        comparison = lambda o, v: v in o.data
    else:
        comparison = lambda o, v: v in hasattr(o, v)
    if not _basic_assertion(obj, variable,
                            comparison,
                            "Could not find variable {}{}",
                            "was" + PRE_VAL,
                            "to have the variable",
                            message, report, contextualize):
        return False
    if isinstance(obj, DataSandbox):
        student_variable = obj.data[variable]
    else:
        student_variable = getattr(obj, variable)
    if types is not None:
        if not _basic_assertion(student_variable, types,
                                lambda v, t: isinstance(v, t),
                                "isinstance({}, {})",
                                "was" + PRE_VAL,
                                "to be of type",
                                message, report, contextualize,
                                modify_right=_humanize_types):
            return False
    if value is not None:
        if not _basic_assertion(student_variable, value,
                                lambda l, r: equality_test(l, r, False, DELTA, False),
                                "{} != {}",
                                "was" + PRE_VAL,
                                "to be equal to",
                                message, report, contextualize,
                                show_expected_value=False):
            return False
    if report is None:
        report = MAIN_REPORT
    report.give_partial(score)
    return True


def assertGenerally(expression, score=None, message=None, report=None,
                    contextualize=True):
    if report is None:
        report = MAIN_REPORT
    _setup_assertions(report)
    if expression:
        report.give_partial(score)
        return True
    else:
        report['assertions']['failures'] += 1
        if report['assertions']['exceptions']:
            raise AssertionException("General assertion")
        else:
            return False

# Allow addition of new assertions
# e.g., assertGraphType, assertGraphValues
