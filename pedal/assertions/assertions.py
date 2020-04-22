from pedal import feedback
from pedal.core.feedback import Feedback, AtomicFeedbackFunction
from pedal.core.commands import give_partial
from pedal.core.report import MAIN_REPORT
from pedal.sandbox.result import SandboxResult
from pedal.sandbox.sandbox import DataSandbox
from pedal.assertions.setup import _setup_assertions, AssertionException, TOOL_NAME_ASSERTIONS
from pedal.utilities.comparisons import equality_test, output_test
from pedal.utilities.types import humanize_types


# TODO: Allow bundling of assertions to make a table


def iterable(obj):
    """

    Args:
        obj:

    Returns:

    """
    return hasattr(obj, '__iter__') or hasattr(obj, '__getitem__')


DELTA = .001
_MAX_LENGTH = 80


def _escape_curly_braces(result):
    return result.replace("{", "{{").replace("}", "}}")


def safe_repr(obj, short=False):
    """

    Args:
        obj:
        short:

    Returns:

    """
    try:
        result = repr(obj)
    except Exception:
        result = object.__repr__(obj)
    if short and len(result) >= _MAX_LENGTH:
        result = result[:_MAX_LENGTH] + ' [truncated]...'
    result = result
    return result


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
    """

    Args:
        value:

    Returns:

    """
    if hasattr(value, "__actual_class__"):
        if value.__actual_class__ == SandboxResult:
            return True
    return False


@AtomicFeedbackFunction(title="Instructor Test",
                        message_template=("Student code failed instructor test.\n"
                                          "{context}{failure}{message}"))
def _basic_assertion(label, justification, left, right, operator, code_comparison_message,
                     hc_message, hc_message_past, message, contextualize, report=MAIN_REPORT,
                     show_expected_value=True, modify_right=None, partial_score=0, muted=False):
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
        report[TOOL_NAME_ASSERTIONS]['collected'].append(failure)
        fields = {'context': context, 'failure': str(failure), 'message': message}
        feedback(label, tool=TOOL_NAME_ASSERTIONS, category=Feedback.CATEGORIES.INSTRUCTOR,
                 justification=justification, title=_basic_assertion.title,
                 message=_basic_assertion.message_template.format(**fields), fields=fields,
                 score=partial_score, correct=False, muted=muted, report=report)
        report[TOOL_NAME_ASSERTIONS]['failures'] += 1
        if report[TOOL_NAME_ASSERTIONS]['exceptions']:
            raise failure
        else:
            return False
    return True


def assertEqual(left, right, score=None, message=None, report=MAIN_REPORT,
                contextualize=True, exact=False, compare_lengths=None, muted=False,
                label="assert_equal"):
    """

    Args:
        label:
        left:
        right:
        score:
        message:
        report:
        contextualize:
        exact:
        compare_lengths:
        muted:

    Returns:

    """
    if compare_lengths is None:
        compare_lengths = (iterable(left) and isinstance(right, (int, float)))
    return _basic_assertion(label, "Left and right were not equal", left, right,
                            lambda l, r:
                            equality_test(len(l), r, exact, DELTA) if
                            compare_lengths else
                            equality_test(l, r, exact, DELTA),
                            "len({}) != {}" if compare_lengths else "{} != {}",
                            "was",
                            "to have its length equal to"
                            if compare_lengths else "to be equal to",
                            message, contextualize, report=report, partial_score=score, muted=muted)


def assertNotEqual(left, right, score=None, message=None, report=MAIN_REPORT,
                   contextualize=True, exact=False, label="assert_not_equal", muted=False):
    """

    Args:
        left:
        right:
        score:
        message:
        report:
        contextualize:
        exact:

    Returns:

    """
    return _basic_assertion(label, "Left and right were equal", left, right,
                            lambda l, r: not equality_test(l, r, exact, DELTA),
                            "{} == {}",
                            "was",
                            "to not be equal to",
                            message, contextualize, report=report, partial_score=score, muted=muted)


def assertTrue(something, score=None, message=None, report=MAIN_REPORT,
               contextualize=True, label="assert_true", muted=False):
    """

    Args:
        something:
        score:
        message:
        report:
        contextualize:

    Returns:

    """
    return _basic_assertion(label, "Value was not True", something, True,
                            lambda l, r: bool(l),
                            "{} is true",
                            "was false",
                            "to be true",
                            message, contextualize, report=report,
                            show_expected_value=False, partial_score=score, muted=muted)


