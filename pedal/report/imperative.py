'''
Imperative style commands for constructing feedback in a convenient way.
Uses a global report object (MAIN_REPORT).
'''

__all__ = ['set_success', 'compliment', 'give_partial', 'explain',
           'gently', 'hide_correctness', 'suppress', 'log', 'debug',
           'clear_report', 'get_all_feedback', 'MAIN_REPORT']

from pedal.report.report import Report
from pedal.report.feedback import Feedback

MAIN_REPORT = Report()

def set_success():
    MAIN_REPORT.set_success()


def compliment(message, line=None):
    MAIN_REPORT.compliment(message, line)


def give_partial(value, message=None):
    MAIN_REPORT.give_partial(value, message)


def explain(message, priority='medium', line=None):
    MAIN_REPORT.explain(message, priority, line)


def gently(message, line=None):
    MAIN_REPORT.gently(message, line)

    
def hide_correctness():
    MAIN_REPORT.hide_correctness()


def suppress(category, label=True):
    MAIN_REPORT.suppress(category, label)
    

def log(message):
    MAIN_REPORT.log(message)


def debug(message):
    MAIN_REPORT.debug(message)


def clear_report():
    MAIN_REPORT.clear()


def get_all_feedback():
    return MAIN_REPORT.feedback
