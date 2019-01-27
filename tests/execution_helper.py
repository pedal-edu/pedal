from pedal.report import *
from pedal.source import set_source
from pedal.tifa import tifa_analysis
from pedal.resolvers import simple
from pedal.sandbox import compatibility
from pedal.cait.cait_api import parse_program


class Execution:
    def __init__(self, code, tracer_style='none', old_style_messages=False):
        self.code = code
        self.tracer_style = tracer_style
        self.old_style_messages = old_style_messages

    def __enter__(self):
        clear_report()
        set_source(self.code)
        tifa_analysis()
        self.student = compatibility._check_sandbox(MAIN_REPORT)
        self.student.report_exceptions_mode = True
        MAIN_REPORT['sandbox']['run'].tracer_style = self.tracer_style
        compatibility.run_student(raise_exceptions=True, old_style_messages=self.old_style_messages)
        return self

    def __exit__(self, *args):
        suppress("runtime", "FileNotFoundError")
        (self.success, self.score, self.category, self.label,
         self.message, self.data, self.hide) = simple.resolve()
        self.feedback = """{label}<br>{message}""".format(
            label=self.label,
            message=self.message
        )
