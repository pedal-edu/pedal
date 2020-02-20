"""

**Source Report**

:code (str): A backup of the original file.
:lines (List[str]): The lines split up using the newline character (``'\\n'``).
"""

import sys
import ast

from pedal.core.report import MAIN_REPORT
from pedal.source.sections import separate_into_sections
from pedal.source.constants import blank_source, syntax_error, source_file_not_found


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
        independent (bool): Whether the separate sections should be considered
            separate or all existing in an accumulating namespace.
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
        verify(code, report)
    else:
        separate_into_sections(report=report)


def verify(code=None, report=MAIN_REPORT):
    if code is None:
        code = report['source']['code']
    if code.strip() == '':
        blank_source()
        report['source']['success'] = False
    try:
        parsed = ast.parse(code, report['source']['filename'])
        report['source']['ast'] = parsed
    except SyntaxError as e:
        syntax_error(e.lineno, e.filename, code, e.offset, e.text, e.__traceback__, e, sys.exc_info(), report=report)
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
        source_file_not_found(filename, sections, report)
        report['source']['success'] = False
