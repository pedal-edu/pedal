"""
Feedback functions of the Source module
"""
import traceback as tb
from pedal.core.commands import feedback
from pedal.core.feedback import FeedbackResponse
from pedal.core.location import Location
from pedal.core.report import MAIN_REPORT
from pedal.utilities.exceptions import ExpandedTraceback, get_exception_name
from pedal.source.constants import TOOL_NAME
from pedal.utilities.system import IS_AT_LEAST_PYTHON_310
from pedal.utilities.text import add_indefinite_article
from pedal.core.formatting import wrap_fields


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
        fields = {'name': name, 'sections': sections}
        group = 0 if sections else kwargs.get('group')
        super().__init__(fields=fields, group=group, **kwargs)


class syntax_error(SourceFeedback):
    """ Generic feedback for any kind of syntax error. """
    muted = False
    title = "Syntax Error"
    constant_fields = {"suggestion": "Suggestion: Check line {lineno:line}, the line before it, and the line "
                                     "after it. Ignore blank lines."}
    message_template = ("Bad syntax on line {lineno:line}.\n\n"
                        "{traceback_preamble}{traceback_message}\n"
                        "{exception_message}"
                        "{suggestion_message}")
    version = '1.0.0'
    justification = "Syntax error was triggered while calling ast.parse"

    def __init__(self, line, filename, code, col_offset,
                 exception, exc_info, enhance=True, **kwargs):
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
        exception_name = get_exception_name(exception)
        exception_name_proper = add_indefinite_article(exception_name)
        traceback = ExpandedTraceback(exception, exc_info, False,
                                      [report.submission.instructor_file],
                                      line_offsets, [filename], lines, files)
        traceback_stack = traceback.build_traceback()
        traceback_message = traceback.format_traceback(traceback_stack, report.format)
        traceback_preamble = f"The traceback was:\n" if traceback_message else ""
        #if not enhance:
        #    self.message_template = "{traceback_message}\n{exception_message}"
        line_offset = line_offsets.get(filename, 0)
        exception_message = self.make_exception_message(exception)
        fields = {'lineno': line + line_offset,
                  'filename': filename,
                  'offset': col_offset,
                  'exception': exception,
                  'exception_name': exception_name,
                  'exception_name_proper': exception_name_proper,
                  'exception_message': exception_message,
                  'traceback': traceback,
                  'traceback_stack': traceback_stack,
                  'traceback_preamble': traceback_preamble,
                  'traceback_message': traceback_message}
        location = Location(line=line + line_offset, col=col_offset, filename=filename)
        fields['suggestion_message'] = self.constant_fields['suggestion'].format(**wrap_fields(report.format, fields))
        super().__init__(fields=fields, location=location, **kwargs)

    def make_exception_message(self, exception):
        """ Generate a suggestion message based on the exception. """
        base_message = exception.msg
        base_message = base_message.capitalize() + "."
        #if base_message == "Invalid syntax.":
        #    return ""
        return base_message + "\n"


class incorrect_number_of_sections(SourceFeedback):
    """ Incorrect number of sections """
    title = "Incorrect Number of Sections"
    message_template = ("Incorrect number of sections in your file. "
                        "Expected {count}, but only found {found}")
    justification = ""

    def __init__(self, count, found, **kwargs):
        fields = {'count': count, 'found': found}
        super().__init__(fields=fields, **kwargs)


# TODO: TabError


class indentation_error(syntax_error):
    """ Generic feedback for indentation errors. """
    title = "Indentation Error"
    constant_fields = {'suggestion': "Suggestion: Check line {lineno:line}, the line before it, and the "
                                     "line after it. Ignore blank lines."}
    message_template = ("Bad indentation on line {lineno:line} or adjacent line.\n\n"
                        "{traceback_preamble}{traceback_message}\n"
                        "{exception_message}"
                        "{suggestion_message}"
                        )
    version = '1.0.0'
    justification = "Indentation error was triggered while calling ast.parse"
