"""
Outputs in GradeScope format

Dumps the JSON in the expected file location.

$> pedal feedback \
        /autograder/run_autograder/on_run.py \
        /autograder/submission \
        --environment gradescope > \
        "/autograder/results/results.json"

{ "score": 44.0, // optional, but required if not on each test case below. Overrides total of tests if specified.
  "output": "Text relevant to the entire submission", // optional
  "visibility": "after_due_date", // Optional visibility setting
  "stdout_visibility": "visible", // Optional stdout visibility setting
  "extra_data": {}, // Optional extra data to be stored
  "tests": // Optional, but required if no top-level score
    [
        {
            "score": 2.0, // optional, but required if not on top level submission
            "max_score": 2.0, // optional
            "name": "Your name here", // optional
            "number": "1.1", // optional (will just be numbered in order of array if no number given)
            "output": "Giant multiline string that will be placed in a <pre> tag and collapsed by default", // optional
            "tags": ["tag1", "tag2", "tag3"], // optional
            "visibility": "visible", // Optional visibility setting
            "extra_data": {} // Optional extra data to be stored
        },
        // and more test cases...
    ],
  "leaderboard": // Optional, will set up leaderboards for these values
    [
      {"name": "Accuracy", "value": .926},
      {"name": "Time", "value": 15.1, "order": "asc"},
      {"name": "Stars", "value": "*****"}
    ]
}

"""
import re
import sys
import json
from html.parser import HTMLParser
import tabulate

from pedal.resolvers.core import make_resolver
from pedal.source import verify, next_section as original_next_section
from pedal.core.feedback import Feedback
from pedal.core.environment import Environment
from pedal.core.report import MAIN_REPORT
from pedal.sandbox import run, get_sandbox, set_input, start_trace, get_output
from pedal.source.sections import FeedbackSourceSection
from pedal.tifa import tifa_analysis
from pedal.resolvers.simple import resolve as simple_resolve, by_priority
from pedal.resolvers.sectional import resolve as original_sectional_resolve
from pedal.core.formatting import Formatter, HtmlFormatter


class GradeScopeEnvironment(Environment):
    """
    Configures the BlockPy programming environment.
    """
    def __init__(self, files=None, main_file='answer.py', main_code=None,
                 user=None, assignment=None, course=None, execution=None,
                 instructor_file='on_run.py', skip_tifa=False, skip_run=False,
                 inputs=None, set_success=True,
                 report=MAIN_REPORT, trace=True):
        super().__init__(files=files, main_file=main_file, main_code=main_code,
                         user=user, assignment=assignment, course=course,
                         execution=execution, instructor_file=instructor_file,
                         report=report)
        self.skip_run = skip_run
        self.skip_tifa = skip_tifa
        self.trace = trace
        report.set_formatter(HtmlFormatter(report))
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


setup_environment = GradeScopeEnvironment


def dump_feedback(**results):
    print(json.dumps(results))


score_maximum = 1


@make_resolver
def detailed_resolver(report=MAIN_REPORT, priority_key=by_priority):
    """ Group by category, provide all the non-muted activated feedback """
    pass


@make_resolver
def resolve(report=MAIN_REPORT, priority_key=by_priority):
    """

    Args:
        report:
        custom_success_message:
    """
    final = simple_resolve(report, priority_key=priority_key)
    tests = []
    if final.positives:
        for positive in final.positives:
            test = {"name": positive.title}
            if positive.title != positive.message:
                test['output'] = positive.message
            tests.append(test)

    dump_feedback(
        score=round(final.score*score_maximum),
        output=f"<strong>{final.title}</strong><br>\n{final.message}",
        tests=tests
    )


@make_resolver
def sectional_resolve(report=MAIN_REPORT, priority_key=by_priority):
    """

    Args:
        report:
        custom_success_message:
    """
    finals = original_sectional_resolve(report, priority_key=priority_key)
    #if final.positives:
    #    print("-Positive Notes")
    #    for positive in final.positives:
    #        print(positive)
    global_feedbacks = sorted([f for f in report.feedback if f.parent is None],
                              key=lambda f: f.section_number if isinstance(f, FeedbackSourceSection) else -1)
    tests = []
    for global_feedback in global_feedbacks:
        if isinstance(global_feedback, FeedbackSourceSection):
            test = {"number": global_feedback.section_number,
                    "name": f"Part {global_feedback.section_number}"}
            final = finals.get(global_feedback)
            if final:
                test['output'] = final.title + "\n" + final.message
            else:
                test['output'] = "No feedback for this section"
        # TODO: Should we be skipping all global feedback? Need more examples
    total_score = sum(f.score for f in finals.values())
    dump_feedback(
        score=round(total_score * score_maximum),
        output="Feedback is below",
        tests=tests
    )


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


class GradeScopeFormatter(HtmlFormatter):

    def python_code(self, code):
        return self.pre(code)

    def python_expression(self, code):
        return self.html_code(code)

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
