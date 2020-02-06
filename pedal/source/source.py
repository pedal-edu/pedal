"""

**Source Report**

:code (str): A backup of the original file.
:lines (List[str]): The lines split up using the newline character (``'\\n'``).
"""

import re
import ast

from pedal.core.report import MAIN_REPORT
from pedal.source import separate_into_sections
from pedal.source.constants import blank_source


def _empty_source_report():
    return {
        'code': None,
        'lines': None,
        'filename': None,
        'independent': None,
        'success': None,
        'sections': None,
        'section': None,
        'section_pattern': None,
        'line_offset': None
    }


def verify(report=MAIN_REPORT):
    pass


def set_source(code, filename='__main__.py', sections=False, independent=False,
               report=MAIN_REPORT):
    """
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
                                will be used: '^##### Part (\\d+)$'
        report (Report): The report object to store data and feedback in. If
                         left None, defaults to the global MAIN_REPORT.
    """
    report['source']['code'] = code
    report['source']['lines'] = code.split("\n")
    report['source']['filename'] = filename
    report['source']['independent'] = independent
    report['source']['success'] = True
    if not sections:
        report['source']['sections'] = None
        report['source']['section'] = None
        _check_issues(code, report)
    else:
        separate_into_sections(report=report)


def _check_issues(code, report=MAIN_REPORT):
    if code.strip() == '':
        blank_source()
        report['source']['success'] = False
    try:
        parsed = ast.parse(code, report['source']['filename'])
        report['source']['ast'] = parsed
    except SyntaxError as e:
        report.attach('Syntax error', category='Syntax', tool='Source',
                      group=report['source']['section'],
                      mistake={'message': "Invalid syntax on line "
                                          + str(e.lineno),
                               'error': e,
                               'position': {"line": e.lineno}})
        report['source']['success'] = False
        report['source']['ast'] = ast.parse("")


def get_program(report=MAIN_REPORT):
    return report['source']['code']


def set_source_file(filename, sections=False, independent=False, report=MAIN_REPORT):
    try:
        with open(filename, 'r') as student_file:
            set_source(student_file.read(), filename=filename,
                       sections=sections, independent=independent,
                       report=report)
    except IOError:
        message = ("The given filename ('{filename}') was either not found"
                   " or could not be opened. Please make sure the file is"
                   " available.").format(filename=filename)
        report.attach('Source File Not Found', category='Syntax', tool='Source',
                      group=0 if sections else None,
                      mistake={'message': message})
        report['source']['success'] = False
