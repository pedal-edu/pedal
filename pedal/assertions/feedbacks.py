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

from pedal.core.feedback import Feedback, FeedbackGroup
from pedal.core.feedback_category import FeedbackStatus
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
            context_id = value._actual_context_id
            sandbox = value._actual_sandbox
            self.context = sandbox.get_context(context_id)
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

    def __init__(self, feedback, exception=None):
        self.feedback = feedback
        self.exception = exception

    def __str__(self):
        exception_name = (self.exception.__class__.__name__
                          if self.exception is not None else "No Error")
        return f"AssertionBreak({self.feedback.label}, {exception_name})"


class AssertionFeedback(Feedback):
    """ Most basic assertion """
    title = "Failed Instructor Test"
    category = Feedback.CATEGORIES.SPECIFICATION
    valence = Feedback.NEGATIVE_VALENCE
    kind = Feedback.KINDS.CONSTRAINT
    assertion_status: str


class RuntimeAssertionFeedback(AssertionFeedback):
    """ Class for representing constraints asserted by an instructor """
    message_template = ("Student code failed instructor test.\n"
                        "{context_message}"
                        "{assertion_message}"
                        "{explanation}")
    # TODO: The explanation field is broken, because it's not a keyword parameter
    _expected_verb: str
    _aggregate_verb = "Expected"
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
            context_message = format_contexts(contexts, self.report.format)
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
        fields['left_boxed'] = left
        fields['right_boxed'] = right
        fields['contexts'] = contexts
        fields['expected_verb'] = self._expected_verb
        fields['aggregate_verb'] = self._aggregate_verb
        fields['inverse_operator'] = self._inverse_operator
        fields['context_message'] = context_message
        fields['assertion_message'] = assertion_message
        fields['explanation'] = explanation

        try:
            super().__init__(left, right, *args, **kwargs)
        except Exception as e:
            #if not hasattr(self, "_met_condition"):
            #    self._met_condition = False
            #    raise e
            parent = self.report.get_current_group()
            # TODO: Does this handle nested groups correctly?
            if parent is not None:
                if not parent.try_all:
                    raise AssertionBreak(self, e)
        if not self:
            if self.report[TOOL_NAME]['exceptions']:
                raise AssertionBreak(self)

    def get_sandbox_contexts(self, wrapped_values):
        """ Retrieve any sandbox contexts associated with these values. """
        contexts = []
        for wrapped_value in wrapped_values:
            if wrapped_value.is_sandboxed:
                contexts.append(wrapped_value.context)
            if isinstance(wrapped_value.value, Sandbox):
                run_contexts = wrapped_value.value.get_context()
                if run_contexts:
                    contexts.append(run_contexts)
        return contexts

    def _build_result_from_target(self, contexts, index):
        target = contexts[index][-1].target
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
        Returns:

        """
        # Handle whether either side had an error
        if left.is_error or right.is_error:
            # TODO:
            assertion = self.format_exception(left, right)
        # Handle the number of contexts
        elif not contexts:
            # TODO: Check if this is working correctly; might be wrapping in output weirdly
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
            actual_output = chomp(left.context[-1].output)
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
            return chomp(execution.context[-1].output)


"""
I ran your function `add` on some new arguments.
{I also entered some inputs of my own.}?
It passed X/Y tests.

|    | Arguments | Returned | Expected |
|----|-----------|----------|----------|
| ❌ |  1, 2     |   -1     |     3    |


What if they trigger an exception instead of producing a value? 

