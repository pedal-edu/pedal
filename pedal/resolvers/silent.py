from pedal.resolvers.core import make_resolver
from pedal.core.report import MAIN_REPORT
from pedal.core.feedback import Feedback


@make_resolver
def resolve(report=MAIN_REPORT):
    """
    Silent resolver that returns empty results.

    Args:
        report: The report to resolve

    Returns:
        dict: A dictionary with empty final feedback and no considered feedback
    """
    result = {
        'final': None,
        'considered': []
    }
    report.result = result
    report.resolves.append(result)
    return result
