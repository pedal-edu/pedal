"""
Resolver that collates all the feedback given into a simple format.
"""
from pedal import Feedback
from pedal.core.final_feedback import FinalFeedback, set_correct_no_errors
from pedal.resolvers.core import make_resolver
from pedal.resolvers.simple import by_priority
from pedal.core.report import MAIN_REPORT


@make_resolver
def resolve(report=MAIN_REPORT):
    """

    Args:
        report:

    Returns:

    """
    feedbacks = report.feedback + report.ignored_feedback
    feedbacks.sort(key=by_priority)
    final = set_correct_no_errors(report)
    result = []
    for feedback in feedbacks:
        final.merge(feedback)
        result.append(feedback.to_json())
    final.finalize()
    report.result = result
    report.resolves.append(result)
    return {
        'considered': [r for r in result],
        'final': final.to_json()
    }
