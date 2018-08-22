'''
A package for verifying source code.
'''

from pedal.report import MAIN_REPORT, Feedback
import ast

NAME = 'Source'
SHORT_DESCRIPTION = "Verifies source code and attaches it to the report"
DESCRIPTION = '''
'''
REQUIRES = []
OPTIONALS = []
CATEGORY = 'Syntax'

__all__ = ['NAME', 'DESCRIPTION', 'SHORT_DESCRIPTION',
           'REQUIRES', 'OPTIONALS',
           'set_source']


def set_source(code, filename='__main__.py', report=None):
    if report is None:
        report = MAIN_REPORT
    report['source']['code'] = code
    report['source']['filename'] = filename
    report['source']['success'] = True
    _check_issues(code, report)


def _check_issues(code, report):
    if code.strip() == '':
        report.attach('Blank source', category=CATEGORY, tool=NAME,
                      mistakes="Source code file is blank.")
        report['source']['success'] = False
    try:
        parsed = ast.parse(code)
        report['source']['ast'] = parsed
    except SyntaxError as e:
        report.attach('Syntax error', category=CATEGORY, tool=NAME,
                      mistakes={'message': "Invalid syntax on line "
                                           +str(e.lineno),
                                'error': e,
                                'position': {"line": e.lineno}})
        report['source']['success'] = False
        if 'ast' in report['source']:
            del report['source']['ast']

def get_program(report=None):
    if report is None:
        report = MAIN_REPORT
    return report['source']['code']
