from pedal.resolvers.core import make_resolver
from pedal.core.report import MAIN_REPORT
from pedal.core.feedback import Feedback

DEFAULT_CATEGORY_PRIORITY = [
    Feedback.CATEGORIES.INSTRUCTIONS,
    Feedback.CATEGORIES.SYNTAX,
    Feedback.CATEGORIES.MISTAKES,
    Feedback.CATEGORIES.INSTRUCTOR,
    Feedback.CATEGORIES.ALGORITHMIC,
    Feedback.CATEGORIES.RUNTIME,
    Feedback.CATEGORIES.STUDENT,
    Feedback.CATEGORIES.POSITIVE,
    Feedback.CATEGORIES.UNKNOWN
]


def resolve_feedback(feedback):
    """

    Args:
        feedback:

    Returns:

    """
    return "{title}\n{body}".format(title=feedback.title, body=feedback.message)


@make_resolver
def resolve(report=MAIN_REPORT):
    """

    Args:
        report:

    Returns:

    """
    grouped = {}
    for feedback in report.feedback:
        if feedback.category not in grouped:
            grouped[feedback.category] = []
        grouped[feedback.category].append(feedback)
    result = []
    for group, feedbacks in grouped.items():
        result.append(group.title())
        result.extend([resolve_feedback(feedback) for feedback in feedbacks])
    return "\n".join(result)