def assertFalse(something, score=None, message=None, report=MAIN_REPORT,
                contextualize=True, label="assert_false", muted=False):
    """

    Args:
        something:
        score:
        message:
        report:
        contextualize:

    Returns:

    """
    return _basic_assertion(label, "Value was not False", something, False,
                            lambda l, r: not bool(l),
                            "{} is false",
                            "was true",
                            "to be false",
                            message, contextualize, report=report, partial_score=score, muted=muted,
                            show_expected_value=False)


def assertIs(left, right, score=None, message=None, report=MAIN_REPORT, contextualize=True,
             label="assert_is", muted=False):
    """

    Args:
        left:
        right:
        score:
        message:
        report:
        contextualize:
    """
    raise NotImplementedError()


def assertIsNot(left, right, score=None, message=None, report=MAIN_REPORT, contextualize=True,
                label="assert_is_not", muted=False):
    """

    Args:
        left:
        right:
        score:
        message:
    """
    raise NotImplementedError()


def _actually_is_none(l, r):
    if is_sandbox_result(l):
        return l._actual_value is None
    return l is None


def assertIsNone(something, score=None, message=None, report=MAIN_REPORT,
                 contextualize=True, label="assert_is_none", muted=False):
    """

    Args:
        something:
        score:
        message:
        report:
        contextualize:

    Returns:

    """
    return _basic_assertion(label, "Value is not None", something, None,
                            _actually_is_none,
                            "{} is none",
                            "was",
                            "to be none",
                            message, contextualize, report=report, partial_score=score, muted=muted,
                            show_expected_value=False)


def _actually_is_not_none(l, r):
    if is_sandbox_result(l):
        return l._actual_value is not None
    return l is not None


def assertIsNotNone(something, score=None, message=None, report=MAIN_REPORT,
                    contextualize=True, label="assert_is_not_none", muted=False):
    """

    Args:
        something:
        score:
        message:
        report:
        contextualize:

    Returns:

    """
    return _basic_assertion(label, "Value is None", something, None,
                            _actually_is_not_none,
                            "{} is not none",
                            "was",
                            "to not be none",
                            message, contextualize, report=report, partial_score=score, muted=muted,
                            show_expected_value=False)


def assertIn(needle, haystack, score=None, message=None, report=MAIN_REPORT,
             contextualize=True, label="assert_in", muted=False):
    """

    Args:
        needle:
        haystack:
        score:
        message:
        report:
        contextualize:

    Returns:

    """
    expected_message = "to be in"
    if not is_sandbox_result(needle) and is_sandbox_result(haystack):
        expected_message = "to contain"
    return _basic_assertion(label, "Needle not in haystack", needle, haystack,
                            lambda n, h: n in h,
                            "{} not in {}",
                            "was",
                            expected_message,
                            message, contextualize, report=report, partial_score=score, muted=muted)


def assertNotIn(needle, haystack, score=None, message=None, report=MAIN_REPORT,
                contextualize=True, label="assert_not_in", muted=False):
    """

    Args:
        needle:
        haystack:
        score:
        message:
        report:
        contextualize:

    Returns:

    """
    expected_message = "to not be in"
    if not is_sandbox_result(needle) and is_sandbox_result(haystack):
        expected_message = "to not contain"
    return _basic_assertion(label, "Needle in haystack", needle, haystack,
                            lambda n, h: n not in h,
                            "{} in {}",
                            "was",
                            expected_message,
                            message, contextualize, report=report, partial_score=score, muted=muted)


def assertIsInstance(value, types, score=None, message=None, report=MAIN_REPORT,
                     contextualize=True, label="assert_is_instance", muted=False):
    """

    Args:
        value:
        types:
        score:
        message:
        report:
        contextualize:

    Returns:

    """
    return _basic_assertion(label, "Value is not of type", value, types,
                            lambda v, t: isinstance(v, t),
                            "isinstance({}, {})",
                            "was",
                            "to be of type",
                            message, contextualize, report=report, partial_score=score, muted=muted,
                            modify_right=humanize_types)


def assertNotIsInstance(value, types, score=None, message=None, report=MAIN_REPORT,
                        contextualize=True, label="assert_not_is_instance", muted=False):
    """

    Args:
        value:
        types:
    """
    return _basic_assertion(label, "Value is of the type", value, types,
                            lambda v, t: not isinstance(v, t),
                            "not isinstance({}, {})",
                            "was",
                            "to not be of type",
                            message, contextualize, report=report, partial_score=score, muted=muted,
                            modify_right=humanize_types)


def assertRaises(exception):
    """

    Args:
        exception:
    """
    raise NotImplementedError()


def assertRaisesRegexp(exception):
    """

    Args:
        exception:
    """
    raise NotImplementedError()


