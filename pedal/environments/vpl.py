"""
Some kind of function to break up the sections
"""
import re
import sys
from html.parser import HTMLParser

from pedal.resolvers.core import make_resolver
from pedal.source import verify, next_section as original_next_section
from pedal.core.feedback import Feedback
from pedal.core.environment import Environment
from pedal.core.report import MAIN_REPORT
from pedal.sandbox import run, get_sandbox, set_input, start_trace
from pedal.source.sections import FeedbackSourceSection
from pedal.tifa import tifa_analysis
from pedal.resolvers.simple import resolve as simple_resolve, by_priority
from pedal.resolvers.sectional import resolve as original_sectional_resolve
from pedal.core.formatting import Formatter

import tabulate


class VPLEnvironment(Environment):
    """
    Configures the BlockPy programming environment.
    """
    def __init__(self, files=None, main_file='answer.py', main_code=None,
                 user=None, assignment=None, course=None, execution=None,
                 instructor_file='on_run.py', skip_tifa=True, skip_run=False,
                 inputs=None, set_success=True,
                 report=MAIN_REPORT, trace=True):
        super().__init__(files=files, main_file=main_file, main_code=main_code,
                         user=user, assignment=assignment, course=course,
                         execution=execution, instructor_file=instructor_file,
                         report=report)
        self.skip_run = skip_run
        self.skip_tifa = skip_tifa
        self.trace = trace
        report.set_formatter(VPLFormatter(report))
        verify(report=self.report)
        if not skip_tifa:
            tifa_analysis(report=self.report)
        if inputs:
            set_input(inputs)
        if skip_run:
            student = get_sandbox(report=report)
        else:
            if trace:
                start_trace()
            student = run(report=report)
        self.fields = {
            'student': student,
            'resolve': resolve,
            'next_section': self.next_section,
            'sectional_resolve': sectional_resolve
        }

    def next_section(self, name=""):
        original_next_section(name=name, report=self.report)
        verify(report=self.report)
        if not self.skip_tifa:
            tifa_analysis(report=self.report)
        student = get_sandbox(report=self.report)
        if self.skip_run:
            student.clear()
        else:
            if self.trace:
                start_trace()
            student.clear()
            student = student.run()
        return student

    def load_main(self, path):
        """
        Allowed to return either a string value (the contents of the file)
        or the exception that was raised.
        """
        try:
            return super().load_main(path)
        except OSError as file_error:
            return file_error


setup_environment = VPLEnvironment

## TODO: Check if file exists

class VPLFormatter(Formatter):

    def pre(self, text):
        return "\n".join([">" + line for line in text.split("\n")])

    def python_code(self, code):
        return self.pre(code)

    def python_expression(self, code):
        return code

    def filename(self, filename):
        return filename

    def python_value(self, code):
        return self.pre(code)

    def inputs(self, inputs):
        return self.pre(inputs)

    def output(self, output):
        return self.pre(output)

    def traceback(self, traceback):
        return traceback

    def name(self, name):
        return name

    def line(self, line_number):
        return line_number

    def frame(self, name):
        return name

    def exception(self, exception):
        return self.pre(exception)

    def table(self, rows, columns):
        return self.pre(tabulate.tabulate(rows, headers=columns))


score_maximum = 1


def set_maximum_score(number):
    """
    TODO: Attach data to the Report instead of a global variable.

    Args:
        number:
        cap:
        report:
    """
    global score_maximum
    score_maximum = number


@make_resolver
def resolve(report=MAIN_REPORT, priority_key=by_priority):
    """

    Args:
        report:
        custom_success_message:
    """
    print("<|--")
    final = simple_resolve(report, priority_key=priority_key)
    if final.positives:
        print("-Positive Notes")
        for positive in final.positives:
            print(positive)
    if final.systems:
        print("-System Notes")
        for system in final.systems:
            if system.label and system.label != "log":
                print(system.title)
            if system.label and system.label != "log":
                print(system.label)
            if system.message:
                print(system.message)
    print("-"+final.title)
    print(final.message)
    print("--|>")
    print("Grade :=>>", round(final.score*score_maximum))


import sys
stdout = sys.stdout

@make_resolver
def sectional_resolve(report=MAIN_REPORT, priority_key=by_priority):
    """

    Args:
        report:
        custom_success_message:
    """
    print("<|--")
    print(report.get_current_group(), file=stdout)
    finals = original_sectional_resolve(report, priority_key=priority_key)
    #if final.positives:
    #    print("-Positive Notes")
    #    for positive in final.positives:
    #        print(positive)
    global_feedbacks = sorted([f for f in report.feedback if f.parent is None],
                              key=lambda f: f.section_number if isinstance(f, FeedbackSourceSection) else -1)
    for global_feedback in global_feedbacks:
        if isinstance(global_feedback, FeedbackSourceSection):
            print(f"-Part {global_feedback.section_number}")
            final = finals.get(global_feedback)
            if final:
                print(final.title)
                print(final.message)
            else:
                print("No feedback for this section")
        # TODO: Should we be skipping all global feedback? Need more examples
        #else:
        #    print(global_feedback.title)
        #    print(global_feedback.message)
    print("--|>")
    total_score = sum(f.score for f in finals.values())
    print("Grade :=>>", round(total_score*score_maximum))
