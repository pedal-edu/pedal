"""
A simple environment for quickly running Pedal code.

Get submission (Main Code, Main Filename, Other Code, Other Settings) from
    function call
    sys.args
        filename
        parameter
    global variable
    filename

"""

from pedal.core.environment import Environment
from pedal.core.commands import contextualize_report
from pedal.core.submission import Submission
from pedal.source import verify
from pedal.cait import parse_program
from pedal.sandbox import run
from pedal.tifa import tifa_analysis
from pedal.resolvers import simple


class SimpleEnvironment(Environment):
    """

    """
    def __init__(self, code):
        contextualize_report(Submission({'answer.py': code}))
        verify()
        self.ast = parse_program()
        self.tifa = tifa_analysis()
        self.student = run()

    def resolve(self):
        """

        Returns:

        """
        return simple.resolve()