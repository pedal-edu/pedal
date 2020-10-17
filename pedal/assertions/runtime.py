"""
Runtime assertions.

TODO: assert_has_class
TODO: assertGraphType, assertGraphValues
TODO: assert_coverage
TODO: assert_ran (latest run produced no expections)
"""
import re

from pedal.assertions.feedbacks import (RuntimeAssertionFeedback,
                                        SandboxedValue, ExactValue,
                                        RuntimePrintingAssertionFeedback, AssertionFeedback, assert_group)
from pedal.core.report import MAIN_REPORT
from pedal.sandbox import Sandbox
from pedal.sandbox.commands import check_coverage
from pedal.sandbox.result import share_sandbox_context
from pedal.types.normalize import normalize_type, get_pedal_type_from_value
from pedal.types.operations import are_types_equal
from pedal.utilities.comparisons import equality_test


class assert_equal(RuntimeAssertionFeedback):
    """
    Determine if the ``left`` and ``right`` values are equal.

    Args:
        exact_strings (bool): Whether to require that strings be exactly the
            same, for each character. If False (the default), then strings will
            be normalized (lowercased, trailing decimals chopped, punctuation
            removed, lines are flattened, and all characters are sorted).
        delta (float): When comparing floats, how close the values must be.
            If delta is None, then the default Delta will be used (.001).
    """
    DELTA = .001
    justification = "Left and right were not equal"
    _expected_verb = "to be equal to"
    _aggregate_verb = "Expected"
    _inverse_operator = "!="

    def __init__(self, left, right, exact_strings=False, delta=DELTA, **kwargs):
        super().__init__(SandboxedValue(left), SandboxedValue(right),
                         exact_strings=exact_strings, delta=delta, **kwargs)

    def condition(self, left, right, exact_strings, delta):
        """ Tests if the left and right are equal """
        return not equality_test(left.value, right.value, exact_strings, delta)


class assert_not_equal(RuntimeAssertionFeedback):
    """
    Determine if the ``left`` and ``right`` values are not equal.

    Args:
        exact_strings (bool): Whether to require that strings be exactly the
            same, for each character. If False (the default), then strings will
            be normalized (lowercased, trailing decimals chopped, punctuation
            removed, lines are flattened, and all characters are sorted).
        delta (float): When comparing floats, how close the values must be.
            If delta is None, then the default Delta will be used (.001).
    """
    DELTA = .001
    justification = "Left and right were equal"
    _expected_verb = "to not be equal to"
    _aggregate_verb = "Expected Anything But"
    _inverse_operator = "=="

    def __init__(self, left, right, exact_strings=False, delta=DELTA, **kwargs):
        super().__init__(SandboxedValue(left), SandboxedValue(right),
                         exact_strings=exact_strings, delta=delta, **kwargs)

    def condition(self, left, right, exact_strings, delta):
        """ Tests if the left and right are not equal """
        return equality_test(left.value, right.value, exact_strings, delta)


class assert_less(RuntimeAssertionFeedback):
    """
    Determine if the ``left`` is less than the ``right``.
    """
    justification = "Left is not less than right"
    _expected_verb = "to be less than"
    _inverse_operator = ">="

    def __init__(self, left, right, **kwargs):
        super().__init__(SandboxedValue(left), SandboxedValue(right), **kwargs)

    def condition(self, left, right):
        """ Tests if the left is greater or equal """
        return left.value >= right.value


class assert_less_equal(RuntimeAssertionFeedback):
    """
    Determine if the ``left`` is less than or equal to the ``right``.
    """
    justification = "Left is not less than or equal to the right"
    _expected_verb = "to be less than or equal to"
    _inverse_operator = ">"

    def __init__(self, left, right, **kwargs):
        super().__init__(SandboxedValue(left), SandboxedValue(right), **kwargs)

    def condition(self, left, right):
        """ Tests if the left is greater than the right """
        return left.value > right.value


