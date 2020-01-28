"""
Imperative style commands for constructing feedback in a convenient way.
Uses a global report object (MAIN_REPORT).
"""

__all__ = ['set_success', 'compliment', 'give_partial', 'explain',
           'gently', 'hide_correctness', 'suppress', 'log', 'debug',
           'clear_report', 'get_all_feedback', 'guidance']

from pedal.core.feedback import Feedback, Kind, PEDAL_DEVELOPERS
from pedal.core.report import MAIN_REPORT


def set_success(score=1, justification=None, tool=None, group=None, report=MAIN_REPORT):
    """
    Creates Successful feedback for the user, indicating that the entire
    assignment is done.

    Args:
        score (number): Arbitrary value to set the user's score to. Defaults to 1.
    """
    return report.add_feedback(Feedback("set_success", tool=tool, kind=Kind.result,
                                        justification=justification, valence=Feedback.POSITIVE_VALENCE,
                                        title="Success", message=set_success.MESSAGE, template=set_success.MESSAGE,
                                        score=score, correct=True,
                                        muted=False, version='1.0.0', author=PEDAL_DEVELOPERS, group=group))


set_success.MESSAGE = {'text': "Great work!"}


def compliment(message, value=0, justification=None, locations=None, tool=None, group=None, report=MAIN_REPORT):
    """
    Create a positive feedback for the user, potentially on a specific line of
    code.

    Args:
        message (str): The message to display to the user.
        locations (int): The relevant line of code to reference.
        value (float): The number to increase the user's score by.
        justification (str): A justification for why this partial credit was given.
    """
    return report.add_feedback(Feedback("compliment", tool=tool, kind=Kind.encouragement,
                                        justification=justification, locations=locations,
                                        valence=Feedback.POSITIVE_VALENCE,
                                        title="Compliment", message=message, template=message,
                                        score=value, correct=False, muted=False, version='1.0.0',
                                        author=PEDAL_DEVELOPERS, group=group
                                        ))


def give_partial(value, justification=None, tool=None, group=None, report=MAIN_REPORT):
    """
    Increases the user's current score by the `value`.

    Args:
        value (number): The number to increase the user's score by.
        justification (str): A justification for why this partial credit was given.
    """
    return report.add_feedback(Feedback("give_partial", tool=tool, kind=Kind.result,
                                        justification=justification, valence=Feedback.POSITIVE_VALENCE,
                                        title="Partial Credit", message=give_partial.MESSAGE, template=give_partial.MESSAGE,
                                        score=value, correct=False, muted=True, version='1.0.0', author=PEDAL_DEVELOPERS, group=group))


give_partial.MESSAGE = {'text': "Partial credit"}


def explain(message, priority='medium', line=None, label='explain'):
    MAIN_REPORT.explain(message, priority, line, label=label)


def guidance(message, priority='medium', line=None, label='Guidance'):
    MAIN_REPORT.guidance(message, priority, line, label=label)


def gently(message, line=None, label='explain'):
    MAIN_REPORT.gently(message, line, label=label)


def gently_r(message, code, line=None, label="explain"):
    gently(message + "<br><br><i>({})<i></br></br>".format(code), line, label=label)
    return message


def explain_r(message, code, priority='medium', line=None, label="explain"):
    explain(message + "<br><br><i>({})<i></br></br>".format(code), priority, line, label=label)
    return message


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
