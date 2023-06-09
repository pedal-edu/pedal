from pedal import verify, allow_real_io, block_real_io
from pedal.core.environment import Environment
from pedal.core.formatting import HtmlFormatter
from pedal.core.report import MAIN_REPORT
from pedal.sandbox import run, get_sandbox, set_input, start_trace
from pedal.tifa import tifa_analysis
from pedal.resolvers.simple import resolve
from pedal.core.formatting import Formatter


class TerminalFormatter(Formatter):
    def name(self, name):
        return f"\033[1m\033[96m{name}\033[0m"

    def line(self, line_number):
        return f"\033[4m{line_number}\033[0m"


def resolve_on_terminal(report=MAIN_REPORT):
    print()
    print("\033[47m", " " * 35, "FEEDBACK", " " * 35, "\033[0m")
    feedback = resolve(report)
    if feedback.success:
        print(f"\033[42m✔️  {feedback.title}\033[0m")
        print(f"{feedback.message}")
    else:
        print(f"\033[41m❌  {feedback.title}\033[0m")
        print(f"\033[0m{feedback.message}")
    print("\033[47m", " " * 33, "END FEEDBACK", " " * 33, "\033[0m")


class TerminalEnvironment(Environment):
    """
    Configures the BlockPy programming environment.
    """
    def __init__(self, files=None, main_file='answer.py', main_code=None,
                 user=None, assignment=None, course=None, execution=None,
                 instructor_file='on_run.py', skip_tifa=False, skip_run=False,
                 inputs=None, set_correct=True, set_success=None,
                 report=MAIN_REPORT, trace=True, threaded=False, real_io=True):
        super().__init__(files=files, main_file=main_file, main_code=main_code,
                         user=user, assignment=assignment, course=course,
                         execution=execution, instructor_file=instructor_file,
                         report=report)
        report.set_formatter(TerminalFormatter(report))
        verify(report=self.report)
        if not skip_tifa:
            tifa_analysis(report=self.report)
        if inputs:
            set_input(inputs)
        if skip_run:
            student = get_sandbox(report=report)
            student.threaded = threaded
        else:
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
            'resolve': resolve_on_terminal()
        }


setup_environment = TerminalEnvironment
