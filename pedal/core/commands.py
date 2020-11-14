"""
Imperative style commands for constructing feedback in a convenient way.
Uses a global report object (MAIN_REPORT).
"""

__all__ = ['feedback', 'set_success', 'compliment', 'give_partial', 'explain',
           'gently', 'hide_correctness', 'suppress', 'log', 'debug',
           'system_error', 'clear_report', 'get_all_feedback', 'guidance',
           'contextualize_report', 'Feedback']

from pedal.core.feedback import (Feedback, FeedbackKind, FeedbackCategory,
                                 FeedbackResponse)
from pedal.core.report import MAIN_REPORT

from pedal.core.submission import Submission

#: Lowercase "function" version that works like other Core Feedback Functions.
feedback = Feedback


# TODO: force_success function, which ignores errors to give the points.

class set_success(FeedbackResponse):
    """
    **(Feedback Function)**

    Creates Successful feedback for the user, indicating that the entire
    assignment is done.
    """
    title = "Complete"
    message_template = "Great work!"
    score = 1
    correct = True
    category = FeedbackCategory.COMPLETE
    kind = FeedbackKind.RESULT
    valence = Feedback.POSITIVE_VALENCE


class compliment(FeedbackResponse):
    """
    Create a positive feedback for the user, potentially on a specific line of
    code.
    """
    category = FeedbackCategory.INSTRUCTOR
    kind = FeedbackKind.COMPLIMENT
    valence = Feedback.POSITIVE_VALENCE
    correct = True

    def __init__(self, message, title=None, **kwargs):
        if title is None:
            title = message
        super().__init__(message=message, title=title, **kwargs)


class give_partial(FeedbackResponse):
    """ Increases the user's current score by the `score`. """
    title = "Partial Credit"
    message_template = "Partial credit"
    category = FeedbackCategory.INSTRUCTOR
    kind = FeedbackKind.RESULT
    valence = Feedback.POSITIVE_VALENCE
    correct = None
    muted = True

    def __init__(self, value, **kwargs):
        super().__init__(score=value, **kwargs)


class explain(FeedbackResponse):
    """ Give a high-priority piece of negative feedback to the student. """
    title = "Instructor Feedback"
    muted = False
    category = Feedback.CATEGORIES.INSTRUCTOR
    kind = FeedbackKind.MISTAKE
    valence = Feedback.NEGATIVE_VALENCE

    def __init__(self, message, **kwargs):
        super().__init__(message=message, **kwargs)


class gently(FeedbackResponse):
    """
    Give a low-priority piece of negative feedback to the student.

    Args:
        message (str): The feedback message to show to the student.

    """
    title = "Instructor Feedback"
    priority = Feedback.CATEGORIES.STUDENT
    muted = False
    category = Feedback.CATEGORIES.INSTRUCTOR
    kind = FeedbackKind.MISTAKE
    valence = Feedback.NEGATIVE_VALENCE

    def __init__(self, message, **kwargs):
        super().__init__(message=message, **kwargs)


class guidance(FeedbackResponse):
    """ Give instructions about a question. """
    title = "Instructor Guidance"
    category = Feedback.CATEGORIES.INSTRUCTIONS
    kind = FeedbackKind.INSTRUCTIONAL
    valence = Feedback.NEUTRAL_VALENCE

    def __init__(self, message, **kwargs):
        super().__init__(message=message, **kwargs)


def hide_correctness(report=MAIN_REPORT):
    """
    Force the report to not indicate score/correctness.

    Args:
        report (:py:class:`pedal.core.report.Report`): The report object to
            hide correctness on.
    """
    report.hide_correctness()


def suppress(category=None, label=True, report=MAIN_REPORT):
    """
    Hides a given category or label within a category from being considered
    by the resolver.

    Args:
        category (str): The general feedback category to suppress within.
            Should be a member of
            :py:class:`pedal.core.feedback_category.FeedbackCategory`.
        label (str or bool): The specific feedback label to suppress, or
            True if all the labels within this category should be suppressed.
        report (:py:class:`~pedal.core.report.Report`): The report object to
            suppress information within.
    """
    report.suppress(category, label)


def log(*items, sep=" ", **kwargs):
    """
    Attach logging information to the Report as a piece of feedback.

    Args:
        items (Any): Any set of values to log information about. Will be
            converted to strings using `str` if not already strings.

    Returns:

    """
    kwargs.setdefault('category', Feedback.CATEGORIES.SYSTEM)
    kwargs.setdefault('muted', True)
    kwargs.setdefault('valence', Feedback.NEUTRAL_VALENCE)
    message = sep.join(item if isinstance(item, str) else str(item)
                       for item in items)
    feedback(message=message, label="log", **kwargs)


def debug(*items, **kwargs):
    """
    Attach logging information to the Report as a piece of feedback.
    Works at a higher priority than :py:func:`~pedal.core.commands.log` and
    does not attempt to convert to strings.

    TODO: Consider updating to match `log`

    Args:
        items (Any): Any set of values to log information about. Will be
            converted to strings using `str` if not already strings.

    Returns:

    """
    kwargs.setdefault('category', Feedback.CATEGORIES.SYSTEM)
    kwargs.setdefault('muted', True)
    kwargs.setdefault('priority', 'high')
    kwargs.setdefault('valence', Feedback.NEGATIVE_VALENCE)
    for item in items:
        item = item
        cloned_kwargs = kwargs.copy()
        cloned_kwargs.setdefault('message', item)
        feedback(label="debug", **kwargs)


def clear_report(report=MAIN_REPORT):
    """
    Removes all existing data from the report, including any submissions,
    suppressions, feedback, and Tool data.

    Args:
        report: The report to clear (defaults to the
            :py:data:`pedal.core.report.MAIN_REPORT`).
    """
    report.clear()


def contextualize_report(submission, filename='answer.py', clear=True,
                         report=MAIN_REPORT):
    """
    Updates the report with the submission. By default, clears out any old
    information in the report. You can pass in either an actual
    :py:class:`~pedal.core.submission.Submission` or a string representing
    the code of the submission.

    Args:
        submission (str or Submission):
        filename (str or None): If the `submission` was not a
            :py:class:`~pedal.core.submission.Submission`, then this will be
            used as the filename for the code given in ``submission``.
        clear (bool): Whether or not to clear the report before attaching
            the submission.
        report: The report to attach this feedback to (defaults to the
            :py:data:`~pedal.core.report.MAIN_REPORT`).
    """
    if not isinstance(submission, Submission):
        submission = Submission(files={filename: submission})
    if clear:
        report.clear()
    report.contextualize(submission)


def get_all_feedback(report=MAIN_REPORT):
    """
    Gives access to the list of feedback from the report. Usually, you won't
    need this; but if you want to build on the results of earlier tools, it
    can be a useful mechanism.

    TODO: Provide mechanisms for conveniently searching feedback

    Args:
        report (:py:class:`~pedal.core.report.Report`): The report to attach
            this feedback to (defaults to the
            :py:data:`~pedal.core.report.MAIN_REPORT`).

    Returns:
        List[:py:class:`~pedal.core.feedback.Feedback`]: A list of feedback
            objects from the report.
    """
    return report.feedback


class system_error(FeedbackResponse):
    """
    Call this function to indicate that something has gone wrong at the system
    level with Pedal. Ideally, this doesn't happen, but sometimes errors
    cascade and its polite for tools to suggest that they are not working
    correctly. These will not usually be reported to the student.
    """
    title = "System Error"
    category = Feedback.CATEGORIES.SYSTEM
    kind = FeedbackKind.META
    valence = Feedback.NEUTRAL_VALENCE
    muted = True
