from pedal.core.report import MAIN_REPORT
from pedal.core.feedback import Feedback
from pedal.resolvers.core import make_resolver

DEFAULT_CATEGORY_PRIORITY = [
    Feedback.CATEGORIES.SYNTAX,
    Feedback.CATEGORIES.MISTAKES,
    Feedback.CATEGORIES.INSTRUCTOR,
    Feedback.CATEGORIES.ALGORITHMIC,
    Feedback.CATEGORIES.RUNTIME,
    Feedback.CATEGORIES.STUDENT,
    Feedback.CATEGORIES.POSITIVE,
    Feedback.CATEGORIES.INSTRUCTIONS,
    Feedback.CATEGORIES.UNKNOWN
]


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
    if priority == 'low':
        return .7
    elif priority == 'medium':
        return .5
    elif priority == 'high':
        return .3
    else:
        return .1


def parse_feedback(feedback):
    message = feedback.message or feedback.text
    return feedback.correct, feedback.score, message, feedback.fields


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
    final_success = False
    final_score = 0
    final_message = None
    final_category = 'Instructor'
    final_label = 'No errors'
    final_data = []
    for feedback in feedbacks:
        category = feedback.category.lower()
        if category in suppressions:
            if True in suppressions[category]:
                continue
            elif feedback.label.lower() in suppressions[category]:
                continue
        success, partial, message, data = parse_feedback(feedback)
        final_success = success or final_success
        final_score += partial if partial is not None else 0
        if message is not None and final_message is None and feedback.priority != 'positive':
            final_message = message
            final_category = feedback.category
            final_label = feedback.label
            final_data = data
    if final_message is None:
        final_message = "No errors reported."
    final_hide_correctness = suppressions.get('success', False)
    if (not final_hide_correctness and final_success and
            final_label == 'No errors' and
            final_category == 'Instructor'):
        final_category = 'Complete'
        final_label = 'Complete'
        final_message = "Great work!"
    return (final_success, final_score, final_category,
            final_label, final_message, final_data,
            final_hide_correctness)