class assert_greater(RuntimeAssertionFeedback):
    """
    Determine if the ``left`` is greater than the ``right``.
    """
    justification = "Left is not greater than right"
    _expected_verb = "to be greater than"
    _inverse_operator = "<="

    def __init__(self, left, right, **kwargs):
        super().__init__(SandboxedValue(left), SandboxedValue(right), **kwargs)

    def condition(self, left, right):
        """ Tests if the left is less than or equal to the right """
        return left.value <= right.value


class assert_greater_equal(RuntimeAssertionFeedback):
    """
    Determine if the ``left`` is greater than or equal to the ``right``.
    """
    justification = "Left is not greater than or equal to the right"
    _expected_verb = "to be greater than or equal to"
    _inverse_operator = "<"

    def __init__(self, left, right, **kwargs):
        super().__init__(SandboxedValue(left), SandboxedValue(right), **kwargs)

    def condition(self, left, right):
        """ Tests if the left is less than the right """
        return left.value < right.value


class assert_in(RuntimeAssertionFeedback):
    """
    Determine if the ``needle`` is in the ``haystack``.
    """
    justification = "Needle not in haystack"
    _expected_verb = ("to be in", "to contain")
    _inverse_operator = "not in"

    def __init__(self, needle, haystack, **kwargs):
        super().__init__(SandboxedValue(needle), SandboxedValue(haystack), **kwargs)

    def condition(self, needle, haystack):
        """ Tests if the needle is not in the haystack """
        return needle.value not in haystack.value


class assert_not_in(RuntimeAssertionFeedback):
    """
    Determine if the ``needle`` is in the ``haystack``.
    """
    justification = "Needle is in haystack"
    _expected_verb = ("to not be in", "to not contain")
    _inverse_operator = "in"

    def __init__(self, needle, haystack, **kwargs):
        super().__init__(SandboxedValue(needle), SandboxedValue(haystack), **kwargs)

    def condition(self, needle, haystack):
        """ Tests if the needle is in the haystack """
        return needle.value in haystack.value


class assert_contains_subset(RuntimeAssertionFeedback):
    """
    Determine if the ``needles`` are in the ``haystack``.
    """
    justification = "Needles not in haystack"
    _expected_verb = ("to be in", "to contain")
    _inverse_operator = "not in"

    def __init__(self, needles, haystack, **kwargs):
        super().__init__(SandboxedValue(needles), SandboxedValue(haystack), **kwargs)

    def condition(self, needles, haystack):
        """ Tests if the needle is not in the haystack """
        return not all(needle in haystack.value for needle in needles.value)


class assert_not_contains_subset(RuntimeAssertionFeedback):
    """
    Determine if the ``needles`` are not in the ``haystack``.
    """
    justification = "Needles in haystack"
    _expected_verb = ("to not be in", "to not contain")
    _inverse_operator = "in"

    def __init__(self, needles, haystack, **kwargs):
        super().__init__(SandboxedValue(needles), SandboxedValue(haystack), **kwargs)

    def condition(self, needles, haystack):
        """ Tests if the needle is not in the haystack """
        return all(needle in haystack.value for needle in needles.value)


class assert_is(RuntimeAssertionFeedback):
    """
    Determine if the ``left`` and ``right`` values are identical.
    """
    justification = "Left is not identical to right"
    _expected_verb = "to be identical to"
    _inverse_operator = "is not"

    def __init__(self, left, right, **kwargs):
        super().__init__(SandboxedValue(left), SandboxedValue(right), **kwargs)

    def condition(self, left, right):
        """ Tests if the left and right are equal """
        left = left.value._actual_value if left.is_sandboxed else left.value
        right = right.value._actual_value if right.is_sandboxed else right.value
        return left is not right


class assert_is_not(RuntimeAssertionFeedback):
    """
    Determine if the ``left`` and ``right`` values are not identical.
    """
    justification = "Left is identical to right"
    _expected_verb = "to not be identical to"
    _inverse_operator = "is"

    def __init__(self, left, right, **kwargs):
        super().__init__(SandboxedValue(left), SandboxedValue(right), **kwargs)

    def condition(self, left, right):
        """ Tests if the left and right are equal """
        left = left.value._actual_value if left.is_sandboxed else left.value
        right = right.value._actual_value if right.is_sandboxed else right.value
        return left is right


