"""
Imperative style commands for constructing feedback in a convenient way.
Uses a global report object (MAIN_REPORT).
"""

__all__ = ['set_success', 'compliment', 'give_partial', 'explain',
           'gently', 'hide_correctness', 'suppress', 'log', 'debug',
           'clear_report', 'get_all_feedback', 'guidance']

from pedal.core.feedback import Feedback, FeedbackKind, FeedbackCategory, PEDAL_DEVELOPERS
from pedal.core.report import MAIN_REPORT


#: Lowercase "function" version that works like other Core Feedback Functions.
feedback = Feedback


def set_success(score=1, justification=None, tool=None, group=None, report=MAIN_REPORT):
    """
    **(Feedback Function)**

    Creates Successful feedback for the user, indicating that the entire
    assignment is done.

    Args:
        justification (str): Internal message that explains why this function was used.
        score (number): Arbitrary value to set the user's score to. Defaults to 1.
    """
    return feedback("set_success",
                    tool=tool, category=FeedbackCategory.INSTRUCTOR, kind=FeedbackKind.RESULT,
                    justification=justification, valence=Feedback.POSITIVE_VALENCE,
                    title="Success", message=set_success.MESSAGE, template=set_success.MESSAGE,
                    score=score, correct=True,
                    muted=False, version='1.0.0', author=PEDAL_DEVELOPERS, group=group,
                    report=report)


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
    return feedback("compliment", tool=tool,
                    category=FeedbackCategory.INSTRUCTOR, kind=FeedbackKind.ENCOURAGEMENT,
                    justification=justification, locations=locations,
                    valence=Feedback.POSITIVE_VALENCE,
                    title="Compliment", message=message, template=message,
                    score=value, correct=False, muted=False, version='1.0.0',
                    author=PEDAL_DEVELOPERS, group=group, report=report
                    )


def give_partial(value, justification=None, tool=None, group=None, report=MAIN_REPORT):
    """
    Increases the user's current score by the `value`.

    Args:
        value (number): The number to increase the user's score by.
        justification (str): A justification for why this partial credit was given.
    """
    return feedback("give_partial", tool=tool, category=FeedbackCategory.INSTRUCTOR,
                    kind=FeedbackKind.RESULT,
                    justification=justification, valence=Feedback.POSITIVE_VALENCE,
                    title="Partial Credit", message=give_partial.TEMPLATE, template=give_partial.TEMPLATE,
                    score=value, correct=False, muted=True, version='1.0.0', author=PEDAL_DEVELOPERS, group=group,
                    report=report)


give_partial.TEMPLATE = "Partial credit"


# TODO: Fix the rest

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


def explain(self, message, priority='medium', line=None, group=None,
            label='explain'):
    misconception = {'message': message}
    if line is not None:
        misconception['line'] = line
    if group is None:
        group = self.group
    self.attach(label, priority=priority, category='instructor',
                group=group, misconception=misconception)

def gently(self, message, line=None, group=None, label='explain'):
    self.explain(message, priority='student', line=line, group=group,
                 label=label)

def guidance(self, message, line=None, group=None, label='guidance'):
    hint = {'message': message}
    if line is not None:
        hint['line'] = line
    if group is None:
        group = self.group
    self.attach(label, priority='instructions', category='instructions', group=group, hint=hint)