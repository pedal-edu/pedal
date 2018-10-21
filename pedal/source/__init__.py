'''
A package for verifying source code.
'''

from pedal.report import MAIN_REPORT, Feedback
import re
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
           'set_source', 'count_sections', 'next_section',
           'verify_section']
DEFAULT_PATTERN = r'^(##### Part .+)$'

def set_source(code, filename='__main__.py', sections=False, report=None):
    '''
    Sets the contents of the Source to be the given code. Can also be
    optionally given a filename.
    
    Args:
        code (str): The contents of the source file.
        filename (str): The filename of the students' code. Defaults to
                        __main__.py. 
        sections (str or bool): Whether or not the file should be divided into
                                sections. If a str, then it should be a
                                Python regular expression for how the sections
                                are separated. If False, there will be no
                                sections. If True, then the default pattern
                                will be used: '^##### Part (\d+)$'
        report (Report): The report object to store data and feedback in. If
                         left None, defaults to the global MAIN_REPORT.
    '''
    if report is None:
        report = MAIN_REPORT
    report['source']['code'] = code
    report['source']['filename'] = filename
    report['source']['success'] = True
    if sections == False:
        report['source']['sections'] = None
        _check_issues(code, report)
    else:
        if sections == True:
            pattern = DEFAULT_PATTERN
        else:
            pattern = sections
        report['source']['section_pattern'] = pattern
        report['source']['section'] = 0
        report['source']['sections'] = re.split(pattern, code,
                                                flags=re.MULTILINE)
        report['source']['code'] = report['source']['sections'][0]

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

def start_section(name, report=None):
    pass

def next_section(name="", report=None):
    if report is None:
        report = MAIN_REPORT
    report['source']['section'] += 2
    section = report['source']['section']
    found = len(report['source']['sections'])
    if section < found:
        report['source']['code'] = ''.join(report['source']['sections'][:section+1])
    else:
        report.attach('Verifier Error', category='verifier', tool=NAME,
                      mistakes=("Tried to advance to next section but the "
                                "section was not found. Tried to load section "
                                "{count}, but there were only {found} sections."
                                ).format(count=int(section/2), found=found))
    
def count_sections(count, report=None):
    '''
    Checks that the right number of sections exist. This is not counting the
    prologue, before the first section. So if you have 3 sections in your code,
    you should pass in 3 and not 4.
    '''
    if report is None:
        report = MAIN_REPORT
    found = int((len(report['source']['sections'])-1)/2)
    if count != found:
        report.attach('Verifier Error', category='verifier', tool=NAME,
                      mistakes=("Incorrect number of sections in your file. "
                                "Expected {count}, but only found {found}"
                                ).format(count=count, found=found))

def verify_section(report=None):
    if report is None:
        report = MAIN_REPORT
    code = report['source']['code']
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
