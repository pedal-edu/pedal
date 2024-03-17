"""
Unifying collection of all the commands in ``pedal.assertions``.
"""
from pedal.core.commands import gently
from pedal.core.scoring import Score, combine_scores
from pedal.sandbox.commands import call, clear_student_data, run, get_sandbox, CommandBlock
from pedal.assertions.static import *
from pedal.assertions.runtime import *
from pedal.assertions.runtime import _FIELDS
from pedal.assertions.positive import close_output, correct_output
from pedal.types.new_types import is_subtype
from pedal.assertions.testing_libraries import *

try:
    from dataclasses import fields
except:
    fields = None


class unit_test(assert_group):
    justification_template = ("Some of the feedback in this group was triggered.",
                              "None of the feedback in this group was triggered.")

    def __init__(self, function_name, given_partial_credit=None, given_score=None, **kwargs):
        super().__init__(function_name, **kwargs)
        self.given_partial_credit = given_partial_credit
        self.given_score = given_score

    def __exit__(self, exc_type, exc_value, traceback):
        super().__exit__(exc_type, exc_value, traceback)
        if self.given_partial_credit is False:
            self.score = self.given_score
        else:
            self.valence = self.POSITIVE_VALENCE
            self.score = combine_scores([success.score for success in self.successes],
                                        [failure.score for failure in self.failures] +
                                        [error.score for error in self.errors])
        return False


_unit_test_class = unit_test


def unit_test(function, *tests, else_message=None, else_message_template=None,
              score=None, partial_credit=False,
              assert_function=None, context=None, **kwargs):
    """
    Helper function for quickly unit testing.

    * Specify exact score for each test case, individually | list[str]
    * Specify exact score for each test case, with single value | str
    * Specify total score for all test cases, no partial credit | False, using `score`
    * Specify total score for all test cases, divide by # of cases passed | True, using `score`

    Args:
        assert_function: Override the assert function (defaults to assert_equal)
        function (str): The name of the function to test.
        *tests (): The test cases to run. Each test case is a tuple of the input/output pairs.
        else_message (str): The message to present as a positive if the
             tests all pass.
        else_message_template (str): The template for the else_message, to be formatted.
        score (str): The score to give overall/per test case, depending on
            partial_credit.
        partial_credit (bool or str or list[str]): Whether to give credit for
            each unit test as a percentage of the whole (True), or to only give
            points for passing all the tests (False). Defaults to False.
            If a list is passed, those scores will be used per test case.
        context (Sandbox or CommandBlock): The context to run the function in.
        **kwargs ():

    Returns:

    """
    if assert_function is None:
        assert_function = assert_equal
    each_score = partial_credit_logic(tests, score, partial_credit)
    # Handle context
    if context is True:
        context = get_sandbox().get_context()
    elif context:
        if isinstance(context, Sandbox):
            context = context.get_context()
        elif isinstance(context, CommandBlock):
            context = context.context
        else:
            context = get_sandbox().get_context(context._actual_context_id)
    unit_test_context = _unit_test_class(function,
                                         else_message=else_message,
                                         else_message_template=else_message_template,
                                         context=context, given_partial_credit=partial_credit,
                                         given_score=score, **kwargs)
    if not tests:
        return unit_test_context
    # TODO: Make it so unit_test can document its cases
    with unit_test_context as group_result:
        for test_index, test in enumerate(tests):
            args, expected = test
            if isinstance(args, str):
                assert_function(call(function, args_locals=[args]), expected, score=each_score[test_index], **kwargs)
            else:
                assert_function(call(function, *args), expected, score=each_score[test_index], **kwargs)

    return not group_result


class check_dataclass_error(RuntimeAssertionFeedback):
    justification = "Value is not a dataclass"
    _expected_verb = "to be"
    _inverse_operator = "is not"

    def __init__(self, value, **kwargs):
        super().__init__(SandboxedValue(value), ExactValue("a dataclass"), **kwargs)

