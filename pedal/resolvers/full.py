from pedal.core.final_feedback import FinalFeedback, set_correct_no_errors
from pedal.resolvers.core import make_resolver
from pedal.core.report import MAIN_REPORT
from pedal.core.feedback import Feedback
from pedal.resolvers.simple import by_priority

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
    This function is used to resolve a single feedback object into a string.

    Args:
        feedback: The feedback object to resolve.

    Returns:
        str: The resolved feedback.
    """
    return "{title}\n{body}".format(title=feedback.title, body=feedback.message)


@make_resolver
def resolve(report=MAIN_REPORT, priority_key=by_priority):
    """
    This function is used to resolve the feedback objects in the report into a FinalFeedback object.

    Args:
        priority_key: The function used to sort the feedback objects.
        report: The report to resolve.

    Returns:
        FinalFeedback: The resolved feedback.
    """

    # Prepare feedbacks
    feedbacks = report.feedback + report.ignored_feedback
    feedbacks.sort(key=priority_key)
    # Create the initial final feedback
    final = set_correct_no_errors(report)
    # Process each feedback in turn
    used = []
    for feedback in feedbacks:
        partial = final.merge(feedback)
        if partial is not None:
            used.append(partial)
    # Override empty message
    final.finalize()
    final.used = used
    report.result = final
    report.resolves.append(final)
    return final
