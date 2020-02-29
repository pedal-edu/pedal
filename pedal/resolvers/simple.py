from pedal.core.report import MAIN_REPORT
from pedal.core.commands import set_success
from pedal.core.feedback import Feedback
from pedal.resolvers.core import make_resolver

DEFAULT_NO_FEEDBACK_MESSAGE = "No errors reported."
DEFAULT_NO_FEEDBACK_TITLE = "No Errors"


DEFAULT_CATEGORY_PRIORITY = [
    "highest",
    Feedback.CATEGORIES.SYNTAX,
    Feedback.CATEGORIES.MISTAKES,
    Feedback.CATEGORIES.INSTRUCTOR,
    Feedback.CATEGORIES.ALGORITHMIC,
    Feedback.CATEGORIES.RUNTIME,
    Feedback.CATEGORIES.STUDENT,
    Feedback.CATEGORIES.POSITIVE,
    Feedback.CATEGORIES.INSTRUCTIONS,
    Feedback.CATEGORIES.UNKNOWN,
    "lowest"
]


class FinalFeedback:
    """
    Internal class used for organizing the feedback into one place. Dumpable into a simple dictionary.
    """
    def __init__(self, success=None, score=None, category=None, label=None, title=None,
                 message=None, data=None, hide_correctness=None):
        self.success = success
        self.score = score
        self.category = category
        self.label = label
        self.title = title
        self.message = message
        self.data = data
        self.hide_correctness = hide_correctness

    def __str__(self) -> str:
        return "FinalFeedback({label!r}, {title!r}, {message!r})".format(label=self.label,
                                                                         title=self.title,
                                                                         message=self.message[:50])

    def for_console(self) -> str:
        return "{label}\n{score}\n{title}\n{message}".format(label=self.label,
                                                             score=self.score,
                                                             title=self.title,
                                                             message=self.message)

    def to_json(self) -> dict:
        """

        Returns:

        """
        return {
            'success': self.success,
            'score': self.score,
            'category': self.category,
            'label': self.label,
            'title': self.title,
            'message': self.message,
            'data': self.data,
            'hide_correctness': self.hide_correctness
        }


def by_priority(feedback):
    """
    Converts a feedback into a numeric representation for sorting.

    Args:
        feedback (Feedback): The feedback object to convert
    Returns:
        float: A decimal number representing the feedback's relative priority.
    """
    category = Feedback.CATEGORIES.UNKNOWN
    if feedback.category is not None:
        category = feedback.category.lower()
    priority = 'medium'
    if feedback.priority is not None:
        priority = feedback.priority.lower()
        priority = Feedback.CATEGORIES.ALIASES.get(priority, priority)
    if category in DEFAULT_CATEGORY_PRIORITY:
        value = DEFAULT_CATEGORY_PRIORITY.index(category)
    else:
        value = len(DEFAULT_CATEGORY_PRIORITY)
    if priority in DEFAULT_CATEGORY_PRIORITY:
        value = DEFAULT_CATEGORY_PRIORITY.index(priority)
    offset = priority_offset(priority)
    return value + offset


def priority_offset(priority):
    """

    Args:
        priority:

    Returns:

    """
    if priority == 'low':
        return .7
    elif priority == 'medium':
        return .5
    elif priority == 'high':
        return .3
    else:
        return .1


def parse_feedback(feedback):
    """

    Args:
        feedback:

    Returns:

    """
    message = feedback.message or feedback.text
    title = feedback.title or feedback.label
    return feedback.correct, feedback.score, message, title, feedback.fields


@make_resolver
def resolve(report=MAIN_REPORT, priority_key=by_priority):
    """
    Args:
        priority_key: The key function to sort feedbacks by
        report (Report): The report object to resolve down. Defaults to the
                         global MAIN_REPORT

    Returns
        str: A string of HTML feedback to be delivered
    """
    # Prepare feedbacks
    feedbacks = report.feedback
    feedbacks.sort(key=priority_key)
    suppressions = report.suppressions
    # Process
    final = FinalFeedback(success=False, score=0,
                          title=None, message=None,
                          category=Feedback.CATEGORIES.COMPLETE, label='set_success_no_errors',
                          data=[], hide_correctness=False)
    for feedback in feedbacks:
        category = feedback.category.lower()
        if category in suppressions:
            if True in suppressions[category]:
                continue
            elif feedback.label.lower() in suppressions[category]:
                continue
        if feedback.label in report.suppressed_labels:
            continue
        success, partial, message, title, data = parse_feedback(feedback)
        final.score += partial if partial is not None else 0
        if feedback.muted:
            continue
        final.success = success or final.success
        if message is not None and final.message is None and feedback.priority != 'positive':
            final.message = message
            final.title = title
            final.category = feedback.category
            final.label = feedback.label
            final.data = data
    if final.message is None:
        final.title = DEFAULT_NO_FEEDBACK_TITLE
        final.message = DEFAULT_NO_FEEDBACK_MESSAGE
    final.hide_correctness = suppressions.get('success', False)
    if (not final.hide_correctness and final.success and
            final.label == 'set_success_no_errors' and final.category == Feedback.CATEGORIES.COMPLETE):
        # TODO: Promote to be its own atomic feedback function
        final.title = set_success.title
        final.message = set_success.text_template()
    report.result = final
    return final
