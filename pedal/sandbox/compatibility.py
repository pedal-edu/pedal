from pedal.sandbox.run import run_code, load

from pedal.report import MAIN_REPORT

def run_student(report=None):
    if report is None:
        report = MAIN_REPORT
    inputs = report['sandbox'].get('inputs', None)
    execution = run_code(report['source']['code'], _inputs=inputs)
    report['sandbox']['run'] = execution
    if 'outputs' not in report['sandbox']:
        report['sandbox']['outputs'] = []
    report['sandbox']['outputs'] += execution.output
    return execution.exception

def queue_input(*inputs, report=None):
    if report is None:
        report = MAIN_REPORT
    report['sandbox']['inputs'] = inputs

def reset_output(report=None):
    if report is None:
        report = MAIN_REPORT
    report['sandbox']['outputs'] = []

def get_output(report=None):
    if report is None:
        report = MAIN_REPORT
    if 'outputs' not in report['sandbox']:
        report['sandbox']['outputs'] = []
    return report['sandbox']['outputs']
