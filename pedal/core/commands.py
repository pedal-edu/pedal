"""
Imperative style commands for constructing feedback in a convenient way.
Uses a global report object (MAIN_REPORT).
"""

__all__ = ['feedback', 'set_success', 'compliment', 'give_partial', 'explain',
           'gently', 'hide_correctness', 'suppress', 'log', 'debug',
           'clear_report', 'get_all_feedback', 'guidance']

from pedal.core.feedback import Feedback, FeedbackKind, FeedbackCategory, PEDAL_DEVELOPERS, AtomicFeedbackFunction
from pedal.core.report import MAIN_REPORT


#: Lowercase "function" version that works like other Core Feedback Functions.
feedback = Feedback


@AtomicFeedbackFunction(title="Success",
                        text_template="Great work!".format)
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
                    title=set_success.title, message=set_success.text_template(),
                    text=set_success.text_template(),
                    score=score, correct=True,
                    muted=False, version='1.0.0', author=PEDAL_DEVELOPERS, group=group,
                    report=report)


@AtomicFeedbackFunction(title="Compliment")
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
                    title=compliment.title, message=message, text=message,
                    score=value, correct=False, muted=False, version='1.0.0',
                    author=PEDAL_DEVELOPERS, group=group, report=report
                    )


@AtomicFeedbackFunction(title="Partial Credit",
                        text_template="Partial credit".format)
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
                    title=give_partial.title, message=give_partial.text_template(),
                    text=give_partial.text_template(),
                    score=value, correct=False, muted=True, version='1.0.0', author=PEDAL_DEVELOPERS, group=group,
                    report=report)


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


def hide_correctness(report=MAIN_REPORT):
    report.hide_correctness()


def suppress(category, label=True, report=MAIN_REPORT):
    report.suppress(category, label)


def log(message, report=MAIN_REPORT):
    report.log(message)


def debug(message, report=MAIN_REPORT):
    report.debug(message)


def clear_report(report=MAIN_REPORT):
    report.clear()


def get_all_feedback(report=MAIN_REPORT):
    return report.feedback


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