def assertAlmostEqual(left, right):
    """

    Args:
        left:
        right:
    """
    raise NotImplementedError()


def assertNotAlmostEqual(left, right):
    """

    Args:
        left:
        right:
    """
    raise NotImplementedError()


def assertGreater(left, right, score=None, message=None, report=MAIN_REPORT, muted=False,
                  contextualize=True, compare_lengths=None, label="assert_greater"):
    """

    Args:
        left:
        right:
        score:
        message:
        report:
        contextualize:
        compare_lengths:

    Returns:

    """
    if compare_lengths is None:
        compare_lengths = (iterable(left) and isinstance(right, (int, float)))
    return _basic_assertion(label, "Left is not greater than right", left, right,
                            lambda l, r:
                            len(l) > r if
                            compare_lengths else
                            l > r,
                            "len({}) <= {}" if compare_lengths else "{} <= {}",
                            "was",
                            "to have its length greater than"
                            if compare_lengths else
                            "to be greater than",
                            message, contextualize, report=report, partial_score=score, muted=muted)


def assertGreaterEqual(left, right, score=None, message=None, report=MAIN_REPORT, muted=False,
                       contextualize=True, compare_lengths=None, label="assert_greater_equal"):
    """

    Args:
        left:
        right:
        score:
        message:
        report:
        contextualize:
        compare_lengths:

    Returns:

    """
    if compare_lengths is None:
        compare_lengths = (iterable(left) and isinstance(right, (int, float)))
    return _basic_assertion(label, "Left is not greater or equal than right", left, right,
                            lambda l, r:
                            len(l) >= r if
                            compare_lengths else
                            l >= r,
                            "len({}) < {}" if compare_lengths else "{} < {}",
                            "was",
                            "to have its length greater than or equal to" if compare_lengths else
                            "to be greater than or equal to",
                            message, contextualize, report=report, partial_score=score, muted=muted)


def assertLess(left, right, score=None, message=None, report=MAIN_REPORT, muted=False,
               contextualize=True, compare_lengths=None, label="assert_less"):
    """

    Args:
        left:
        right:
        score:
        message:
        report:
        contextualize:
        compare_lengths:

    Returns:

    """
    if compare_lengths is None:
        compare_lengths = (iterable(left) and isinstance(right, (int, float)))
    return _basic_assertion(label, "Left is not less than right", left, right,
                            lambda l, r:
                            len(l) < r if
                            compare_lengths else
                            l < r,
                            "len({}) >= {}" if compare_lengths else "{} >= {}",
                            "was",
                            "to have its length less than"
                            if compare_lengths else
                            "to be less than",
                            message, contextualize, report=report, partial_score=score, muted=muted)


def assertLessEqual(left, right, score=None, message=None, report=MAIN_REPORT, muted=False,
                    contextualize=True, compare_lengths=None, label="assert_less_equal"):
    """

    Args:
        left:
        right:
        score:
        message:
        report:
        contextualize:
        compare_lengths:

    Returns:

    """
    if compare_lengths is None:
        compare_lengths = (iterable(left) and isinstance(right, (int, float)))
    return _basic_assertion(label, "Left is not less than or equal to right", left, right,
                            lambda l, r:
                            len(l) <= r if
                            compare_lengths else
                            l <= r,
                            "len({}) > {}" if compare_lengths else "{} > {}",
                            "was",
                            "to have its length less than or equal to" if compare_lengths else
                            "to be less than or equal to",
                            message, contextualize, report=report, partial_score=score, muted=muted)


def assertRegexpMatches(text, pattern):
    """

    Args:
        text:
        pattern:
    """
    raise NotImplementedError()


def assertNotRegexpMatches(text, pattern):
    """

    Args:
        text:
        pattern:
    """
    raise NotImplementedError()


def assertItemsEqual(left, right):
    """

    Args:
        left:
        right:
    """
    raise NotImplementedError()


def assertDictContainsSubset(left, right):
    """

    Args:
        left:
        right:
    """
    raise NotImplementedError()


def assertMultiLineEqual(left, right):
    """

    Args:
        left:
        right:
    """
    raise NotImplementedError()


def assertSequenceEqual(left, right):
    """

    Args:
        left:
        right:
    """
    raise NotImplementedError()


# TODO: assertPrintIncludes

