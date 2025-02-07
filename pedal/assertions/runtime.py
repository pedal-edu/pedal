"""
Runtime assertions.

TODO: assert_has_class
TODO: assertGraphType, assertGraphValues
TODO: assert_coverage
TODO: assert_ran (latest run produced no expections)


assert_equal
assert_not_equal
assert_less
assert_less_equal
assert_greater
assert_greater_equal
assert_in
assert_not_in
assert_contains_subset
assert_is
assert_is_not
assert_is_none
assert_is_dataclass
assert_is_not_dataclass
assert_true
assert_false
assert_length_equal
"""
import re

try:
    from dataclasses import _FIELDS
except Exception:
    _FIELDS = '__dataclass_fields__'

from pedal.assertions.feedbacks import (RuntimeAssertionFeedback,
                                        SandboxedValue, ExactValue,
                                        RuntimePrintingAssertionFeedback, AssertionFeedback, assert_group)
from pedal.assertions.functions import function_not_available, name_is_not_a_function
from pedal.core.report import MAIN_REPORT
from pedal.core.feedback import CompositeFeedbackFunction
from pedal.sandbox import Sandbox
from pedal.sandbox.commands import check_coverage, get_call_arguments, get_student_data, evaluate
from pedal.sandbox.result import share_sandbox_context, is_sandbox_result, unwrap_value
from pedal.types.normalize import normalize_type, get_pedal_type_from_value
from pedal.types.new_types import is_subtype
from pedal.utilities.comparisons import equality_test


def errors(*executions):
    for e in executions:
        if e.is_error:
            return True
    return False


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
    justification_template = ("Left ({left}) and right ({right}) were not equal",
                              "Left ({left}) and right ({right}) were equal")
    _expected_verb = "to be equal to"
    _aggregate_verb = "Expected"
    _inverse_operator = "!="

    def __init__(self, left, right, exact_strings=False, delta=DELTA, **kwargs):
        super().__init__(SandboxedValue(left), SandboxedValue(right),
                         exact_strings=exact_strings, delta=delta, **kwargs)

    def condition(self, left, right, exact_strings, delta):
        """ Tests if the left and right are equal """
        return errors(left, right) or not equality_test(left.value, right.value, exact_strings, delta)


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


class assert_is_dataclass(RuntimeAssertionFeedback):
    """
    Determine if the ``value`` is a dataclass.
    """
    justification = "Value does not evaluate to a dataclass"
    _expected_verb = "to evaluate to"
    _inverse_operator = "to not evaluate to"

    def __init__(self, value, **kwargs):
        super().__init__(SandboxedValue(value), ExactValue("a dataclass"), **kwargs)

    def condition(self, left, right):
        """ Tests if the left evaluates to true """
        return not hasattr(left.value, _FIELDS)


class assert_is_not_dataclass(RuntimeAssertionFeedback):
    """
    Determine if the ``value`` is not a dataclass.
    """
    justification = "Value does not evaluate to a dataclass"
    _expected_verb = "to not evaluate to"
    _inverse_operator = "to evaluate to"

    def __init__(self, value, **kwargs):
        super().__init__(SandboxedValue(value), ExactValue("a dataclass"), **kwargs)

    def condition(self, left, right):
        """ Tests if the left evaluates to true """
        return hasattr(left.value, _FIELDS)


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

    def condition(self, sequence, length, **kwargs):
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

    def condition(self, sequence, length, **kwargs):
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
        value = cls.value
        if value == int or value == float:
            value = (int, float)
        return not isinstance(obj.value, value)


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
        value = cls.value
        if value == int or value == float:
            value = (int, float)
        return isinstance(obj.value, value)


def type_to_pedal_type(expected_type):
    evaluated_expected_type = evaluate(expected_type) if isinstance(expected_type, str) else expected_type
    expected_pedal_type = normalize_type(evaluated_expected_type, evaluate)
    if not isinstance(expected_pedal_type, Exception):
        expected_pedal_type = expected_pedal_type.as_type()
        expected_pedal_type_name = expected_pedal_type.singular_name
    else:
        expected_pedal_type_name = ""
    return expected_pedal_type, expected_pedal_type_name


def value_to_pedal_type(value):
    if isinstance(unwrap_value(value), Exception):
        value_pedal_type = "An error"
    else:
        value_pedal_type = get_pedal_type_from_value(unwrap_value(value), evaluate)
    return value_pedal_type


