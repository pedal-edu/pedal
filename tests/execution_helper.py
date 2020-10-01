import unittest
import io
from contextlib import contextmanager, redirect_stdout
from textwrap import dedent

from pedal.core import *
from pedal.core.report import MAIN_REPORT
from pedal.core.commands import clear_report, suppress, contextualize_report
from pedal.sandbox.commands import get_sandbox
from pedal.source import verify
from pedal.tifa import tifa_analysis
from pedal.resolvers import simple
from pedal.sandbox import commands
from pedal.cait.cait_api import parse_program

SUCCESS_MESSAGE = "Complete\nGreat work!"
SUCCESS_TEXT = "Great work!"


class ExecutionTestCase(unittest.TestCase):
    def assertFeedback(self, execution, feedback_string):
        """

        Args:
            execution:
            feedback_string:

        Returns:

        """
        return self.assertEqual(dedent(feedback_string).lstrip(), execution.feedback)



class Execution:
    """

    """
    def __init__(self, code, tracer_style='none', old_style_messages=False,
                 run_tifa=True, report=MAIN_REPORT):
        self.code = code
        self.tracer_style = tracer_style
        self.old_style_messages = old_style_messages
        self.report=report
        self.final = None
        self.run_tifa = run_tifa

    def __enter__(self):
        clear_report(report=self.report)
        contextualize_report(self.code, report=self.report)
        verify(report=self.report)
        if self.run_tifa:
            tifa_analysis(report=self.report)
        # TODO: Clean this up
        self.student = get_sandbox(self.report)
        self.report['sandbox']['sandbox'].tracer_style = self.tracer_style
        commands.run()
        return self

    def __exit__(self, *args):
        suppress("runtime", "FileNotFoundError", report=self.report)
        self.final = simple.resolve()
        self.feedback = """{title}\n{message}""".format(
            title=self.final.title,
            message=self.final.message
        )