What if they assert_prints?
    Could be a separate table. Perhaps all the asserts get their own table?
    Yes, this would make a lot of sense. Then each table is adjusting their
        "Expected" column title as appropriate.
    And some tables want to also adjust their Returned column to be "Printed".
        And to also include the Input column, I suppose (although maybe
            that should happen automatically whenever you include inputs).
        Or perhaps it always tells you explicitly what was printed (if it's available?)
            I feel like that would be information overload.

    "Expected the output to be"

If you encounter an existing AssertionGroup feedback, concatenate it.

The final result is turned into a new AssertionFeedback that is placed before
    its composite children, to ensure that is given priority. Perhaps we should
    also mark certain feedback as "superseded" by others?

Group Manager:
    Keep track of current groups in a stack
    Groups have a name
    Also record
        Errors, failures, successes
            of each AssertionFeedback that occurs
    Two modes:
        Try all: Keep going even if you encounter an error or a failure.
        Fail on first: If you encounter any fails/errors, stop checking.
        
Automatically mutes/unscores any collected assertion feedbacks.

"""


class assert_group(AssertionFeedback, FeedbackGroup):
    """

    TODO: Decorator version

    """

    message_template = ("Student code failed instructor tests.\n"
                        "{summary_statistics}\n"
                        "{tables}")

    def __init__(self, name, try_all=True, **kwargs):
        super().__init__(delay_condition=True, **kwargs)
        self.name = name
        self.try_all = try_all
        self.successes = []
        self.failures = []
        self.errors = []
        self.all_feedback = []

    def __enter__(self):
        self.report.start_group(self)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Go through all my collected assertions
        # Count failures, errors, successes
        # If there are any non-successes, then produce a summary table.
        #   Otherwise produce a success within this group
        # Mute and unscore any feedbacks (use their scores though)
        self.report.stop_group(self)
        self.format_message()
        self.format_table()
        self._handle_condition()
        return False

    def _get_child_feedback(self, feedback, active):
        if isinstance(feedback, RuntimeAssertionFeedback):
            if feedback._status == FeedbackStatus.INACTIVE:
                self.successes.append(feedback)
            elif feedback._status == FeedbackStatus.ACTIVE:
                self.failures.append(feedback)
            elif feedback._status == FeedbackStatus.ERROR:
                self.errors.append(feedback)
            self.all_feedback.append(feedback)
        feedback.muted = True
        feedback.unscored = True

    def format_message(self):
        self.fields['failures'] = self.failures
        self.fields['errors'] = self.errors
        self.fields['successes'] = self.successes
        self.fields['failure_count'] = failure_count = len(self.failures)
        self.fields['error_count'] = error_count = len(self.errors)
        self.fields['success_count'] = success_count = len(self.successes)
        self.fields['total_count'] = total_count = len(self.all_feedback)
        self.fields['name'] = self.name
        self.fields['try_all'] = self.try_all

        stats = []
        stats.append(f"You passed {success_count}/{total_count} tests.\n")
        if error_count:
            stats.append(f"There were {error_count} errors.\n")
        self.fields['summary_statistics'] = "\n".join(stats)

    def format_table(self):
        # Group by their tables
        # TODO: left target, right target, expected_verb
        groups = {}
        for feedback in self.all_feedback:
            left = feedback.fields['left_boxed']
            right = feedback.fields['right_boxed']
            verb = feedback.fields['aggregate_verb']
            left_called = left.context[-1].called if left.context else None
            right_called = right.context[-1].called if right.context else None
            key = (left_called, right_called, verb)
            if key not in groups:
                groups[key] = []
            groups[key].append(feedback)

        # Actually build tables
        tables = []
        for (left_called, right_called, verb), feedbacks in groups.items():
            if left_called is None and right_called is None:
                continue
            # TODO: Handle left AND right called
            called = self.report.format.name(left_called or right_called)
            # TODO: Handle inputs, outputs
            columns = ["", "Arguments", "Returned", verb]
            rows = []
            for feedback in feedbacks:
                left = feedback.fields['left_boxed']
                right = feedback.fields['right_boxed']
                if left.context:
                    arguments = left.context[-1].args
                    actual, expected = str(left.value), str(right.value)
                else:
                    arguments = right.context[-1].args
                    actual, expected = str(right.value), str(left.value)
                if feedback._status == FeedbackStatus.INACTIVE:
                    outcome = self.report.format.check_mark()
                else:
                    outcome = self.report.format.negative_mark()
                rows.append([outcome, self.report.format.python_code(arguments), actual, expected])
            table = self.report.format.table(rows, columns)
            table = (f"I ran your function {called} on some new arguments."
                     f"{table}")
            tables.append(table)
        self.fields['tables'] = "\n".join(tables)

    def condition(self):
        """ Check that there are no errors or failures. """
        return self.errors or self.failures


"""
# Group a bunch of tests at the top level
with assert_group('add') as add_group:
    assert_equal(call('add', 1, 2), 3)
    assert_equal(call('add', 4, 5), 9)
    assert_equal(call('add', -4, -2), -6)

if add_group:
    pass


# Parameterize the tests
@assert_group('add')
def test_add(first_arg):
    assert_equal(call('add', first_arg, 2), first_arg + 3)
    assert_equal(call('add', first_arg, 5), first_arg + 9)
    assert_equal(call('add', first_arg, -2), first_arg + -6)
    assert_greater(call('add', first_arg, 3), 0)


if test_add(5) and test_add(-3):
    set_success()


def unit_test(function_name, *tests):
    with assert_group(function_name) as group:
        for test in tests:
            args, expected = test
            assert_equal(call(function_name, *args), expected)
    return group


if unit_test('add', [[1, 2], 3]):
    pass
"""
