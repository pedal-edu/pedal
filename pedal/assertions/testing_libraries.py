"""
Assertions for working with various testing libraries. Currently we support:
- bakery (formerly known as cisc106.py and cisc108.py)

We do intend to add more support as people request. If you have a testing
library that you would like to see supported, please open an issue on GitHub!

# TODO: At least support the builtin unittest library.
"""

from pedal.core.feedback import CompositeFeedbackFunction
from pedal.core.commands import gently
from pedal.sandbox.commands import get_student_data

# TODO: Decompose these with a helper function that parameterizes these fields.


@CompositeFeedbackFunction()
def ensure_cisc108_tests(test_count, **kwargs):
    """
    Ensure that the student has not failed their own tests.
    This is for the specific ``cisc108`` library, not the general unittest
    library.
    """
    student = get_student_data()
    if 'assert_equal' not in student:
        return gently(f"You have not imported assert_equal from the cisc108 module.",
               label=f"missing_cisc108_assert_equal",
               title="Missing assert_equal", **kwargs)
    assert_equal = student['assert_equal']
    if not hasattr(assert_equal, 'student_tests'):
        return gently("The assert_equal function has been modified. Do not let it be overwritten!",
               label="overwrote_assert_equal",
               title="Overwrote assert_equal", **kwargs)
    student_tests = assert_equal.student_tests
    if student_tests.tests == 0:
        return gently("You are not unit testing the result.",
                      title="No Student Unit Tests",
                      label="no_student_tests", **kwargs)
    elif student_tests.tests < test_count:
        return gently("You have not written enough unit tests.",
                      label="not_enough_tests",
                      title="Not Enough Student Unit Tests", **kwargs)
    elif student_tests.failures > 0:
        failures = student_tests.failures
        successes = student_tests.successes
        tests = student_tests.tests
        return gently(f"{failures}/{tests} of your unit tests are not passing.",
                      label="failing_student_tests",
                      title="Student Unit Tests Failing",
                      fields={'failures': failures, 'successes': successes,
                              'tests': tests},
                      **kwargs)
    return False


@CompositeFeedbackFunction()
def ensure_cisc106_tests(test_count, **kwargs):
    """
    Ensure that the student has not failed their own tests.
    This is for the specific ``cisc106`` library, not the general unittest
    library.
    """
    student = get_student_data()
    if 'assertEqual' not in student:
        return gently("You have not imported assertEqual from the cisc106 module.",
               label="missing_cisc106_assertEqual",
               title="Missing assertEqual", **kwargs)
    assertEqual = student['assertEqual']
    if not hasattr(assertEqual, 'student_tests'):
        return gently("The assertEqual function has been modified. Do not let it be overwritten!",
               title="overwrote_assertEqual",
               label="Overwrote assertEqual", **kwargs)
    student_tests = assertEqual.student_tests
    if student_tests.tests == 0:
        return gently("You are not unit testing the result.",
                      title="No Student Unit Tests",
                      label="no_student_tests", **kwargs)
    elif student_tests.tests < test_count:
        return gently("You have not written enough unit tests.",
                      label="not_enough_tests",
                      title="Not Enough Student Unit Tests", **kwargs)
    elif student_tests.failures > 0:
        failures = student_tests.failures
        successes = student_tests.successes
        tests = student_tests.tests
        return gently(f"{failures}/{tests} of your unit tests are not passing.",
                      label="failing_student_tests",
                      title="Student Unit Tests Failing",
                      fields={'failures': failures, 'successes': successes,
                              'tests': tests},
                      **kwargs)
    return False


@CompositeFeedbackFunction()
def ensure_bakery_tests(test_count, **kwargs):
    """
    Ensure that the student has not failed their own tests.
    This is for the specific ``bakery`` library, not the general unittest
    library.
    """
    student = get_student_data()
    if 'assert_equal' not in student:
        return gently(f"You have not imported assert_equal from the `bakery` module.",
               label=f"missing_bakery_assert_equal",
               title="Missing assert_equal", **kwargs)
    assert_equal = student['assert_equal']
    if not hasattr(assert_equal, 'student_tests'):
        return gently("The assert_equal function has been modified. Do not let it be overwritten!",
               label="overwrote_assert_equal",
               title="Overwrote assert_equal", **kwargs)
    student_tests = assert_equal.student_tests
    if student_tests.tests == 0:
        return gently("You are not unit testing the result.",
                      title="No Student Unit Tests",
                      label="no_student_tests", **kwargs)
    elif student_tests.tests < test_count:
        return gently("You have not written enough unit tests.",
                      label="not_enough_tests",
                      title="Not Enough Student Unit Tests", **kwargs)
    elif student_tests.failures > 0:
        failures = student_tests.failures
        successes = student_tests.successes
        tests = student_tests.tests
        return gently(f"{failures}/{tests} of your unit tests are not passing.",
                      label="failing_student_tests",
                      title="Student Unit Tests Failing",
                      fields={'failures': failures, 'successes': successes,
                              'tests': tests},
                      **kwargs)
    return False