class assert_is_none(RuntimeAssertionFeedback):
    """
    Determine if the ``value`` is ``None``.
    """
    justification = "Value is not None"
    _expected_verb = "to be"
    _inverse_operator = "is not"

    def __init__(self, value, **kwargs):
        super().__init__(SandboxedValue(value), ExactValue("None"), **kwargs)

    def condition(self, left, right):
        """ Tests if the left and right are equal """
        if left.is_sandboxed:
            return left.value._actual_value is not None
        return left.value is not None


class assert_is_not_none(RuntimeAssertionFeedback):
    """
    Determine if the ``value`` is not ``None``.
    """
    justification = "Value is None"
    _expected_verb = "to not be"
    _inverse_operator = "is"

    def __init__(self, value, **kwargs):
        super().__init__(SandboxedValue(value), ExactValue("None"), **kwargs)

    def condition(self, left, right):
        """ Tests if the left and right are equal """
        if left.is_sandboxed:
            return left.value._actual_value is None
        return left.value is None


class assert_true(RuntimeAssertionFeedback):
    """
    Determine if the ``value`` is true.
    """
    justification = "Value does not evaluate to true"
    _expected_verb = "evaluates to"
    _inverse_operator = "does not evaluate to"

    def __init__(self, value, **kwargs):
        super().__init__(SandboxedValue(value), ExactValue("a true value"), **kwargs)

    def condition(self, left, right):
        """ Tests if the left evaluates to true """
        return not bool(left.value)


class assert_false(RuntimeAssertionFeedback):
    """
    Determine if the ``value`` is false.
    """
    justification = "Value does not evaluate to false"
    _expected_verb = "evaluates to"
    _inverse_operator = "does not evaluate to"

    def __init__(self, value, **kwargs):
        super().__init__(SandboxedValue(value), ExactValue("a true value"), **kwargs)

    def condition(self, left, right):
        """ Tests if the left evaluates to true """
        return bool(left.value)


class assert_length_equal(RuntimeAssertionFeedback):
    """
    Determine if the ``sequence`` has the ``length``.
    """
    justification = "Sequence does not have length"
    _expected_verb = ("to have the length", "to be the length of")
    _inverse_operator = "did not have the length"

    def __init__(self, sequence, length, **kwargs):
        super().__init__(SandboxedValue(sequence), SandboxedValue(length), **kwargs)

    def condition(self, sequence, length):
        """ Tests if the needle is not in the haystack """
        return len(sequence.value) != length.value


class assert_length_not_equal(RuntimeAssertionFeedback):
    """
    Determine if the ``sequence`` does not have the ``length``.
    """
    justification = "Sequence has length"
    _expected_verb = ("to not have the length", "to not be the length of")
    _inverse_operator = "had the length"

    def __init__(self, sequence, length, **kwargs):
        super().__init__(SandboxedValue(sequence), SandboxedValue(length), **kwargs)

    def condition(self, sequence, length):
        """ Tests if the needle is not in the haystack """
        return len(sequence.value) == length.value


class assert_length_less(RuntimeAssertionFeedback):
    """
    Determine if the ``sequence`` has less than the ``length``.
    """
    justification = "Sequence length is less than"
    _expected_verb = ("to have length less than", "to be less than the length of")
    _inverse_operator = "did not have less than the length"

    def __init__(self, sequence, length, **kwargs):
        super().__init__(SandboxedValue(sequence), SandboxedValue(length), **kwargs)

    def condition(self, sequence, length):
        """ Tests if the needle is not in the haystack """
        return len(sequence.value) >= length.value


