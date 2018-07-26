from pedal.sandbox.sandbox import Sandbox

from pedal.report import MAIN_REPORT

def _check_sandbox(report):
    if 'run' not in report['sandbox']:
        report['sandbox']['run'] = Sandbox()
    return report['sandbox']['run']

def run_student(report=None):
    if report is None:
        report = MAIN_REPORT
    sandbox = _check_sandbox(report)
    source_code = report['source']['code']
    sandbox.run(source_code)
    return sandbox.exception

def queue_input(*inputs, report=None):
    if report is None:
        report = MAIN_REPORT
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
