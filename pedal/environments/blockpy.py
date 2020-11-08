"""
Environment to support BlockPy.

# Support our sysmodules hack by clearing out any lingering old data
from pedal.core.report import MAIN_REPORT
MAIN_REPORT.clear()

# Interface for interacting with BlockPy
from utility import *

from pedal.environments.blockpy import setup_pedal
pedal = setup_pedal(skip_tifa=${skip_tifa},
                    main_file='answer.py',
                    main_code=${safeCode})

# Execute students' code
if not get_model_info('assignment.settings.disableInstructorRun'):
    set_inputs(get_model_info('execution.input'))
    student = run()
else:
    student = get_sandbox()

# Load in some commonly used tools
from pedal.cait.cait_api import parse_program
from pedal.sandbox.commands import *

# TODO: Refactor resolver to return instructions
# Monkey-patch questions
from pedal import questions
questions.show_question = set_instructions

# Run the actual instructor code
${instructorCode}

# Resolve everything
final = pedal.resolve()
SUCCESS = final.success
SCORE = final.score
CATEGORY = final.category
LABEL = final.title
MESSAGE = final.message
DATA = final.data
HIDE = final.hide_correctness
"""
from pedal import verify
from pedal.core.environment import Environment
from pedal.core.formatting import HtmlFormatter
from pedal.core.report import MAIN_REPORT
from pedal.sandbox import run, get_sandbox, set_input, start_trace
from pedal.tifa import tifa_analysis
from pedal.resolvers.simple import resolve
from pedal.resolvers.statistics import resolve as stats_resolve


class BlockPyEnvironment(Environment):
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
            'stats_resolve': stats_resolve
        }


setup_environment = BlockPyEnvironment

"""
TODO: Enhance the following

Override formatters
assertions could get HTML diffs
Grouping a bunch of assert_equal produces a table
"""
