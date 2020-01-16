import unittest
import os
import sys
from textwrap import dedent

from pedal.toolkit.records import check_record_instance

pedal_library = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, pedal_library)

here = "" if os.path.basename(os.getcwd()) == "tests" else "tests/"

from pedal.core import *
from pedal.source import set_source

from pedal.cait.cait_api import parse_program
from pedal.sandbox.sandbox import Sandbox
from pedal.toolkit.files import files_not_handled_correctly
from pedal.toolkit.functions import (match_signature, output_test, unit_test,
                                     check_coverage, match_parameters)
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
from pedal.questions.loader import check_question
from tests.execution_helper import Execution


ADD5_QUESTION = {'functions': [{
    'name': 'add5',
    'parameters': ["int"],
    'cases': [{
        "arguments": [10],
        "returns": 15
    }, {
        "arguments": [20],
        "returns": 25
    }]
}]}

ADD5_QUESTION_SIGNATURE = {'functions': [{
    'name': 'add5',
    'signature': "int -> int",
    'cases': [{
        "arguments": [10],
        "returns": 15
    }, {
        "arguments": [20],
        "returns": 25
    }]
}]}

LIST_SIGNATURE = {'functions': [{
    'name': 'summate',
    'signature': "[int] -> int",
    'cases': [{
        "arguments": [[40, 20, 30, 10]],
        "returns": 100
    }]
}]}

class TestQuestionsLoader(unittest.TestCase):

    def test_loading_simple_question(self):
        with Execution('def undefined():\n pass\nundefined()') as e:
            check_question(ADD5_QUESTION)
        self.assertEqual(e.message, "No function named `add5` was found.")

        with Execution('def add5():\n pass\nadd5()') as e:
            check_question(ADD5_QUESTION)
        self.assertEqual(e.message, "The function named `add5` has fewer parameters (0) than expected (1).")

        with Execution('def add5(a, b):\n pass\nadd5(1, 2)') as e:
            check_question(ADD5_QUESTION)
        self.assertEqual(e.message, "The function named `add5` has more parameters (2) than expected (1).")

        with Execution('def add5(a):\n return 7\nadd5(1)') as e:
            check_question(ADD5_QUESTION)
        self.assertEqual(e.message, """I ran your function <code>add5</code> on my own test cases. It failed 2/2 of my tests.
<table class='pedal-test-cases table table-sm table-bordered table-hover'>
    <tr class='table-active'>
        <th></th>
        <th>Arguments</th>
        <th>Expected</th>
        <th>Returned</th>
    </tr>
        <tr>
        <td>&#10060;</td>
        <td><code>10</code></td>
        <td><code>15</code></td>
        <td><code>7</code></td>
    </tr>
    <tr>
        <td>&#10060;</td>
        <td><code>20</code></td>
        <td><code>25</code></td>
        <td><code>7</code></td>
    </tr>
</table>""")

        with Execution('def add5(a):\n a+""\nadd5("1")') as e:
            check_question(ADD5_QUESTION)
        self.assertEqual(e.message, """I ran your function <code>add5</code> on my own test cases. It failed 2/2 of my tests.
<table class='pedal-test-cases table table-sm table-bordered table-hover'>
    <tr class='table-active'>
        <th></th>
        <th>Arguments</th>
        <th>Expected</th>
        <th>Returned</th>
    </tr>
        <tr>
        <td>&#10060;</td>
        <td><code>10</code></td>
        <td colspan='2'>Error: <code>unsupported operand type(s) for +: 'int' and 'str'</code></td>
    </tr>
    <tr>
        <td>&#10060;</td>
        <td><code>20</code></td>
        <td colspan='2'>Error: <code>unsupported operand type(s) for +: 'int' and 'str'</code></td>
    </tr>
</table>""")

        with Execution('def add5(a):\n return a+5\nadd5(3)') as e:
            check_question(ADD5_QUESTION)
        self.assertEqual(e.message, "Great work!")

    def test_loading_signature_question(self):
        with Execution('def add5(a):\n return a+5\nadd5(3)') as e:
            check_question(ADD5_QUESTION_SIGNATURE)
        self.assertEqual(e.message, "Error in definition of function `add5` signature. Expected `int -> int`, instead found `Any -> Any`.")

        with Execution('def add5(a: int):\n return a+5\nadd5(3)') as e:
            check_question(ADD5_QUESTION_SIGNATURE)
        self.assertEqual(e.message, "Error in definition of function `add5` signature. Expected `int -> int`, instead found `int -> Any`.")

        with Execution('def add5(a: int) -> int:\n return a+5\nadd5(3)') as e:
            check_question(ADD5_QUESTION_SIGNATURE)
        self.assertEqual(e.message, "Great work!")

    def test_loading_list_question(self):
        with Execution('def summate(vals: [int]) -> int:\n return sum(vals)\nsummate([1,2,3])') as e:
            check_question(LIST_SIGNATURE)
        self.assertEqual(e.message, "Great work!")

if __name__ == '__main__':
    unittest.main(buffer=False)
