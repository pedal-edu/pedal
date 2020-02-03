from pedal.core.commands import feedback
from pedal.core.report import MAIN_REPORT

TOOL_NAME_SOURCE = 'source'


def blank_source(group=None, report=MAIN_REPORT):
    feedback(blank_source.__name__, category=feedback.CATEGORIES.SYNTAX, tool=TOOL_NAME_SOURCE,
             title=blank_source.TITLE, version=blank_source.VERSION,
             group=group, message=blank_source.MESSAGE_TEMPLATE, report=report)


blank_source.TITLE = "No Source Code"
blank_source.MESSAGE_TEMPLATE = "Source code file is blank."
blank_source.VERSION = '0.0.1'
blank_source.JUSTIFICATION = "After stripping the code, there were no characters."