def check_dataclass_instance(value, dataclass, else_message=None, score=None, partial_credit=False, **kwargs):
    report = kwargs.get('report', MAIN_REPORT)
    name = dataclass.__name__
    # Check that we weren't given an error
    if isinstance(value, Exception):
        return check_dataclass_error(value, score=score, **kwargs)
        #return gently(f"I evaluated the name {report.format.name(name)} and expected the result to be a dataclass. "
        #              f"However, there was an error instead.",
        #              label="check_dataclass_error", score=score, **kwargs)
    # Get the students' instance as a Pedal Type
    value_pedal_type = get_pedal_type_from_value(unwrap_value(value), evaluate)
    # Convert the instructor's version to a Pedal type
    evaluated_expected_type = evaluate(dataclass) if isinstance(dataclass, str) else dataclass
    expected_pedal_type = normalize_type(evaluated_expected_type, evaluate)
    if not isinstance(expected_pedal_type, Exception):
        expected_pedal_type = expected_pedal_type.as_type()
        expected_pedal_type_name = expected_pedal_type.singular_name
    else:
        expected_pedal_type_name = ""
    # Make sure the students' version is an actual dataclass
    singular_name = share_sandbox_context(value_pedal_type.singular_name, value)
    if not hasattr(unwrap_value(value), _FIELDS):
        return check_dataclass_error(value, score=score, **kwargs)
        #return gently(f"I evaluated the name {report.format.name(name)} and expected the result to be a dataclass. "
        #              f"However, the result was a {report.format.python_expression(str(type(unwrap_value(value))))}",
        #              label="check_dataclass_missing", score=score, **kwargs)
    if not fields:
        return gently("Dataclasses are not supported in this version of Python", label="dataclasses_not_supported")
    # Now Check the fields
    actual_fields = {field.name: get_pedal_type_from_value(getattr(unwrap_value(value), field.name), evaluate) for field
                     in fields(unwrap_value(value))}
    expected_fields = {field.name: field.type for field in fields(dataclass)}
    # Number of fields
    expected_arity = len(expected_fields)
    actual_arity = len(actual_fields)
    if actual_arity < expected_arity:
        return too_few_fields(name, actual_arity, expected_arity, **kwargs)
    elif actual_arity > expected_arity:
        return too_many_fields(name, actual_arity, expected_arity, **kwargs)
    # Checks each field's name and type
    for actual_field_name, actual_field_type in actual_fields.items():
        if actual_field_name not in expected_fields:
            return unknown_field(name, actual_field_name, **kwargs)
        expected_field_type = expected_fields[actual_field_name]
        expected_field_type = normalize_type(expected_field_type, evaluate).as_type()
        try:
            actual_field_type = normalize_type(actual_field_type, evaluate).as_type()
        except ValueError as e:
            return invalid_field_type(name, actual_field_name, actual_field_type, expected_field_type, **kwargs)
        if not is_subtype(actual_field_type, expected_field_type):
            return wrong_fields_type(name, actual_field_name, actual_field_type,
                                     expected_field_type, **kwargs)
    return None


class wheat_chaff_game_class(assert_group):
    message_template = """
I ran your test cases against some of my own implementations of {name:name}.
I had {wheat_count} programs I expected to pass, and {chaff_count} programs I expected to fail.
{wheat_outcome}{chaff_outcome}
{wheat_names}{chaff_names}
"""

    def __init__(self, name, wheats, chaffs, **kwargs):
        super().__init__(name=name, **kwargs)
        self.wheats = wheats
        self.correct_wheats = []
        self.chaffs = chaffs
        self.correct_chaffs = []
        self.points = 0
        self.points_possible = 2
        self.fields['name'] = name
        self.fields['wheat_count'] = len(wheats)
        self.fields['chaff_count'] = len(chaffs)

    def __exit__(self, exc_type, exc_value, traceback):
        self.report.stop_group(self)
        self.format_message()
        self._handle_condition()
        return False

    def format_message(self):
        missing_wheats = len(self.wheats) - len(self.correct_wheats)
        if missing_wheats:
            self.fields['wheat_outcome'] = f"Your tests did not pass {missing_wheats} of my good programs.\n"
            names = "\n".join([name for name in self.wheats.keys() if name not in self.correct_wheats])
            self.fields[
                'wheat_names'] = "Here are the names for the good programs that incorrectly failed on your test cases:\n" + self.report.format.output(
                names) + "\n"
        else:
            self.fields['wheat_outcome'] = "Your tests passed all of my good programs.\n"
            self.fields['wheat_names'] = ""
        missing_chaffs = len(self.chaffs) - len(self.correct_chaffs)
        if missing_chaffs:
            self.fields['chaff_outcome'] = f"Your tests did not catch {missing_chaffs} of my bad programs.\n"
            names = "\n".join([name for name in self.chaffs.keys() if name not in self.correct_chaffs])
            self.fields[
                'chaff_names'] = "Here are the names for the bad programs that incorrectly passed your tests:\n" + self.report.format.output(
                names)
        else:
            self.fields['chaff_outcome'] = "At least one of your tests correctly failed for all of my bad programs.\n"
            self.fields['chaff_names'] = ""

    def wheat_outcome(self, wheat, success):
        if success:
            self.points += 1 / len(self.wheats)
            self.correct_wheats.append(wheat)

    def chaff_outcome(self, chaff, failure):
        if failure:
            self.points += 1 / len(self.chaffs)
            self.correct_chaffs.append(chaff)



    def condition(self):
        correct = len(self.correct_wheats) + len(self.correct_chaffs)
        possible = len(self.wheats) + len(self.chaffs)
        return correct < possible