# Speciality Asserts
def assertPrints(result, expected_output, args=None, returns=None,
                 score=None, message=None, report=MAIN_REPORT, muted=False,
                 contextualize=True, exact=False, label="assert_prints"):
    """

    Args:
        result:
        expected_output:
        args:
        returns:
        score:
        message:
        report:
        contextualize:
        exact:

    Returns:

    """
    if not isinstance(result, SandboxResult):
        return False
        #raise TypeError("You must pass in a SandboxResult (e.g., using `call`) to assertPrints")
    _setup_assertions(report)
    call_id = result._actual_call_id
    sandbox = result._actual_sandbox
    calls = sandbox.call_contexts[call_id]
    inputs = sandbox.input_contexts[call_id]
    actual_output = sandbox.output_contexts[call_id]
    if not output_test(actual_output, expected_output, exact):
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
        # TODO: Fix this!
        report.attach('Instructor Test', category='student', tool='Assertions',
                      mistake={'message': "Student code failed instructor test.<br>\n" +
                                          str(failure)})
        report['assertions']['failures'] += 1
        if report['assertions']['exceptions']:
            raise failure
        else:
            return False
    give_partial(score)
    return True


def assertHasFunction(obj, function, args=None, returns=None,
                      score=None, message=None, report=MAIN_REPORT, muted=False,
                      contextualize=True, exact=False, label="assert_has_function"):
    """

    Args:
        obj:
        function:
        args:
        returns:
        score:
        message:
        report:
        contextualize:
        exact:

    Returns:

    """
    # If object is a sandbox, will check the .data[variable] attribute
    # Otherwise, check it directly
    if isinstance(obj, DataSandbox):
        comparison = lambda o, f: f in o.data
    else:
        def comparison(o, f):
            """

            Args:
                o:
                f:

            Returns:

            """
            try:
                return f in o
            except:
                return hasattr(o, f)
    if not _basic_assertion(label, "Student object does not have function", obj, function,
                            comparison,
                            "Could not find function {}{}",
                            "was",
                            "to have the function",
                            message, contextualize=contextualize, report=report, partial_score=score, muted=muted):
        return False
    if isinstance(obj, DataSandbox):
        student_function = obj.data[function]
    else:
        try:
            student_function = obj[function]
        except:
            student_function = getattr(obj, function)
    if _basic_assertion(label, "Value is not a function", student_function, function,
                        lambda l, r: callable(l),
                        "The value {} is in the variable {}, and that value is not a callable function.",
                        "was callable",
                        "to be callable",
                        message, contextualize=contextualize, report=report, partial_score=score, muted=muted,
                        show_expected_value=False):
        give_partial(score)
        return True
    return False


def assertHas(obj, variable, types=None, value=None, score=None, muted=False,
              message=None, report=MAIN_REPORT, contextualize=True, label="assert_has"):
    """

    Args:
        obj:
        variable:
        types:
        value:
        score:
        message:
        report:
        contextualize:

    Returns:

    """
    # If object is a sandbox, will check the .data[variable] attribute
    # Otherwise, check it directly
    if isinstance(obj, DataSandbox):
        comparison = lambda o, v: v in o.data
    else:
        comparison = lambda o, v: v in hasattr(o, v)
    if not _basic_assertion(label, "Object does not have variable", obj, variable,
                            comparison,
                            "Could not find variable {}{}",
                            "was",
                            "to have the variable",
                            message, contextualize, report=report, partial_score=score, muted=muted):
        return False
    if isinstance(obj, DataSandbox):
        student_variable = obj.data[variable]
    else:
        student_variable = getattr(obj, variable)
    if types is not None:
        if not _basic_assertion(label, "Object's value does not have the right type", student_variable, types,
                                lambda v, t: isinstance(v, t),
                                "isinstance({}, {})",
                                "was",
                                "to be of type",
                                message, contextualize, report=report, partial_score=score, muted=muted,
                                modify_right=humanize_types):
            return False
    if value is not None:
        if not _basic_assertion(label, "Object is not equal to value", student_variable, value,
                                lambda l, r: equality_test(l, r, False, DELTA),
                                "{} != {}",
                                "was",
                                "to be equal to",
                                message, contextualize, report=report, partial_score=score, muted=muted,
                                show_expected_value=False):
            return False
    if report is None:
        report = MAIN_REPORT
    give_partial(score)
    return True


def assertGenerally(expression, score=None, message=None, report=MAIN_REPORT, muted=False,
                    contextualize=True, label="assert_generally"):
    """

    Args:
        expression:
        score:
        message:
        report:
        contextualize:

    Returns:

    """
    _setup_assertions(report)
    if expression:
        give_partial(score)
        return True
    else:
        report['assertions']['failures'] += 1
        if report['assertions']['exceptions']:
            raise AssertionException("General assertion")
        else:
            return False


# TODO: assertHasClass

# TODO: assertGraphType, assertGraphValues
assert_equal = assertEqual
assert_not_equal = assertNotEqual
assert_prints = assertPrints