class assert_length_less_equal(RuntimeAssertionFeedback):
    """
    Determine if the ``sequence`` has less or equal than the ``length``.
    """
    justification = "Sequence length is less than or equal to"
    _expected_verb = ("to have length less than or equal to",
                      "to be less than or equal to the length of")
    _inverse_operator = "did not have less than or equal to the length"

    def __init__(self, sequence, length, **kwargs):
        super().__init__(SandboxedValue(sequence), SandboxedValue(length), **kwargs)

    def condition(self, sequence, length):
        """ Tests if the needle is not in the haystack """
        return len(sequence.value) > length.value


class assert_length_greater(RuntimeAssertionFeedback):
    """
    Determine if the ``sequence`` has greater than the ``length``.
    """
    justification = "Sequence length is greater than"
    _expected_verb = ("to have length greater than", "to be greater than the length of")
    _inverse_operator = "did not have greater than the length"

    def __init__(self, sequence, length, **kwargs):
        super().__init__(SandboxedValue(sequence), SandboxedValue(length), **kwargs)

    def condition(self, sequence, length):
        """ Tests if the needle is not in the haystack """
        return len(sequence.value) <= length.value


class assert_length_greater_equal(RuntimeAssertionFeedback):
    """
    Determine if the ``sequence`` has greater than or equal to the ``length``.
    """
    justification = "Sequence length is greater than or equal to"
    _expected_verb = ("to have length greater than or equal to",
                      "to be greater than or equal to the length of")
    _inverse_operator = "did not have greater than or equal to the length"

    def __init__(self, sequence, length, **kwargs):
        super().__init__(SandboxedValue(sequence), SandboxedValue(length), **kwargs)

    def condition(self, sequence, length):
        """ Tests if the needle is not in the haystack """
        return len(sequence.value) < length.value


class assert_is_instance(RuntimeAssertionFeedback):
    """
    Determine if the ``obj`` is an instance of ``cls``
    """
    justification = "Object is not an instance of class"
    _expected_verb = ("to be an instance of", "to be the type of")
    _inverse_operator = "is not an instance of"

    def __init__(self, obj, cls, **kwargs):
        super().__init__(SandboxedValue(obj), SandboxedValue(cls), **kwargs)

    def condition(self, obj, cls):
        """ Tests if the left and right are equal """
        return not isinstance(obj.value, cls.value)


class assert_not_is_instance(RuntimeAssertionFeedback):
    """
    Determine if the ``obj`` is an instance of ``cls``
    """
    justification = "Object is an instance of class"
    _expected_verb = ("to not be an instance of", "to not be the type of")
    _inverse_operator = "is an instance of"

    def __init__(self, obj, cls, **kwargs):
        super().__init__(SandboxedValue(obj), SandboxedValue(cls), **kwargs)

    def condition(self, obj, cls):
        """ Tests if the left and right are equal """
        return isinstance(obj.value, cls.value)


class _compare_type(RuntimeAssertionFeedback):
    """
    TODO: Failing for assert_type({"test":1}, dict)
    """

    def __init__(self, value, expected_type, **kwargs):
        fields = kwargs.setdefault('fields', {})
        value_pedal_type = get_pedal_type_from_value(value)
        expected_pedal_type = normalize_type(expected_type)
        singular_name = share_sandbox_context(value_pedal_type.singular_name, value)
        fields['value_raw'] = value
        fields['value_type'] = value_pedal_type
        fields['value_type_name'] = singular_name
        fields['expected_type_raw'] = expected_type
        fields['expected_type'] = expected_pedal_type
        fields['expected_type_name'] = expected_pedal_type.singular_name
        super().__init__(SandboxedValue(singular_name),
                         SandboxedValue(expected_pedal_type.singular_name), **kwargs)

    def condition(self, value, expected_type):
        """ Tests if the left and right are equal """
        value_type = self.fields['value_type']
        expected_type = self.fields['expected_type']
        return not are_types_equal(value_type, expected_type)


class assert_type(_compare_type):
    """ Same as assert_is_instance, but has a slightly different wording. """
    justification = "Value is not of type"
    _expected_verb = ("to not be a value of type", "to not be the type of")
    _inverse_operator = "is a value of type"


