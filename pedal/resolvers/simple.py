from pedal.core.report import MAIN_REPORT
from pedal.core.final_feedback import FinalFeedback
from pedal.core.feedback import Feedback, DEFAULT_CATEGORY_PRIORITY
from pedal.resolvers.core import make_resolver


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
        priority = 'medium'
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
    # Create the initial final feedback
    final = FinalFeedback(success=True, score=0,
                          title=None, message=None,
                          category=Feedback.CATEGORIES.COMPLETE, label='set_success_no_errors',
                          data=[], hide_correctness=False,
                          suppressions=report.suppressions,
                          suppressed_labels=report.suppressed_labels)
    # Process each feedback in turn
    for feedback in feedbacks:
        final.merge(feedback)
    # Override empty message
    final.finalize()
    report.result = final
    report.resolves.append(final)
    return final

