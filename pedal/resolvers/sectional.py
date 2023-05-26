"""
A version of the resolver that still chooses one piece of feedback, but
does so per section.
"""

from pedal.core.feedback import Feedback
from pedal.core.final_feedback import FinalFeedback, set_correct_no_errors
from pedal.core.report import MAIN_REPORT
from pedal.resolvers.core import make_resolver
from pedal.resolvers.simple import by_priority


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
    all_feedbacks = report.feedback
    # Group the feedback
    feedback_by_group = {}
    for feedback in all_feedbacks:
        if feedback.parent in feedback_by_group:
            feedback_by_group[feedback.parent].append(feedback)
        else:
            feedback_by_group[feedback.parent] = [feedback]
    # Process each subgroup
    finals = {}
    for group, feedbacks in feedback_by_group.items():
        feedbacks.sort(key=priority_key)
        # Create the initial final feedback
        final = set_correct_no_errors(report)
        # Process each feedback in turn
        for feedback in feedbacks:
            final.merge(feedback)
        # Override empty message
        final.finalize()
        finals[group] = final
    report.result = finals
    report.resolves.append(finals)
    return finals