def partial_credit_logic(cases, score, partial_credit):
    if isinstance(partial_credit, bool):
        if partial_credit:
            # Specify total score for all test cases, divide by # of cases passed | True, using `score`
            if score:
                return [str(Score.parse(score) / len(cases)) for case in cases]
            else:
                return [None for case in cases]
        else:
            # Specify total score for all test cases, no partial credit | False, using `score`
            return [None for case in cases]
    elif isinstance(partial_credit, (int, str, float)):
        # Specify exact score for each test case, with single value | str
        return [partial_credit for case in cases]
    else:
        # Specify exact score for each test case, individually | list[str]
        return partial_credit


def get_success_passed_failed_total_reason(student):
    student = get_student_data()
    if 'assert_equal' not in student:
        return False, 0, 0, 0, "Failed to import `assert_equal`"
    assert_equal = student['assert_equal']
    if not hasattr(assert_equal, 'student_tests'):
        return False, 0, 0, 0, "The `assert_equal` function has been modified."
    student_tests = assert_equal.student_tests
    return True, student_tests.successes, student_tests.failures, student_tests.tests, ''


def check_type_signature(function_name, function, type_signature, type_failures):
    if type_signature is None:
        return function

    def check_types(*args, **kwargs):
        if len(type_signature)-1 != len(args):
            type_failures.append(TypeError(f"Expected {len(type_signature)-1} arguments, but got {len(args)}"))
        for i, (arg, expected_type) in enumerate(zip(args, type_signature[:-1])):
            expected_type, _ = type_to_pedal_type(expected_type)
            arg = value_to_pedal_type(arg)
            if not is_subtype(arg, expected_type):
                type_failures.append(f"Argument {i} should be {expected_type}, but got {type(arg)}")
        result = function(*args, **kwargs)
        expected_type, _ = type_to_pedal_type(type_signature[-1])
        result_type = value_to_pedal_type(result)
        if not is_subtype(result_type, expected_type):
            type_failures.append(f"Expected return type of {expected_type}, but got {result_type}")
        return result

    return check_types


def wheat_chaff_game(function_name, wheats, chaffs,
                     else_message=None, score=None, partial_credit=True, type_signature=None,
                     **kwargs):
    report = kwargs.get('report', MAIN_REPORT)
    each_score = partial_credit_logic([0] * (len(wheats) + len(chaffs)), score, partial_credit)
    type_failures = []
    with wheat_chaff_game_class(function_name, wheats, chaffs, **kwargs) as group_result:
        sandbox = get_sandbox(report)
        last = 0
        for kind, iterator in [("wheat", wheats.items()), ("chaff", chaffs.items())]:
            for i, (name, wheat) in enumerate(iterator, start=last):
                clear_student_data()
                student = get_student_data(report)
                student[function_name] = check_type_signature(function_name, wheat, type_signature, type_failures)
                result = run(report=report, before='from bakery import assert_equal\nassert_equal.student_tests.reset()')
                success, passed, failed, total, reason = get_success_passed_failed_total_reason(result)
                if kind == 'wheat':
                    group_result.wheat_outcome(name, not sandbox.exception and not failed and success and passed)
                else:
                    group_result.chaff_outcome(name, sandbox.exception or failed or not success)
                if 'assert_equal' in student:
                    student['assert_equal'].student_tests.reset()
                last = i

    if type_failures:
        return gently(f"""I ran your test cases against some of my own implementations of {function_name}.
At least one of your tests had the wrong parameter or return type.
Make sure that all of your tests have valid types.""", label='wheat_chaff_game_types', title='Invalid Type for Test', **kwargs)
    if partial_credit is False:
        group_result.score = score
    else:
        group_result.valence = group_result.POSITIVE_VALENCE
        group_result.score = group_result.points / group_result.points_possible
    return not group_result
