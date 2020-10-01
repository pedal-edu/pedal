"""
Feedback functions of the Source module
"""

from pedal.core.commands import feedback
from pedal.core.feedback import FeedbackResponse
from pedal.core.location import Location
from pedal.core.report import MAIN_REPORT
from pedal.utilities.exceptions import ExpandedTraceback
from pedal.source.constants import TOOL_NAME


class SourceFeedback(FeedbackResponse):
    """ Base class of all Feedback functions for Source Tool """
    category = feedback.CATEGORIES.SYNTAX
    kind = feedback.KINDS.MISTAKE
    tool = TOOL_NAME


class blank_source(SourceFeedback):
    """ Source code file was blank. """
    title = "No Source Code"
    message_template = "Source code file is blank."
    justification = "After stripping the code, there were no characters."


class not_enough_sections(SourceFeedback):
    """ Didn't have all the needed sections. """
    title = "Not Enough Sections"
    message_template = ("Tried to advance to next section but the "
                        "section was not found. Tried to load section "
                        "{count}, but there were only {found} sections.")
    justification = ("Section index exceeded the length of the separated "
                     "sections list.")

    def __init__(self, section_number, found, **kwargs):
        fields = {'count': section_number, 'found': found}
        super().__init__(fields=fields, **kwargs)


class source_file_not_found(SourceFeedback):
    """ No source file was given. """
    title = 'Source File Not Found'
    message_template = ("The given filename {name:filename} was either not "
                        "found or could not be opened. Please make sure the "
                        "file is available.")
    version = '0.0.1'
    justification = "IOError while opening file to set_source"

    def __init__(self, name, sections, **kwargs):
        report = kwargs.get("report", MAIN_REPORT)
        fields = {'name': name, 'sections': sections }
        group = 0 if sections else kwargs.get('group')
        super().__init__(fields=fields, group=group, **kwargs)


class syntax_error(SourceFeedback):
    """ Generic feedback for any kind of syntax error. """
    muted = False
    title = "Syntax Error"
    message_template = ("Bad syntax on line {lineno:line}\n\n"
                        "The traceback was:\n{traceback_message}\n\n"
                        "Suggestion: Check line {lineno:line}, the line "
                        "before it, and the line after it.")
    version = '0.0.1'
    justification = "Syntax error was triggered while calling ast.parse"

    def __init__(self, line, filename, code, col_offset,
                 exception, exc_info, **kwargs):
        report = kwargs.get('report', MAIN_REPORT)
        files = report.submission.get_files_lines()
        if filename not in files:
            files[filename] = code.split("\n")
        if report.submission is not None:
            lines = report.submission.get_lines()
            line_offsets = report.submission.line_offsets
        else:
            lines = code.split("\n")
            line_offsets = {}
        line_offset = line_offsets.get(filename, 0)
        traceback = ExpandedTraceback(exception, exc_info, False,
                                      [report.submission.instructor_file],
                                      line_offsets, [filename], lines, files)
        traceback_stack = traceback.build_traceback()
        traceback_message = traceback.format_traceback(traceback_stack,
                                                       report.format)
        line_offset = line_offsets.get(filename, 0)
        fields = {'lineno': line+line_offset,
                  'filename': filename, 'offset': col_offset,
                  'exception': exception,
                  'traceback': traceback,
                  'traceback_stack': traceback_stack,
                  'traceback_message': traceback_message}
        location = Location(line=line+line_offset, col=col_offset, filename=filename)
        super().__init__(fields=fields, location=location, **kwargs)


class incorrect_number_of_sections(SourceFeedback):
    """ Incorrect number of sections """
    title = "Incorrect Number of Sections"
    message_template = ("Incorrect number of sections in your file. "
                     "Expected {count}, but only found {found}")
    justification = ""

    def __init__(self, count, found, **kwargs):
        fields = {'count': count, 'found': found}
        super().__init__(fields=fields, **kwargs)

# TODO: IndentationError
# TODO: TabError