class _compare_type(RuntimeAssertionFeedback):
    """
    TODO: Failing for assert_type({"test":1}, dict)
    """

    def __init__(self, value, expected_type, **kwargs):
        fields = kwargs.setdefault('fields', {})
        value_pedal_type = value_to_pedal_type(value)
        singular_name = share_sandbox_context(value_pedal_type if
                                              isinstance(value_pedal_type, str) else
                                              value_pedal_type.singular_name, value)
        expected_pedal_type, expected_pedal_type_name = type_to_pedal_type(expected_type)
        fields['value_raw'] = value
        fields['value_type'] = value_pedal_type
        fields['value_type_name'] = singular_name
        fields['expected_type_raw'] = expected_type
        fields['expected_type'] = expected_pedal_type
        fields['expected_type_name'] = expected_pedal_type_name
        super().__init__(SandboxedValue(singular_name),
                         SandboxedValue(expected_pedal_type_name), **kwargs)

    def condition(self, value, expected_type):
        """ Tests if the left and right are equal """
        value_type = self.fields['value_type']
        expected_type = self.fields['expected_type']
        return not is_subtype(value_type, expected_type)


class assert_type(_compare_type):
    """ Same as assert_is_instance, but has a slightly different wording. """
    justification = "Value is not of type"
    _expected_verb = ("to be a value of type", "to be the type of")
    _inverse_operator = "is a value of type"


class assert_not_type(_compare_type):
    justification = "Value is of type"
    _expected_verb = ("to not be a value of type", "to not be the type of")
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
        return re.search(regex.value, str(text.value)) is None


class assert_not_regex(RuntimeAssertionFeedback):
    """
    Determine if the ``regex`` does not match ``text``.
    """
    justification = "Regex matches text"
    _expected_verb = ("to not match the regex", "to not match the text")
    _inverse_operator = "matches the text"

    def __init__(self, regex, text, **kwargs):
        super().__init__(SandboxedValue(regex), SandboxedValue(text), **kwargs)

    def condition(self, regex, text):
        """ Tests if the regex does not match the text """
        return re.search(regex.value, str(text.value)) is not None


class assert_almost_equal(assert_equal):
    """ Test if the two values are almost equal; equivalent to assert_equal. """


class assert_not_almost_equal(assert_not_equal):
    """ Test if the two values are not almost equal; equivalent to
    assert_not_equal. """


class assert_output(RuntimePrintingAssertionFeedback):
    """
    Determine if the ``execution`` outputs ``text``. Uses the `==` operator to do the final comparison.
    In this case, you can think of the output as a single string with newlines, as opposed to a list
    of strings (i.e., it is retrieved with `raw_output`).

    If the `exact_strings` parameter is set to be `False`, then output is first normalized following
    this strategy:
    * Make strings lowercase
    * Remove all punctuation characters
    * Split the string by newlines into a list
    * Split each individual line by spaces (aka into words)
    * Remove all empty lines
    * Sorts the lines by default order

    So the default check will be fairly generous about checking output; as long as all the lines are
    there (in whatever order), ignoring punctuation and case, the text will be found.
    """
    justification = "Did not print the output"
    _expected_verb = "the output to be"
    _inverse_operator = "does not have the text"

    def condition(self, execution, text, exact_strings):
        """ Tests if the regex does not match the text """
        return errors(execution) or not equality_test(self.get_output(execution), str(text.value),
                                                      _exact_strings=exact_strings, _delta=None)


class assert_prints(assert_output):
    """ Deprecated version of assert_output """


class assert_not_output(RuntimePrintingAssertionFeedback):
    """
    Determine if the ``execution`` does not output ``text``. Simply the inverse of
    :py:func:`pedal.assertions.runtime.assert_output` so check the rules there for more information.
    """
    justification = "Printed the output"
    _expected_verb = "the output to not be"
    _inverse_operator = "has the text"

    def condition(self, execution, text, exact_strings):
        """ Tests if the regex does not match the text """
        return equality_test(self.get_output(execution), str(text.value),
                             _exact_strings=exact_strings, _delta=None)


class assert_output_contains(RuntimePrintingAssertionFeedback):
    """
    Determine if the ``execution`` outputs ``text`` anywhere. Unlike :py:func:`pedal.assertions.runtime.assert_output`,
    this function uses the `in` operator. If the `exact_strings` parameter is `False`, then both strings are only
    lowercased first (but the other normalization rules from `assert_output` are not applied). Can be a more flexible
    check since it just looks for whether the run of characters is ANYWHERE in the output. Remember that newlines are
    part of the output, though, so the check will not work across lines unless the `text` includes those newlines.
    """
    justification = "Did not contain the printed output"
    _expected_verb = "the output to contain"
    _inverse_operator = "does not contain the text"

    def condition(self, execution, text, exact_strings):
        """ Tests if the regex does not match the text """
        if not exact_strings:
            return str(text.value).lower() not in self.get_output(execution).lower()
        return str(text.value) not in self.get_output(execution)


