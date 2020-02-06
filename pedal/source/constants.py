from pedal.core.commands import feedback
from pedal.core.report import MAIN_REPORT

TOOL_NAME_SOURCE = 'source'


def blank_source(group=None, report=MAIN_REPORT):
    feedback(blank_source.__name__, category=feedback.CATEGORIES.SYNTAX, tool=TOOL_NAME_SOURCE,
             title=blank_source.TITLE, version=blank_source.VERSION,
             group=group, message=blank_source.TEXT_TEMPLATE(), report=report)


blank_source.TITLE = "No Source Code"
blank_source.TEXT_TEMPLATE = "Source code file is blank.".format
blank_source.VERSION = '0.0.1'
blank_source.JUSTIFICATION = "After stripping the code, there were no characters."


def not_enough_sections(section_number, found, report=MAIN_REPORT):
    fields = {'count': section_number, 'found': found}
    return feedback(not_enough_sections.__name__, category=feedback.CATEGORIES.SYNTAX, tool=TOOL_NAME_SOURCE,
                    title=not_enough_sections.TITLE, version=not_enough_sections.VERSION,
                    fields=fields,
                    message=not_enough_sections.TEXT_TEMPLATE(**fields), report=report)


not_enough_sections.TITLE = "Not Enough Sections"
not_enough_sections.TEXT_TEMPLATE = ("Tried to advance to next section but the "
                                     "section was not found. Tried to load section "
                                     "{count}, but there were only {found} sections.").format
not_enough_sections.VERSION = '0.0.1'
not_enough_sections.JUSTIFICATION = "Section index exceeded the length of the separated sections list."


def syntax_error(line, filename, offset, text, traceback, exception, report=MAIN_REPORT):
    fields = {'lineno': line, 'filename': filename, 'offset': offset, 'text': text,
              'traceback': traceback, 'exception': exception}
    return feedback(syntax_error.__name__, category=feedback.CATEGORIES.SYNTAX, tool=TOOL_NAME_SOURCE,
                    title=syntax_error.TITLE, version=syntax_error.VERSION,
                    fields=fields,
                    message=syntax_error.MESSAGE_TEMPLATE(**fields),
                    text=syntax_error.TEXT_TEMPLATE(**fields),
                    report=report)


syntax_error.TITLE = "Syntax Error"
syntax_error.MESSAGE_TEMPLATE = "Bad syntax on line {lineno}".format
syntax_error.TEXT_TEMPLATE = "Bad syntax on line {lineno}".format
syntax_error.VERSION = '0.0.1'
syntax_error.JUSTIFICATION = "Syntax error was triggered while calling ast.parse"

# TODO: IndentationError
# TODO: TabError
# TODO: Decide if we wanna do .format at the end of every template... could be powerful with the
#       whole function call aspect.
# TODO: Move traceback fixing into a separate utilities module; drag in comparisons.
