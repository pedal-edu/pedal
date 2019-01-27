import unittest
import os
import sys
from textwrap import dedent

pedal_library = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, pedal_library)

from pedal.report import *
from pedal.source import set_source

'''
from pedal.cait.cait_api import parse_program
from pedal.sandbox.sandbox import Sandbox
from pedal.toolkit.files import files_not_handled_correctly
from pedal.toolkit.functions import (match_signature, output_test, unit_test,
                                     check_coverage)
from pedal.toolkit.signatures import (function_signature)
from pedal.toolkit.utilities import (is_top_level, function_prints,
                                     no_nested_function_definitions,
                                     find_function_calls, function_is_called,
                                     only_printing_variables, prevent_literal,
                                     find_prior_initializations,
                                     prevent_unused_result, ensure_literal,
                                     prevent_builtin_usage, find_operation,
                                     prevent_advanced_iteration,
                                     ensure_operation, prevent_operation,
                                     ensure_assignment)
from pedal.toolkit.imports import ensure_imports
from pedal.toolkit.printing import ensure_prints
from pedal.toolkit.plotting import check_for_plot, prevent_incorrect_plt
'''
from pedal.assertions import *
from tests.execution_helper import Execution


class TestAssertions(unittest.TestCase):

    def test_exceptional_mode(self):
        with Execution('a = 0') as e:
            set_assertion_mode(exceptions=True)
            self.assertRaises(AssertionException, assertEqual, 1, 3)
        
    def test_assertion_mode(self):
        with Execution('a = 0\na') as e:
            @section(1)
            def part1():
                assertEqual(5, 0)
        
        self.assertEqual(e.feedback, "Instructor Test<br>5 != 0")

if __name__ == '__main__':
    unittest.main(buffer=False)
