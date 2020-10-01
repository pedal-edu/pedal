"""
Functions for letting students organize their code into sections.
"""

import re

from pedal.core.feedback import FeedbackGroup
from pedal.core.report import MAIN_REPORT
from pedal.source.constants import TOOL_NAME
from pedal.source.feedbacks import not_enough_sections, incorrect_number_of_sections
from pedal.source.substitutions import Substitution

DEFAULT_SECTION_PATTERN = r'^(##### Part .+)$'


class FeedbackSourceSection(FeedbackGroup):
    tool = TOOL_NAME
    category = FeedbackGroup.CATEGORIES.SYSTEM
    message = "Feedback separated into groups"

    def __init__(self, section_number, **kwargs):
        self.section_number = section_number
        super().__init__(section_number, **kwargs)


def separate_into_sections(pattern=DEFAULT_SECTION_PATTERN, independent=True, report=MAIN_REPORT):
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
    report[TOOL_NAME]['independent'] = independent
    report[TOOL_NAME]['section'] = 0
    report[TOOL_NAME]['section_group'] = FeedbackSourceSection(0)
    report.start_group(report[TOOL_NAME]['section_group'])
    report.submission.clear_line_offsets()
    report[TOOL_NAME]['section_pattern'] = pattern
    report[TOOL_NAME]['sections'] = re.split(pattern, report.submission.main_code, flags=re.MULTILINE)

    backup = Substitution(report.submission.main_code, report.submission.main_file)
    report[TOOL_NAME]['substitutions'].append(backup)
    report.submission.replace_main(report[TOOL_NAME]['sections'][0])

    report.add_hook('pedal.resolvers.resolve', stop_any_sections)

    #print(report[TOOL_NAME]['sections'])


def _calculate_section_number(section_index):
    return int((section_index+1)/2)


def stop_sections(report=MAIN_REPORT):
    """

    Args:
        report:
    """
    # TODO: If no substitutions, then throw error that we haven't separated into sections
    old_submission = report[TOOL_NAME]['substitutions'].pop()
    report.stop_group(report[TOOL_NAME]['section_group'])
    report.submission.replace_main(old_submission.code, old_submission.filename)
    report[TOOL_NAME]['section_group'] = None

def stop_any_sections(report=MAIN_REPORT):
    if report[TOOL_NAME]['substitutions']:
        stop_sections(report)


def next_section(name="", report=MAIN_REPORT):
    """

    TODO: Incoporate name to allow instructors to name sections (defaults to numbers)

    Args:
        name:
        report:
    """
    report.execute_hooks(TOOL_NAME, 'next_section.before')
    source = report[TOOL_NAME]
    old_submission = report[TOOL_NAME]['substitutions'][-1]
    report.stop_group(report[TOOL_NAME]['section_group'])
    report.submission.replace_main(old_submission.code, old_submission.filename)
    # Advance to next section
    source['section'] += 2
    section_index = source['section']
    section_number = _calculate_section_number(section_index)
    report[TOOL_NAME]['section_group'] = FeedbackSourceSection(section_number)
    sections = source['sections']
    found = _calculate_section_number(len(source['sections']))
    if section_number <= found:
        if source['independent']:
            new_code = ''.join(sections[section_index])
            old_code = ''.join(sections[:section_index])
            report.submission.set_line_offset(len(old_code.split("\n"))-1)
        else:
            new_code = ''.join(sections[:section_index + 1])
        report.submission.replace_main(new_code)
        report[TOOL_NAME]['success'] = None
        report.start_group(report[TOOL_NAME]['section_group'])
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
    #print(section_number, found, len(report[TOOL_NAME]['sections']))
    if section_number > found:
        incorrect_number_of_sections(section_number, found, parent=report[TOOL_NAME]['section'], report=report)
