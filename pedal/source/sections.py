import ast
import re
import sys
from pedal.core.report import MAIN_REPORT
from pedal.source.constants import TOOL_NAME
from pedal.source.feedbacks import not_enough_sections, incorrect_number_of_sections
from pedal.source.substitutions import Substitution

DEFAULT_SECTION_PATTERN = r'^(##### Part .+)$'


def separate_into_sections(pattern=DEFAULT_SECTION_PATTERN, report=MAIN_REPORT):
    """
    Chunks the current submissions' main code into separate sections.
    Args:
        pattern:
        report:

    Returns:

    """
    if not report[TOOL_NAME]['success']:
        pass
    if report[TOOL_NAME]['sections']:
        # TODO: System constraint violated: separating into sections multiple times
        pass
    report.group = 0
    report[TOOL_NAME]['section'] = 0
    report[TOOL_NAME]['line_offset'] = 0
    report[TOOL_NAME]['section_pattern'] = pattern
    report[TOOL_NAME]['sections'] = re.split(pattern, report.submission.main_code, flags=re.MULTILINE)

    backup = Substitution(report.submission.main_code, report.submission.main_file)
    report[TOOL_NAME]['substitutions'].append(backup)
    report.submission.replace_main(report[TOOL_NAME]['sections'][0])

    print(report[TOOL_NAME]['sections'])


def _calculate_section_number(section_index):
    return int((section_index+1)/2)


def stop_sections(report=MAIN_REPORT):
    """

    Args:
        report:
    """
    # TODO: If no substitutions, then throw error that we haven't separated into sections
    old_submission = report[TOOL_NAME]['substitutions'].pop()
    report.submission.replace_main(old_submission.code, old_submission.filename)


def next_section(name="", report=MAIN_REPORT):
    """

    Args:
        name:
        report:
    """
    report.execute_hooks(TOOL_NAME, 'next_section.before')
    source = report[TOOL_NAME]
    old_submission = report[TOOL_NAME]['substitutions'][-1]
    report.submission.replace_main(old_submission.code, old_submission.filename)
    # Advance to next section
    source['section'] += 2
    section_index = source['section']
    section_number = _calculate_section_number(section_index)
    sections = source['sections']
    found = len(source['sections'])
    if section_index < found:
        if source['independent']:
            new_code = ''.join(sections[section_index])
            old_code = ''.join(sections[:section_index])
            source['line_offset'] = len(old_code.split("\n"))-1
        else:
            new_code = ''.join(sections[:section_index + 1])
        report.submission.replace_main(new_code)
        report[TOOL_NAME]['success'] = None
        report.group = section_index
    else:
        not_enough_sections(section_number, found)
    report.execute_hooks(TOOL_NAME, 'next_section.after')


def check_section_exists(section_number, report=MAIN_REPORT):
    """
    Checks that the right number of sections exist. The prologue before the
    first section is 0, while subsequent ones are 1, 2, 3, etc. 
    So if you have 3 sections in your code plus the prologue,
    you should pass in 3 and not 4 to verify that all of them exist.
    """
    if report[TOOL_NAME]['success'] is False:
        return False
    found = int((len(report[TOOL_NAME]['sections']) - 1) / 2)
    print(section_number, found, len(report[TOOL_NAME]['sections']))
    if section_number > found:
        incorrect_number_of_sections(section_number, found, group=report[TOOL_NAME]['section'], report=report)


class _finish_section:
    def __init__(self, number, *functions):
        if isinstance(number, int):
            self.number = number
        else:
            self.number = -1
            functions = [number] + list(functions)
        self.functions = functions
        for function in functions:
            self(function, False)

    def __call__(self, f=None, quiet=True):
        if f is not None:
            f()
        if quiet:
            print("\tNEXT SECTION")

    def __enter__(self):
        pass

    def __exit__(self, x, y, z):
        print("\tNEXT SECTION")
        # return wrapped_f


def finish_section(number, *functions, **kwargs):
    """

    Args:
        number:
        *functions:
        **kwargs:

    Returns:

    """
    if 'next_section' in kwargs:
        ns = kwargs['next_section']
    else:
        ns = False
    if len(functions) == 0:
        x = _finish_section(number, *functions)
        x()
    else:
        result = _finish_section(number, *functions)
        if ns:
            print("\tNEXT SECTION")
        return result


# TODO: set up precondition and postcondition decorators for sections
def section(number):
    """
    """
    pass


def precondition(function):
    """

    Args:
        function:
    """
    pass


def postcondition(function):
    """

    Args:
        function:
    """
    pass
