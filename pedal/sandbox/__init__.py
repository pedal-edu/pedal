from pedal.report import MAIN_REPORT
from pedal.sandbox.sandbox import Sandbox

# Compatibility API
'''
run_student
queue_input
reset_output
get_output
'''


def reset(report=None):
    if report is None:
        report = MAIN_REPORT
    report['sandbox']['run'] = Sandbox(filename=report['source']['filename'])


def run(raise_exceptions=True, report=None, coverage=False, threaded=False, inputs=None):
    if report is None:
        report = MAIN_REPORT
    if 'run' not in report['sandbox']:
        report['sandbox']['run'] = Sandbox(filename=report['source']['filename'], threaded=threaded)
    sandbox = report['sandbox']['run']
    source_code = report['source']['code']
    sandbox.record_coverage = coverage
    sandbox.run(source_code, _as_filename=report['source']['filename'], _inputs=inputs)
    if raise_exceptions and sandbox.exception is not None:
        name = str(sandbox.exception.__class__)[8:-2]
        report.attach(name, category='Runtime', tool='Sandbox',
                      section=report['source']['section'],
                      mistakes={'message': sandbox.format_exception(),
                                'error': sandbox.exception})
    return sandbox
