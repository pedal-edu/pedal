from pedal.core.commands import feedback
from pedal.core.feedback import AtomicFeedbackFunction, FeedbackResponse
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
    text_template = "Source code file is blank."
    justification = "After stripping the code, there were no characters."


class not_enough_sections(SourceFeedback):
    """ Didn't have all the needed sections. """
    title = "Not Enough Sections"
    text_template = ("Tried to advance to next section but the "
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
    text_template = ("The given filename ('{filename}') was either not found"
                     " or could not be opened. Please make sure the file is"
                     " available.")
    version = '0.0.1'
    justification = "IOError while opening file to set_source"

    def __init__(self, filename, sections, **kwargs):
        fields = {'filename': filename, 'sections': sections}
        group = 0 if sections else kwargs.get('group')
        super().__init__(fields=fields, group=group, **kwargs)


class syntax_error(SourceFeedback):
    """ Generic feedback for any kind of syntax error. """
    muted = False
    title = "Syntax Error"
    message_template = "```\n{context}\n```\nBad syntax on line {lineno}"
    text_template = "{context}\nBad syntax on line {lineno}"
    version = '0.0.1'
    justification = "Syntax error was triggered while calling ast.parse"

    def __init__(self, line, filename, code, offset, text,
                 exception, exc_info, **kwargs):
        report = kwargs.get('report', MAIN_REPORT)
        traceback = ExpandedTraceback(exception, exc_info, False,
                                      report.submission.instructor_file,
                                      line, filename, code)
        context = traceback.format_exception()
        fields = {'lineno': line, 'filename': filename, 'offset': offset,
                  'text': text, 'traceback': traceback, 'exception': exception,
                  'context': context}
        location = Location(line=line, col=offset, filename=filename)
        super().__init__(fields=fields, location=location, **kwargs)


class incorrect_number_of_sections(SourceFeedback):
    """ Incorrect number of sections """
    title = "Incorrect Number of Sections"
    text_template = ("Incorrect number of sections in your file. "
                     "Expected {count}, but only found {found}")
    justification = ""

    def __init__(self, count, found, **kwargs):
        fields = {'count': count, 'found': found}
        super().__init__(fields=fields, **kwargs)

# TODO: IndentationError
# TODO: TabError
