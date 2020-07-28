"""
List of features to test:

* Setting context_message and assertion_message to False
* Setting context_message and assertion_message to strings
* Setting explanation to be a non-empty string

* Testing at top-level
* Testing within a function
* Testing within a subtest

* Testing call() on both sides
* Testing call() on either side
* Testing no call()

Two sandboxed results:
    The value of `{first_name}` was:\n<pre>{first_value}</pre>
    The value of `{second_name}` was:\n<pre>{second_value}</pre>
    But I expected `{first_name}` to be equal to `{second_name}`.
One sandboxed result:
    The value of `{first_name}` was:\n<pre>{first_value}</pre>
    But I expected `{first_name}` to be equal to:\n<pre>{expected_value}</pre>
No sandbox result:
    <pre>{first_value} != {expected_value}</pre>



assert_not_equal(call('add', 5, 4), 1,
                 context = None, assertion = None,
                 explanation="Your add function is subtracting.",
                 label="test_add_but_subtracted_5_4")

assert_equal(call('add', 5, 4), 9,
             explanation="You added incorrectly."
             label="test_add_5_4")


"""

from pedal.core.feedback import Feedback
from pedal.core.report import MAIN_REPORT
from pedal.sandbox import Sandbox
from pedal.sandbox.data import format_contexts
from pedal.sandbox.result import is_sandbox_result
from pedal.assertions.constants import TOOL_NAME
from pedal.utilities.text import chomp


class InterpolatedValue:
    """ Abstract wrapper around asserted values to handle different ways
    of printing them. """

    def __init__(self, value):
        self.value = value
        self.is_sandboxed = is_sandbox_result(value)
        self.is_error = not self.is_sandboxed and isinstance(value, Exception)
        self.report = MAIN_REPORT
        if self.is_sandboxed:
            call_id = value._actual_call_id
            sandbox = value._actual_sandbox
            self.context = sandbox._context[call_id]
        else:
            self.context = None

    def set_report(self, report):
        """ Update the report on this value. """
        self.report = report


class ExactValue(InterpolatedValue):
    """ Wrapper around literal values to produce them unmodified. """

    def __str__(self):
        return " "+str(self.value)


class SandboxedValue(InterpolatedValue):
    """ Wrapper around sandboxed values to preformat their text. """

    def __str__(self):
        return ":\n"+self.report.format.python_value(repr(self.value))


class AssertionBreak(Exception):
    """
    Exception that can be raised to exit out of an assertion, jumping control
    flow around subsequent checks.
    """

    def __init__(self, feedback):
        self.feedback = feedback

    def __str__(self):
        return str(self.feedback.label)


class AssertionFeedback(Feedback):
    """ Most basic assertion """
    category = Feedback.CATEGORIES.SPECIFICATION
    valence = Feedback.NEGATIVE_VALENCE
    kind = Feedback.KINDS.CONSTRAINT


