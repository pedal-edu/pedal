from pedal.resolvers import simple
from pedal.report import MAIN_REPORT


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
        priority_key = simple.by_priority
    # Prepare feedbacks
    feedbacks = report.feedback
    feedbacks.sort(key=lambda f: (f.group or 0, priority_key(f)))
    suppressions = report.suppressions
    # Process
    final_success = False
    final_score = 0
    finals = {}
    found_failure = False
    for feedback in feedbacks:
        group = feedback.group or 0
        category = feedback.category.lower()
        if category in suppressions:
            if True in suppressions[category]:
                continue
            elif feedback.label.lower() in suppressions[category]:
                continue
        success, partial, message, data = simple.parse_feedback(feedback)
        final_success = success or final_success
        final_score += partial
        if message is not None:
            if feedback.priority != 'positive':
                if found_failure:
                    continue
                found_failure = True
            if group not in finals:
                finals[group] = []
            entry = {'label': feedback.label,
                     'message': message,
                     'category': feedback.category,
                     'priority': feedback.priority,
                     'data': data}
            if feedback.priority != 'positive':
                finals[group].insert(0, entry)
            else:
                finals[group].append(entry)
    final_hide_correctness = suppressions.get('success', False)
    if not finals:
        finals[0] = [{
            'label': 'No errors',
            'category': 'Instructor',
            'data': [],
            'priority': 'medium',
            'message': "No errors reported."
        }]
    return (final_success, final_score, final_hide_correctness, finals)
