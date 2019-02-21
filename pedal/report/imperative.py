"""
Imperative style commands for constructing feedback in a convenient way.
Uses a global report object (MAIN_REPORT).
"""

__all__ = ['set_success', 'compliment', 'give_partial', 'explain',
           'gently', 'hide_correctness', 'suppress', 'log', 'debug',
           'clear_report', 'get_all_feedback', 'MAIN_REPORT']

from pedal.report.report import Report

#: The global Report object. Meant to be used as a default singleton
#: for any tool, so that instructors do not have to create their own Report.
#: Of course, all APIs are expected to work with a given Report, and only
#: default to this Report when no others are given.
MAIN_REPORT = Report()


def set_success():
    """
    Creates Successful feedback for the user, indicating that the entire
    assignment is done.
    """
    MAIN_REPORT.set_success()


def compliment(message, line=None):
    """
    Create a positive feedback for the user, potentially on a specific line of
    code.

    Args:
        message (str): The message to display to the user.
        line (int): The relevant line of code to reference.
    """
    MAIN_REPORT.compliment(message, line)


def give_partial(value, message=None):
    """
    Increases the user's current score by the `value`. Optionally display
    a positive message too.

    Args:
        value (number): The number to increase the user's score by.
        message (str): The message to display to the user.
    """
    MAIN_REPORT.give_partial(value, message)


def explain(message, priority='medium', line=None, label='explain'):
    MAIN_REPORT.explain(message, priority, line, label=label)


def gently(message, line=None, label='explain'):
    MAIN_REPORT.gently(message, line, label=label)


def hide_correctness():
    MAIN_REPORT.hide_correctness()


def suppress(category, label=True):
    MAIN_REPORT.suppress(category, label)


def log(message):
    MAIN_REPORT.log(message)


def debug(message):
    MAIN_REPORT.debug(message)


def clear_report():
    MAIN_REPORT.clear()


def get_all_feedback():
    return MAIN_REPORT.feedback