class assert_not_type(_compare_type):
    justification = "Value is of type"
    _expected_verb = ("to be a value of type", "to be the type of")
    _inverse_operator = "is not a value of type"

    def condition(self, value, expected_type):
        return not super().condition(value, expected_type)


class assert_regex(RuntimeAssertionFeedback):
    """
    Determine if the ``regex`` matches ``text``.
    """
    justification = "Regex does not match text"
    _expected_verb = ("to be matched by the regex", "to match the text")
    _inverse_operator = "does not match the text"

    def __init__(self, regex, text, **kwargs):
        super().__init__(SandboxedValue(regex), SandboxedValue(text), **kwargs)

    def condition(self, regex, text):
        """ Tests if the regex matches the text """
        return re.search(regex.value, text.value) is None


class assert_not_regex(RuntimeAssertionFeedback):
    """
    Determine if the ``regex`` does not match ``text``.
    """
    justification = "Regex matches text"
    _expected_verb = ("to not match the regex", "to not match the text")
    _inverse_operator = "matches the text"

    def __init__(self, regex, text, **kwargs):
        super().__init__(SandboxedValue(regex.value), SandboxedValue(text.value), **kwargs)

    def condition(self, regex, text):
        """ Tests if the regex does not match the text """
        return re.search(regex, text) is not None


class assert_almost_equal(assert_equal):
    """ Test if the two values are almost equal; equivalent to assert_equal. """


class assert_not_almost_equal(assert_not_equal):
    """ Test if the two values are not almost equal; equivalent to
    assert_not_equal. """


class assert_output(RuntimePrintingAssertionFeedback):
    """
    Determine if the ``execution`` outputs ``text``
    """
    justification = "Did not print the output"
    _expected_verb = "the output to be"
    _inverse_operator = "does not have the text"

    def condition(self, execution, text, exact_strings):
        """ Tests if the regex does not match the text """
        return not equality_test(self.get_output(execution), text.value,
                                 _exact_strings=exact_strings, _delta=None)


class assert_prints(assert_output):
    """ Deprecated version of assert_output """


class assert_not_output(RuntimePrintingAssertionFeedback):
    """
    Determine if the ``execution`` does not output ``text``
    """
    justification = "Printed the output"
    _expected_verb = "the output to not be"
    _inverse_operator = "has the text"

    def condition(self, execution, text, exact_strings):
        """ Tests if the regex does not match the text """
        return equality_test(self.get_output(execution), text.value,
                             _exact_strings=exact_strings, _delta=None)


class assert_output_contains(RuntimePrintingAssertionFeedback):
    """
    Determine if the ``execution`` outputs ``text``
    """
    justification = "Did not contain the printed output"
    _expected_verb = "the output to contain"
    _inverse_operator = "does not contain the text"

    def condition(self, execution, text, exact_strings):
        """ Tests if the regex does not match the text """
        return text.value not in self.get_output(execution)


class assert_not_output_contains(RuntimePrintingAssertionFeedback):
    """
    Determine if the ``execution`` outputs ``text``
    """
    justification = "Contained the printed output"
    _expected_verb = "the output to not contain"
    _inverse_operator = "contained the text"

    def condition(self, execution, text, exact_strings):
        """ Tests if the regex does not match the text """
        return text.value in self.get_output(execution)


class assert_has_attr(RuntimeAssertionFeedback):
    """
    Determine if the ``object`` has the ``name``
    """
    justification = "Contained the attribute"
    _expected_verb = "the object to contain"
    _inverse_operator = "did not contain"

    def condition(self, obj, attr, exact_strings):
        """ Tests if the regex does not match the text """
        return hasattr(obj.value, attr.value)


class assert_has_variable(RuntimeAssertionFeedback):
    """
    Determine if the student's data has the name.
    """
    _expected_verb = "to contain the variable"
    _inverse_operator = "does not contain the variable"

    def __init__(self, sandbox, variable_name, **kwargs):
        super().__init__(SandboxedValue(sandbox),
                         ExactValue(variable_name), **kwargs)

    def format_assertion(self, sandbox, variable_name, contexts):
        variable_name = variable_name.value
        return f"The variable {variable_name} was not created."


    def condition(self, sandbox, variable_name):
        sandbox = sandbox.value
        variable_name = variable_name.value
        if isinstance(sandbox, Sandbox):
            return variable_name not in sandbox.data
        elif isinstance(sandbox, dict):
            return variable_name not in sandbox
        else:
            return True


