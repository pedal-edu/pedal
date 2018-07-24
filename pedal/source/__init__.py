'''
A package for verifying source code.
'''

from pedal.report import MAIN_REPORT
import ast

STUDENT_NAME = 'Syntax Error'
NAME = 'Source'

def _prepare_report(report):
    if 'source' in report:
        return False
    report['source'] = {}

def set_source(code, filename='__main__.py', report=None):
    if report is None:
        report = MAIN_REPORT
    _prepare_report(report)
    report['source']['code'] = code
    report['source']['filename'] = filename
    _check_issues(code, report)

def _check_issues(code, report):
    if code.strip() == '':
        report.complaint(NAME, 'Source code file is blank.')
    try:
        parsed = ast.parse(code)
    except:
        report.complaint(NAME, 'Failed to parse code.')
    