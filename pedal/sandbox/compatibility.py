import sys

from pedal.sandbox import TOOL_NAME
from pedal.sandbox.feedbacks import runtime_error
from pedal.sandbox.sandbox import Sandbox
from pedal.sandbox.messages import EXTENDED_ERROR_EXPLANATION

from pedal.core.report import MAIN_REPORT


def run_student(raise_exceptions=False, report=MAIN_REPORT, old_style_messages=False):
    """

    Args:
        raise_exceptions:
        report:
        old_style_messages:

    Returns:

    """
    sandbox = report[TOOL_NAME]['run']
    source_code = report.submission.main_code
    filename = report.submission.main_file
    sandbox.run(source_code, as_filename=filename, report_exceptions=not raise_exceptions)
    if raise_exceptions:
        raise_exception(sandbox.exception, sandbox.exception_position,
                        report=report, message=None if old_style_messages else sandbox.exception_formatted)
    return sandbox.exception


def queue_input(*inputs, **kwargs):
    """

    Args:
        *inputs:
        **kwargs:
    """
    if 'report' not in kwargs:
        report = MAIN_REPORT
    else:
        report = kwargs['report']
    sandbox = report[TOOL_NAME]['run']
    sandbox.set_input(inputs)


def reset_output(report=MAIN_REPORT):
    """

    Args:
        report:
    """
    sandbox = report[TOOL_NAME]['run']
    sandbox.set_output(None)


def get_output(report=MAIN_REPORT):
    """

    Args:
        report:

    Returns:

    """
    sandbox = report[TOOL_NAME]['run']
    return sandbox.output


def get_plots(report=MAIN_REPORT):
    """

    Args:
        report:

    Returns:

    """
    sandbox = report[TOOL_NAME]['run']
    if 'matplotlib.pyplot' in sandbox.modules:
        mock_plt = sandbox.modules['matplotlib.pyplot']
        if hasattr(mock_plt, 'plots'):
            return mock_plt.plots
    return []


def capture_output(function, *args, **kwargs):
    """

    Args:
        function:
        *args:
        **kwargs:

    Returns:

    """
    if 'report' in kwargs:
        report = kwargs['report']
    else:
        report = MAIN_REPORT
    sandbox = report[TOOL_NAME]['run']
    sandbox.set_output(None)
    sandbox.call(function.__name__, *args)
    return sandbox.output


def get_sandbox(report=MAIN_REPORT):
    """

    Args:
        report:

    Returns:

    """
    sandbox = report[TOOL_NAME]['run']
    return sandbox


def raise_exception(exception, position=None, report=MAIN_REPORT, message=None):
    """

    Args:
        exception:
        position:
        report:
        message:

    Returns:

    """
    sandbox = report[TOOL_NAME]['run']
    if exception is None:
        return
    extended = EXTENDED_ERROR_EXPLANATION.get(exception.__class__, "")
    if message is None:
        message = "<pre>{}</pre>\n{}".format(str(exception), extended)
    # Skulpt compatible name lookup
    name = str(exception.__class__)[8:-2]
    runtime_error(message, name, exception, position, report=report)
    sandbox.exception = exception


def get_student_data(report=MAIN_REPORT):
    """

    Args:
        report:

    Returns:

    """
    return get_sandbox(report)


def set_sandbox(sandbox, report=MAIN_REPORT):
    """
    Update the sandbox to hold the new sandbox instance. Particularly useful
    for Skulpt, which needs to set the sandbox in an unusual way.
    """
    report['sandbox']['run'] = sandbox
    return sandbox


def trace_lines(report=MAIN_REPORT):
    """

    Args:
        report:

    Returns:

    """
    sandbox = report[TOOL_NAME]['run']
    if sandbox.tracer_style == 'coverage':
        return sandbox.trace.lines - sandbox.trace.missing
    else:
        return []
