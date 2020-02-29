import sys

from pedal.core.commands import contextualize_report
from pedal.sandbox import run
from pedal.core.environment import Environment
from pedal.core.submission import Submission


class SandboxEnvironment(Environment):
    """
    Sandbox Environment that simply runs the students code and spits out the
    output and any runtime errors. Does not attempt to provide feedback or run
    an instructor control script.

    """
    def __init__(self, code):
        contextualize_report(Submission({'answer.py': code}))
        self.student = run()

    def resolve(self):
        """

        Returns:

        """
        print(self.student.raw_output)
        if self.student.exception:
            print(self.student.exception_formatted, file=sys.stderr)
