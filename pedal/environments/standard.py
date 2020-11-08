"""
A simple environment for quickly running Pedal code.
"""

import sys

from pedal.assertions import resolve_all
from pedal.core.environment import Environment
from pedal.core.report import MAIN_REPORT
from pedal.source import verify
from pedal.cait import parse_program
from pedal.sandbox.commands import run
from pedal.resolvers import simple


def parse_argv():
    """ Retrieve fields from sys.argv """
    if len(sys.argv) == 2:
        main_file = sys.argv[1]
        with open(main_file) as main_file_handle:
            main_code = main_file_handle.read()
        return sys.argv[0], {main_file: main_code}, main_file, main_code, None, None, None, None
    # elif len(sys.argv) == 3:
    else:
        return sys.argv
    # TODO: Finish handling arguments intelligently


class StandardEnvironment(Environment):
    """
    The StandardEnvironment is a convenience class for basic command line
    usage of Pedal. It doesn't do very much, but runs a few of our tools:
    CAIT, TIFA, and Sandbox. It uses the Simple resolver, and just dumps the
    result to the command line.

    from pedal.environments.standard import setup_pedal
    code, student, resolve = setup_pedal()
    """
    def __init__(self, files=None, main_file='answer.py', main_code=None,
                 user=None, assignment=None, course=None, execution=None,
                 instructor_file='on_run.py', skip_tifa=False, set_success=True,
                 report=MAIN_REPORT):
        # Possibly user passed in stuff via the command line.
        if files is None and main_code is None:
            (instructor_file, files, main_file, main_code, user, assignment,
             course, execution) = parse_argv()
        super().__init__(files=files, main_file=main_file, main_code=main_code,
                         user=user, assignment=assignment, course=course,
                         execution=execution, instructor_file=instructor_file,
                         report=report)
        # Then default custom stuff
        verify(report=report)
        self.ast = parse_program(report=report)
        if skip_tifa:
            self.tifa = None
        else:
            from pedal.tifa import tifa_analysis
            self.tifa = tifa_analysis(report=report)
        self.student = run(threaded=True, report=report)
        self.set_success = set_success

    def print_resolve(self, *args, **kwargs):
        """
        Trivial formatter for resolver, just dumps the
        Title/Label/Score/Message. Any arguments are forwarded to
        :py:func:`pedal.resolvers.simple.resolve`
        """
        #resolve_all(set_successful=self.set_success, no_phases_is_success=True,
        #            report=self.report)
        # TODO: Fix resolve_all
        result = simple.resolve(*args, **kwargs)
        # print("Feedback Label:", result.label)
        print("Title:", result.title)
        print("Label:", result.label)
        print("Score:", result.score)
        print("Message:", result.message)
        return result

    def get_fields(self):
        """ Returns Cait's AST, the student Sandbox,
            and the Simple Resolver. """
        return self.ast, self.student, self.print_resolve


setup_environment = StandardEnvironment
