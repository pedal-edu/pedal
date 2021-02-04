from pedal.core.final_feedback import FinalFeedback
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

    # Prepare feedbacks
    feedbacks = report.feedback + report.ignored_feedback

    # Create the initial final feedback
    final = FinalFeedback(success=True, score=0,
                          title=None, message=None,
                          category=Feedback.CATEGORIES.COMPLETE,
                          label='set_success_no_errors',
                          data=[], hide_correctness=False,
                          suppressions=report.suppressions,
                          suppressed_labels=report.suppressed_labels)
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