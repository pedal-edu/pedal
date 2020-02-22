from pedal.core import *
from pedal.core.report import MAIN_REPORT
from pedal.core.commands import clear_report, suppress, contextualize_report
from pedal.sandbox.compatibility import get_sandbox
from pedal.source import verify
from pedal.tifa import tifa_analysis
from pedal.resolvers import simple
from pedal.sandbox import compatibility
from pedal.cait.cait_api import parse_program


class Execution:
    def __init__(self, code, tracer_style='none', old_style_messages=False, report=MAIN_REPORT):
        self.code = code
        self.tracer_style = tracer_style
        self.old_style_messages = old_style_messages
        self.report=report
        self.final = None

    def __enter__(self):
        clear_report(report=self.report)
        contextualize_report(self.code, report=self.report)
        verify(report=self.report)
        tifa_analysis(report=self.report)
        # TODO: Clean this up
        self.student = get_sandbox(self.report)
        self.student.report_exceptions_mode = True
        self.report['sandbox']['run'].tracer_style = self.tracer_style
        compatibility.run_student(raise_exceptions=True, old_style_messages=self.old_style_messages)
        return self

    def __exit__(self, *args):
        suppress("runtime", "FileNotFoundError", report=self.report)
        self.final = simple.resolve()
        self.feedback = """{title}\n{message}""".format(
            title=self.final.title,
            message=self.final.message
        )
