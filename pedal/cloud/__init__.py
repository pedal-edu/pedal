"""
A tool for sending submission data and existing feedback to a remote cloud service,
and then get the response back as a new feedback object.

An obvious use case is for LLMs like GPT. This can be a delayed response.
"""
from pedal.core.report import MAIN_REPORT, Report
from pedal.cloud.constants import TOOL_NAME
from pedal.cloud.gpt import reset as gpt_reset


def reset(report=MAIN_REPORT):
    """
    Resets (or initializes) the information about assertions.

    Args:
        report:
    """
    report[TOOL_NAME] = {
        'endpoints': {}
    }
    gpt_reset()


Report.register_tool(TOOL_NAME, reset)
