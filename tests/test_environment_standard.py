import os
import sys
import io
from contextlib import redirect_stdout
import unittest

from pedal import MAIN_REPORT, call
from pedal.utilities.system import IS_AT_LEAST_PYTHON_311

pedal_library = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, pedal_library)

here = "" if os.path.basename(os.getcwd()) == "tests" else "tests/"

from tests.execution_helper import ExecutionTestCase
from pedal.environments.standard import setup_environment
from pedal.source import next_section, verify_section, check_section_exists, set_source_file, separate_into_sections
from pedal.core.commands import compliment, clear_report, contextualize_report, log, explain
from pedal.assertions import assert_equal, prevent_ast


class TestEnvironmentStandard(ExecutionTestCase):

    def checkFeedback(self, actual, expected):
        self.assertEqual(expected.strip(), actual.strip())

    def test_correct(self):
        with io.StringIO() as f, redirect_stdout(f):
            terminal = setup_environment(main_code="""1+2""")
            terminal.resolve()
            clear_report()
            self.checkFeedback(f.getvalue(), '''
Title: Complete
Label: set_correct_no_errors
Score: 1
Message: Great work!
''')

    def test_empty_source(self):
        with io.StringIO() as f, redirect_stdout(f):
            terminal = setup_environment(main_code="")
            terminal.resolve()
            clear_report()
            self.checkFeedback(f.getvalue(), '''
Title: No Source Code
Label: blank_source
Score: 0
Message: Source code file is blank.
''')

    def test_compliments(self):
        with io.StringIO() as f, redirect_stdout(f):
            standard = setup_environment(main_code="1+2")
            compliment("Good job!")
            standard.resolve()
            clear_report()
            self.checkFeedback(f.getvalue(), '''
Title: Complete
Label: set_correct_no_errors
Score: 1
Message: Great work!
Compliments:
  - Good job!
''')