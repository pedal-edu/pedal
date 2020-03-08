from pedal.core.report import MAIN_REPORT, Report
from pedal.sandbox.constants import TOOL_NAME
from pedal.sandbox.feedbacks import runtime_error
from pedal.sandbox.sandbox import Sandbox, DataSandbox

# Compatibility API
'''
run_student
queue_input
reset_output
get_output
'''


def reset(report=MAIN_REPORT):
    """

    Args:
        report:
    """
    report[TOOL_NAME] = {
        'run': Sandbox()
    }


Report.register_tool(TOOL_NAME, reset)


def run(raise_exceptions=True, report=MAIN_REPORT, coverage=False, threaded=False, inputs=None) -> Sandbox:
    """

    Args:
        raise_exceptions:
        report:
        coverage:
        threaded:
        inputs:

    Returns:

    """
    sandbox = report[TOOL_NAME]['run']
    sandbox.threaded = threaded
    source_code = report.submission.main_code
    sandbox.record_coverage = coverage
    sandbox.run(source_code, as_filename=report.submission.main_file, inputs=inputs, threaded=threaded)
    sandbox.raise_exceptions_mode = raise_exceptions
    if raise_exceptions and sandbox.exception is not None:
        name = str(sandbox.exception.__class__)[8:-2]

        runtime_error(sandbox.exception_formatted, name, sandbox.exception, sandbox.exception_position,
                      group=report['source']['section'], report=report)

    return sandbox
