import sys

from pedal.sandbox.sandbox import Sandbox
from pedal.sandbox.messages import EXTENDED_ERROR_EXPLANATION

from pedal.report import MAIN_REPORT, Feedback

def _check_sandbox(report):
    if 'run' not in report['sandbox']:
        report['sandbox']['run'] = Sandbox()
    return report['sandbox']['run']

def run_student(raise_exceptions=False, report=None):
    if report is None:
        report = MAIN_REPORT
    sandbox = _check_sandbox(report)
    source_code = report['source']['code']
    sandbox.run(source_code)
    if raise_exceptions:
        raise_exception(sandbox.exception, sandbox.exception_position, 
                        report=report)
    return sandbox.exception

def queue_input(*inputs, **kwargs):
    if 'report' not in kwargs:
        report = MAIN_REPORT
    else:
        report = kwargs['report']
    sandbox = _check_sandbox(report)
    sandbox.set_input(inputs)

def reset_output(report=None):
    if report is None:
        report = MAIN_REPORT
    sandbox = _check_sandbox(report)
    sandbox.set_output(None)

def get_output(report=None):
    if report is None:
        report = MAIN_REPORT
    sandbox = _check_sandbox(report)
    return sandbox.output

def get_plots(report=None):
    if report is None:
        report = MAIN_REPORT
    sandbox = _check_sandbox(report)
    mock_plt = sandbox.modules['matplotlib.pyplot']
    return mock_plt.plots

def capture_output(function, *args, **kwargs):
    if 'report' in kwargs:
        report = kwargs['report']
    else:
        report = MAIN_REPORT
    sandbox = _check_sandbox(report)
    sandbox.set_output(None)
    sandbox.call(function.__name__, *args)
    return sandbox.output

def get_sandbox(report=None):
    if report is None:
        report = MAIN_REPORT
    sandbox = _check_sandbox(report)
    return sandbox

def raise_exception(exception, position=None, report=None):
    if report is None:
        report = MAIN_REPORT
    sandbox = _check_sandbox(report)
    if exception is None:
        return
    extended = EXTENDED_ERROR_EXPLANATION.get(exception.__class__, "")
    message = "<pre>{}</pre>\n{}".format(str(exception), extended)
    # Skulpt compatible name lookup
    name = str(exception.__class__)[8:-2]
    report.attach(name, category='Runtime', tool='Sandbox',
                  mistakes={'message': message, 
                            'error': exception,
                            'position': position,
                            'traceback': None})
    sandbox.exception = exception
    
def get_student_data(report=None):
    if report is None:
        report = MAIN_REPORT
    sandbox = _check_sandbox(report)
    return sandbox


def set_sandbox(sandbox, report=None):
    '''
    Update the sandbox to hold the new sandbox instance. Particularly useful
    for Skulpt, which needs to set the sandbox in an unusual way.
    '''
    if report is None:
        report = MAIN_REPORT
    report['sandbox']['run'] = sandbox
    return sandbox
