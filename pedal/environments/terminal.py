import sys
import os

from pedal import verify, allow_real_io, block_real_io, get_python_errors
from pedal.core.environment import Environment
from pedal.core.report import MAIN_REPORT
from pedal.core.commands import set_correct as set_correct_feedback
from pedal.resolvers.core import make_resolver
from pedal.sandbox import run, get_sandbox, set_input, start_trace
from pedal.sandbox.feedbacks import runtime_error
from pedal.source.feedbacks import syntax_error
from pedal.tifa import tifa_analysis
from pedal.resolvers.simple import resolve
from pedal.core.formatting import Formatter

RESET = "\033[0;0m"
REVERSE = "\033[;7m"
UNDERLINE = "\033[4m"
# \033[1m\033[96m
BOLD_BRIGHT_COLOR = "\033[1;96m"
BOLD_RED = "\033[1;91m"
BOLD_GREEN = "\033[1;92m"
CHECKMARK = "\u2713"
CROSSMARK = "\u2717"


class TerminalFormatter(Formatter):
    def __init__(self, report=MAIN_REPORT, path_mask=None, **kwargs):
        super().__init__(report, **kwargs)
        self.path_mask = path_mask

    def name(self, name):
        return f"{BOLD_BRIGHT_COLOR}{name}{RESET}"

    def line(self, line_number):
        return f"{UNDERLINE}{line_number}{RESET}"

    def filename(self, filename):
        if self.path_mask:
            filename = filename.replace(self.path_mask, '')
        else:
            filename = os.path.basename(filename)
        return f"{UNDERLINE}{filename}{RESET}"


@make_resolver
def resolve_on_terminal(report=MAIN_REPORT):
    # print("\033[47m", "-" * 35, "FEEDBACK", "-" * 35, "\033[0m", file=file)
    feedback = resolve(report)
    print("")
    print(f"{REVERSE}FEEDBACK{RESET} Based on your code, here are some tips and recommendations:\n")
    if feedback.correct:
        print(f"{BOLD_GREEN}{CHECKMARK}{RESET}️  Your code ran successfully.\n")
        print(f"{feedback.message}")
    else:
        print(f"{BOLD_RED}{CROSSMARK}{RESET}  {feedback.title}\n")
        print(f"{feedback.message}")
    print("")

    # if feedback.category not in (FeedbackCategory.SYNTAX, FeedbackCategory.RUNTIME):
    # Print out the first runtime/syntax error that we encounter
    for python_error in get_python_errors(report):
        if python_error:
            print(f"{REVERSE}TERMINAL OUTPUT{RESET} For reference, here is the original Python error:")
            print(to_native_message(python_error))
        break
    return feedback


def to_native_message(error):
    return f"\n{error.fields['traceback_message']}\n{error.fields['exception_name']}: {error.fields['exception_message'].strip()}"


def enhance_native_errors():
    syntax_error.override(message_template="Bad syntax on line {lineno:line}.\n{suggestion_message}")
    runtime_error.override(message_template=(
        "{context_message}\n"
        "{exception_name_proper} occurred:\n\n"
        "{exception_message}\n\n"
        "{suggestion_message}"
    ))


class TerminalEnvironment(Environment):
    """
    Configures the BlockPy programming environment.

    Args:
        main_file (str): If `files` and `main_code` are not provided, then this should be the path to a file
            that contains the student's code. If `files` is not given but `main_code` is, then `main_code` will be
            the contents of that file and `main_file` will be the filename (defaults to `answer.py`). If `files` is
            given, then `main_file` will be used to select a `files` from that dictionary (defaults to `answer.py`).
    """

    def __init__(self, files=None, main_file='answer.py', main_code=None,
                 user=None, assignment=None, course=None, execution=None,
                 instructor_file='on_run.py', skip_tifa=False, skip_run=False,
                 inputs=None, set_correct=True, set_success=None,
                 report=MAIN_REPORT, trace=True, threaded=False, real_io=True, path_mask=None):
        super().__init__(files=files, main_file=main_file, main_code=main_code,
                         user=user, assignment=assignment, course=course,
                         execution=execution, instructor_file=instructor_file,
                         report=report)
        enhance_native_errors()
        report.set_formatter(TerminalFormatter(report, path_mask=path_mask))
        set_correct_feedback.override(message_template=("Great work! Based on your code submitted, there are no other "
                                                        "recommendations available. You can proceed to the next page "
                                                        "by using the “Next” button in your lesson."))
        verify(report=self.report)
        if not skip_tifa:
            tifa_analysis(report=self.report)
        if inputs:
            set_input(inputs)
        if skip_run:
            student = get_sandbox(report=report)
        else:
            print(f"{REVERSE}YOUR CODE{RESET} We ran your code. Here's the output:\n")
            if trace:
                start_trace()
            if real_io:
                allow_real_io()
            student = run(report=report, threaded=threaded)
            if real_io:
                block_real_io()
        student.threaded = threaded
        self.fields = {
            'student': student,
            'resolve': resolve_on_terminal
        }


setup_environment = TerminalEnvironment