class RuntimeAssertionFeedback(AssertionFeedback):
    """ Class for representing constraints asserted by an instructor """
    message_template = ("Student code failed instructor test.\n"
                        "{context_message}"
                        "{assertion_message}"
                        "{explanation}")
    _expected_verb: str
    _inverse_operator: str

    def __init__(self, left, right, *args, **kwargs):
        self.report = kwargs.get('report', MAIN_REPORT)
        left.set_report(self.report)
        right.set_report(self.report)
        # Get contexts
        contexts = self.get_sandbox_contexts([left, right])
        # Calculate the context_message
        if kwargs.get('context') is False:
            context_message = ""
        elif kwargs.get('context') is not None:
            context_message = kwargs['context']
        else:
            context_message = format_contexts(contexts)
        # Calculate the assertion_message
        if kwargs.get('assertion') is False:
            assertion_message = ""
        elif kwargs.get('assertion') is not None:
            assertion_message = kwargs['assertion'] + "\n"
        else:
            assertion_message = self.format_assertion(left, right, contexts)
        # Calculate explanation
        explanation = kwargs.get("explanation", "")
        # Add in new fields
        fields = kwargs.setdefault('fields', {})
        fields['left'] = left.value
        fields['right'] = right.value
        fields['contexts'] = contexts
        fields['expected_verb'] = self._expected_verb
        fields['inverse_operator'] = self._inverse_operator
        fields['context_message'] = context_message
        fields['assertion_message'] = assertion_message
        fields['explanation'] = explanation
        try:
            super().__init__(left, right, *args, **kwargs)
        except Exception as e:
            self.report[TOOL_NAME]['errors'] += 1
            if self.report[TOOL_NAME]['exceptions']:
                raise AssertionBreak(self, e)
        if not self:
            self.report[TOOL_NAME]['failures'] += 1
            if self.report[TOOL_NAME]['exceptions']:
                raise AssertionBreak(self)

    def get_sandbox_contexts(self, wrapped_values):
        """ Retrieve any sandbox contexts associated with these values. """
        contexts = []
        for wrapped_value in wrapped_values:
            if wrapped_value.is_sandboxed:
                contexts.append(wrapped_value.context)
        return contexts

    def _build_result_from_target(self, contexts, index):
        target = contexts[index].target
        if target == "_" or target is None:
            if len(contexts) == 1:
                return "the result"
            elif index == 0:
                return "the first result"
            else:
                return "the second result"
        return self.report.format.name(target)

    def format_assertion(self, left, right, contexts):
        """
        Creates a textual explanation of the difference between left and right,
        using any targets from the contexts. The ``expected_verb`` is the
        human-friendly description of the comparison being made between the two
        sides, while ``inverse_operator`` is the actual comparison that was
        performed.

        Args:
            left (InterpolatedValue):
            right (InterpolatedValue):
            contexts (list[:py:class:`pedal.sandbox.data.SandboxContext`]):
            expected_verb (str):
            inverse_operator (str):
        Returns:

        """
        # Handle whether either side had an error
        if left.is_error or right.is_error:
            # TODO:
            assertion = self.format_exception(left, right)
        # Handle the number of contexts
        elif not contexts:
            assertion = self.report.format.output(f"{left.value} "
                                                  f"{self._inverse_operator} "
                                                  f"{right.value}")
        elif len(contexts) == 1:
            # If the expected_verb is a tuple, the right side's value is used
            #   to determine which of the two possible messages should be used.
            #   If the right side is a sandboxed value, uses the second; else the first.
            _expected_verb = self._expected_verb
            if isinstance(_expected_verb, tuple):
                relevant_index = int(right.is_sandboxed)
                _expected_verb = _expected_verb[relevant_index]
            # Make sure ``left`` is the sandbox result
            if right.is_sandboxed:
                left, right = right, left
            target = self._build_result_from_target(contexts, 0)
            assertion = (f"The value of {target} was{left}\n"
                         f"But I expected {target} {_expected_verb}{right}")
        elif len(contexts) == 2:
            first_target = self._build_result_from_target(contexts, 0)
            second_target = self._build_result_from_target(contexts, 1)
            assertion = (f"The value of {first_target} was{left}\n"
                         f"The value of {second_target} was{right}\n"
                         f"But I expected {first_target} {self._expected_verb}{second_target}")
        else:
            # Invalid state, why'd you have 3+ contexts?
            assertion = ""
        return assertion

    def format_exception(self, left, right):
        """ Create a simple formatted exception message """
        assertion = "The following exception occurred:\n"
        if left.is_error:
            assertion += self.report.format.output(str(left.value))
        if right.is_error:
            assertion += self.report.format.output(str(right.value))
        return assertion


class RuntimePrintingAssertionFeedback(RuntimeAssertionFeedback):
    """ Variant for handling printing instead of return value"""

    def __init__(self, execution, text, exact_strings=False, **kwargs):
        super().__init__(SandboxedValue(execution), SandboxedValue(text),
                         exact_strings=exact_strings, **kwargs)

    def format_assertion(self, left, right, contexts):
        """
        Overrides the regular format_assertion to write better descriptions
        of the text.
        """
        # Handle whether either side had an error
        if left.is_error or right.is_error:
            assertion = self.format_exception(left, right)
        # Sandbox
        if isinstance(left.value, Sandbox):
            actual_output = chomp(left.value.raw_output)
            if not actual_output:
                actual = "There was no printed output."
                actual_output = ""
            else:
                actual = "The printed output was:"
                actual_output = self.report.format.output(actual_output)
        # Sandboxed value
        else:
            actual_output = chomp(left.context.output)
            if not actual_output:
                actual = "The function did not print."
                actual_output = ""
            else:
                actual = "The function printed:"
                actual_output = self.report.format.output(actual_output)
        # Get the expected
        expected = f"But I expected {self._expected_verb}:"
        expected_output = self.report.format.output(right.value)
        # Join everything
        return "\n".join((actual, actual_output, expected, expected_output))

    def get_output(self, execution):
        """ Get the actual output from the execution"""
        if isinstance(execution.value, Sandbox):
            return chomp(execution.value.raw_output)
        # Sandboxed value
        else:
            return chomp(execution.context.output)
