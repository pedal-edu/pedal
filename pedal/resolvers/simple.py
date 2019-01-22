from pedal.report import MAIN_REPORT, Feedback
from pedal.resolvers.core import make_resolver

DEFAULT_CATEGORY_PRIORITY = [
    'syntax',
    'mistakes',
    'instructor',
    'analyzer',
    'runtime',
    'student',
    'positive',
    'uncategorized',
]

# For compatibility with the old feedback API
LEGACY_CATEGORIZATIONS = {
    # 'student': 'runtime',
    'parser': 'syntax',
    'verifier': 'syntax',
    'instructor': 'instructor'
}


def by_priority(feedback):
    """
    Converts a feedback into a numeric representation for sorting.

    Args:
        feedback (Feedback): The feedback object to convert
    Returns:
        float: A decimal number representing the feedback's relative priority.
    """
    category = 'uncategorized'
    if feedback.category is not None:
        category = feedback.category.lower()
    priority = 'medium'
    if feedback.priority is not None:
        priority = feedback.priority.lower()
        priority = LEGACY_CATEGORIZATIONS.get(priority, priority)
    if category in DEFAULT_CATEGORY_PRIORITY:
        value = DEFAULT_CATEGORY_PRIORITY.index(category)
    else:
        value = len(DEFAULT_CATEGORY_PRIORITY)
    offset = .5
    if priority == 'low':
        offset = .7
    elif priority == 'high':
        offset = .3
    elif priority not in ('low', 'medium', 'high'):
        if priority in DEFAULT_CATEGORY_PRIORITY:
            value = DEFAULT_CATEGORY_PRIORITY.index(priority)
            offset = .1
    return value + offset


def parse_message(component):
    if isinstance(component, str):
        return component
    elif isinstance(component, list):
        return '<br>\n'.join(parse_message(c) for c in component)
    elif isinstance(component, dict):
        if "html" in component:
            return component["html"]
        elif "message" in component:
            return component["message"]
        else:
            raise ValueError("Component has no message field: " + str(component))
    else:
        raise ValueError("Invalid component type: " + str(type(component)))


def parse_data(component):
    if isinstance(component, str):
        return [{'message': component}]
    elif isinstance(component, list):
        return component
    elif isinstance(component, dict):
        return [component]


def parse_feedback(feedback):
    # Default returns
    success = False
    performance = 0
    message = None
    data = []
    # Actual processing
    for feedback_type in Feedback.MESSAGE_TYPES:
        feedback_value = getattr(feedback, feedback_type)
        if feedback_value is not None:
            data.extend(parse_data(feedback_value))
            parsed_message = parse_message(feedback_value)
            if parsed_message is not None:
                message = parsed_message
    if feedback.result is not None:
        success = feedback.result
    if feedback.performance is not None:
        performance = feedback.performance
    return success, performance, message, data


@make_resolver
def resolve(report=None, priority_key=None):
    """
    Args:
        report (Report): The report object to resolve down. Defaults to the
                         global MAIN_REPORT

    Returns
        str: A string of HTML feedback to be delivered
    """
    if report is None:
        report = MAIN_REPORT
    if priority_key is None:
        priority_key = by_priority
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
        final_score += partial
        if (message is not None and
                final_message is None and
                feedback.priority != 'positive'):
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