class assert_has_function(RuntimeAssertionFeedback):
    """
    Determine if the student's code has the function.
    """
    _expected_verb = "to contain the function"
    _inverse_operator = "does not contain the function"

    def __init__(self, sandbox, function_name, **kwargs):
        super().__init__(SandboxedValue(sandbox),
                         ExactValue(function_name), **kwargs)

    def format_assertion(self, sandbox, function_name, contexts):
        sandbox = sandbox.value
        function_name = function_name.value
        if isinstance(sandbox, Sandbox):
            return "Sandbox does not contain the function."
        else:
            return "The result does not contain the function."

    def condition(self, sandbox, function_name):
        sandbox = sandbox.value
        function_name = function_name.value
        if isinstance(sandbox, Sandbox):
            function = sandbox.data.get(function_name, None)
        elif isinstance(sandbox, dict):
            function = sandbox.get(function_name, None)
        elif hasattr(sandbox, function_name):
            function = getattr(sandbox, function_name)
        else:
            function = None
        return not callable(function)


# TODO: This one is at Runtime, but is not an assertion... Should these be "tests"?

class ensure_coverage(AssertionFeedback):
    """
    Verifies that the most recent executed and traced student code has
    ``at_least`` the given ratio of covered (executed) lines.

    Args:
        at_least (float): The ratio of covered lines. A value of 1.0 is all
            lines covered, 0.0 is no lines covered, and .5 is half the lines
            covered.
    """
    title = "You Must Test Your Code"
    message_template = ("Your code coverage is not adequate. You must cover at "
                        "least {at_least_message}% of your code to receive "
                        "feedback. So far, you have only covered "
                        "{coverage_message}%.")

    def __init__(self, at_least=.5, **kwargs):
        report = kwargs.get("report", MAIN_REPORT)
        fields = kwargs.setdefault('fields', {})
        fields['at_least'] = at_least
        fields['at_least_message'] = str(int(round(100*at_least)))
        unexecuted_lines, coverage = check_coverage(report)
        fields['unexecuted_lines'] = unexecuted_lines
        fields['coverage'] = coverage
        fields['coverage_message'] = str(int(round(100*coverage)))
        super().__init__(coverage, at_least, **kwargs)

    def condition(self, coverage, at_least):
        return coverage <= at_least


# Alias conventional camel-case names to our functions

assertEqual = assert_equal
assertNotEqual = assert_not_equal
assertLess = assert_less
assertLessEqual = assert_less_equal
assertGreater = assert_greater
assertGreaterEqual = assert_greater_equal
assertLengthEqual = assert_length_equal
assertLengthNotEqual = assert_length_not_equal
assertLengthLess = assert_length_less
assertLengthLessEqual = assert_length_less_equal
assertLengthGreater = assert_length_greater
assertLengthGreaterEqual = assert_length_greater_equal
assertIn = assert_in
assertNotIn = assert_not_in
assertIs = assert_is
assertIsNot = assert_is_not
assertIsNone = assert_is_none
assertIsNotNone = assert_is_not_none
assertTrue = assert_true
assertFalse = assert_false
assertIsInstance = assert_is_instance
assertIsNotInstance = assert_not_is_instance
assertAlmostEqual = assert_equal
assertNotAlmostEqual = assert_not_equal
assertRegex = assert_regex
assertNotRegex = assert_not_regex
assertPrints = assert_prints
assertOutput = assert_output
assertNotOutput = assert_not_output
assertOutputContains = assert_output_contains
assertNotOutputContains = assert_not_output_contains
assertHasAttr = assert_has_attr
assertHasFunction = assert_has_function
assertHasVariable = assert_has_variable
assertType = assert_type
assertNotType = assert_not_type
