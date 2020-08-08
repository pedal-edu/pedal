from pedal.core.report import MAIN_REPORT, Report
from pedal.sandbox.constants import TOOL_NAME
from pedal.sandbox.sandbox import Sandbox
from pedal.sandbox.commands import *


def reset(report=MAIN_REPORT):
    """
    Resets (or initializes) the Sandbox instance for this report.
    Completely destroys the existing Sandbox instance attached to this report;
    if you want to just clear out its data, then instead use
    :py:func:`pedal.sandbox.commands.clear_sandbox`.

    Args:
        report:
    """
    report[TOOL_NAME] = {
        'sandbox': Sandbox(report=report)
    }


Report.register_tool(TOOL_NAME, reset)