class assert_not_output_contains(RuntimePrintingAssertionFeedback):
    """
    Determine if the ``execution`` outputs ``text``
    """
    justification = "Contained the printed output"
    _expected_verb = "the output to not contain"
    _inverse_operator = "contained the text"

    def condition(self, execution, text, exact_strings):
        """ Tests if the regex does not match the text """
        if not exact_strings:
            return str(text.value).lower() in self.get_output(execution).lower()
        return str(text.value) in self.get_output(execution)


class assert_output_regex(RuntimePrintingAssertionFeedback):
    """
    Determine if the ``execution`` output matches the given regex, similar to assert_output and assert_regex.
    """
    justification = "Did not print the output matching the regex"
    _expected_verb = "the output to match the regex"
    _inverse_operator = "does not match the text"

    def __init__(self, pattern, execution, exact_strings=False, **kwargs):
        super().__init__(execution, pattern,
                         exact_strings=exact_strings, **kwargs)

    def condition(self, execution, text, exact_strings):
        """ Tests if the regex does not match the text """
        return errors(execution) or re.search(str(text.value), self.get_output(execution)) is None


class assert_not_output_regex(RuntimePrintingAssertionFeedback):
    """
    Determine if the ``execution`` does not output ``text``. Simply the inverse of
    :py:func:`pedal.assertions.runtime.assert_output` so check the rules there for more information.
    """
    justification = "Printed the output matching the regex"
    _expected_verb = "the output to not match the regex"
    _inverse_operator = "matches the text"

    def __init__(self, pattern, execution, exact_strings=False, **kwargs):
        super().__init__(execution, pattern,
                         exact_strings=exact_strings, **kwargs)

    def condition(self, execution, text, exact_strings):
        """ Tests if the regex does not match the text """
        return re.search(str(text.value), self.get_output(execution)) is not None


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
        return coverage < at_least


class ensure_called_uniquely(AssertionFeedback):
    """
    Verifies that the most recent executed and traced student code has
    ``at_least`` called the given function uniquely that number of times.
    In other words, it prevents students from calling the same function repeatedly
    WITHOUT changing the arguments.

    TODO: Allow instructor to ignore certain collection of arguments
    TODO: Report how many calls it has seen so far.

    Args:
        function_name (str): The name of the function to check.
        at_least (int): The number of calls that have to have unique arguments
            between them.
        ignore (set[tuple]): A sequence of argument sets to ignore.
        why_ignored (str): If you want to explain why you are ignoring some of
            the tests, you can provide some text here. For example,
            `" because they overlap with examples you were given"`.
    """
    title = "You Must Test Your Code"
    message_template = ("You have not tested the function {function_name} enough. "
                        "You should test it at least {at_least} times. Each time you"
                        " test it, you should be using a new set of arguments."
                        " So far, you have called it {total_calls} times in total and"
                        " {unique_calls} times distinctively{instructor_ignore_message}.")

    def __init__(self, function_name, at_least=1, ignore=None, why_ignored="", **kwargs):
        report = kwargs.get("report", MAIN_REPORT)
        fields = kwargs.setdefault('fields', {})
        fields['function_name'] = function_name
        fields['at_least'] = at_least
        if ignore is None:
            ignore = set()
        else:
            ignore = set(ignore)
        fields['ignore'] = ignore
        calls = get_call_arguments(function_name, report)
        unique_calls = set([tuple(map(repr, args.values())) for args in calls])
        fields['instructor_ignored'] = instructor_ignored = len(unique_calls & ignore)
        if instructor_ignored:
            fields['instructor_ignore_message'] = f" (but your instructor did not count {instructor_ignored} of the tests{why_ignored})"
        else:
            fields['instructor_ignore_message'] = ""
        fields['total_calls'] = len(calls)
        unique_call_count = len(unique_calls - ignore)
        fields['unique_calls'] = unique_call_count
        super().__init__(unique_call_count, at_least, **kwargs)

    def condition(self, unique_call_count, at_least):
        return unique_call_count < at_least


@CompositeFeedbackFunction(function_not_available, name_is_not_a_function)
def ensure_function_callable(name, **kwargs):
    report = kwargs.get("report", MAIN_REPORT)
    values = get_student_data(report)
    # 2.1. Does the name exist in the values?
    if name not in values:
        return function_not_available(name, **kwargs)
    function_value = values[name]
    # 2.2. Is the name bound to a callable?
    if not callable(function_value):
        return name_is_not_a_function(name)

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
