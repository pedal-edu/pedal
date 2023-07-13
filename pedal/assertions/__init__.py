"""
The assertions module contains classic unittest-style assert statements.
"""

from pedal.assertions.setup import _setup_assertions, resolve_all
from pedal.assertions.constants import TOOL_NAME
from pedal.core.report import Report, MAIN_REPORT
from pedal.assertions.commands import *
from pedal.assertions.positive import close_output, correct_output
from pedal.assertions.testing_libraries import *


def reset(report=MAIN_REPORT):
    """
    Resets (or initializes) the information about assertions.

    Args:
        report:
    """
    report[TOOL_NAME] = {
        'failures': 0,
        'exceptions': False
    }


Report.register_tool(TOOL_NAME, reset)
