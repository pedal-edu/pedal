"""

.. csv-table:: Source Report Data
    :header: "Field", "Type", "Initial", "Description"
    :widths: 20, 20, 20, 40

    "substitutions", "List[Substitution]", "[]", "The history of previous source codes before the latest substitutions."
    "success", "bool", "None", "Whether the current file has been parsed successfully."
    "ast", "ast.Ast", "None", "The root node of the latest successfully parsed chunk of code."

"""

import sys
import ast

from pedal.core.feedback import CompositeFeedbackFunction
from pedal.core.report import Report, MAIN_REPORT
from pedal.core.submission import Submission
from pedal.source.constants import TOOL_NAME, DEFAULT_STUDENT_FILENAME
from pedal.source.sections import separate_into_sections
from pedal.source.feedbacks import blank_source, syntax_error, source_file_not_found
from pedal.source.substitutions import Substitution


def reset(report=MAIN_REPORT):
    """
    Resets the Source tool back to its initial configuration, removing any
    previously stored code/parses/section info.

    Args:
        report: The report object to be reseting.

    Returns:
        dict: The data associated with the Source tool.
    """
    report[TOOL_NAME] = {
        'substitutions': [],

        'success': None,
        'ast': None,

        'independent': None,
        'sections': None,
        'section': None,
        'section_pattern': None,
    }
    return report[TOOL_NAME]


Report.register_tool(TOOL_NAME, reset)


def set_source(code, filename=DEFAULT_STUDENT_FILENAME, sections=False,
               independent=False, report=MAIN_REPORT):
    """
    Sets the contents of the Source to be the given code. Can also be
    optionally given a filename.

    Args:
        code (str): The contents of the source file.
        filename (str): The filename of the students' code. Defaults to
                        `answer.py`.
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
    if report.submission is None:
        report.contextualize(Submission({filename: code}, filename, code))
    else:
        backup = Substitution(report.submission.main_code, report.submission.main_file)
        report[TOOL_NAME]['substitutions'].append(backup)
        report.submission.replace_main(code, filename)

    report[TOOL_NAME]['independent'] = independent
    report[TOOL_NAME]['success'] = True
    if not sections:
        report[TOOL_NAME]['sections'] = None
        report[TOOL_NAME]['section'] = None
        verify(code, report=report)
    else:
        separate_into_sections(report=report)


# TODO: source_prepend and source_append


def restore_code(report=MAIN_REPORT):
    """

    Args:
        report:
    """
    if TOOL_NAME in report:
        old_submission = report[TOOL_NAME]['substitutions'].pop()
        report.submission.replace_main(old_submission.code, old_submission.filename)
        verify(report=report)


@CompositeFeedbackFunction(blank_source, syntax_error)
def verify(code=None, filename=DEFAULT_STUDENT_FILENAME, report=MAIN_REPORT,
           muted=False):
    """
    Parses the given source code and checks for syntax errors; if no code is given, defaults to the
    current Main file of the submission.

    Args:
        muted:
        code (str): Some code to parse and syntax check.
        filename: An optional filename to use
        report:

    Returns:

    """
    if code is None:
        code = report.submission.main_code
        filename = report.submission.main_file
    if report.submission.load_error:
        source_file_not_found(filename, None)
        report[TOOL_NAME]['success'] = False
        return False
    if code.strip() == '':
        blank_source()
        report[TOOL_NAME]['success'] = False
    try:
        parsed = ast.parse(code, filename)
        report[TOOL_NAME]['ast'] = parsed
    except SyntaxError as e:
        syntax_error(e.lineno, e.filename, code, e.offset, e,
                     sys.exc_info(), report=report, muted=muted)
        report[TOOL_NAME]['success'] = False
        report[TOOL_NAME]['ast'] = ast.parse("")
    report[TOOL_NAME]['success'] = True
    return report[TOOL_NAME]['success']


# Legacy verify_section; now done by verify since its aware of sections
verify_section = verify


def get_program(report=MAIN_REPORT) -> str:
    """
    Retrieves the current main file's code.
    """
    return report.submission.main_code


def get_original_program(report=MAIN_REPORT) -> str:
    """
    Retrieves the original version of the Submission's main code, ignoring all subsitutions.
    Args:
        report:

    Returns:

    """
    return report[TOOL_NAME]['substitutions'][0].code


@CompositeFeedbackFunction(source_file_not_found)
def set_source_file(filename: str, sections=False, independent=False, report=MAIN_REPORT):
    """
    Uses the given `filename` on the filesystem as the new main file.

    Args:
        filename:
        sections:
        independent:
        report:

    Returns:

    """
    try:
        with open(filename, 'r') as student_file:
            set_source(student_file.read(), filename=filename,
                       sections=sections, independent=independent,
                       report=report)
    except IOError:
        source_file_not_found(filename, sections, report=report)
        report[TOOL_NAME]['success'] = False
