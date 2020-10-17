import unittest
import os
import sys
from textwrap import dedent

pedal_library = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, pedal_library)

here = "" if os.path.basename(os.getcwd()) == "tests" else "tests/"

from pedal.questions.loader import check_question
from tests.execution_helper import Execution, ExecutionTestCase

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

@unittest.skip
class TestQuestionsLoader(ExecutionTestCase):

    def test_loader_missing_function(self):
        with Execution('def undefined():\n pass\nundefined()', run_tifa=False) as e:
            check_question(ADD5_QUESTION)
        self.assertFeedback(e, "Instructor Feedback\nNo function named `add5` was found.")

    def test_loader_fewer_parameters(self):
        with Execution('def add5():\n pass\nadd5()') as e:
            check_question(ADD5_QUESTION)
        self.assertFeedback(e, "Instructor Feedback\nThe function named `add5` has fewer parameters (0) than expected (1).")

    def test_loader_more_parameters(self):
        with Execution('def add5(a, b):\n a\n b\nadd5(1, 2)') as e:
            check_question(ADD5_QUESTION)
        self.assertFeedback(e, "Instructor Feedback\nThe function named `add5` has more parameters (2) than expected (1).")

    def test_loader_failing_tests(self):
        with Execution('def add5(a):\n return 7+a-a\nadd5(1)') as e:
            check_question(ADD5_QUESTION)
        self.assertFeedback(e, """Instructor Feedback
I ran your function <code>add5</code> on my own test cases. It failed 2/2 of my tests.
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

    def test_loader_error_tests(self):
        with Execution('def add5(a):\n a+""\nadd5("1")') as e:
            check_question(ADD5_QUESTION)
        self.assertFeedback(e, """Instructor Feedback
I ran your function <code>add5</code> on my own test cases. It failed 2/2 of my tests.
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

    def test_loader_success(self):
        with Execution('def add5(a):\n return a+5\nadd5(3)') as e:
            check_question(ADD5_QUESTION)
        self.assertFeedback(e, "Complete\nGreat work!")

    # TODO: Finish this test once the functionality is ready!
    @unittest.skip
    def test_loading_signature_no_parameter_type(self):
        with Execution('def add5(a):\n return a+5\nadd5(3)') as e:
            check_question(ADD5_QUESTION_SIGNATURE)
        self.assertFeedback(e, "Instructor Feedback\nError in definition of function `add5` signature. Expected `int -> int`, instead found `Any -> Any`.")

    # TODO: Finish this test once the functionality is ready!
    @unittest.skip
    def test_loading_signature_no_return_type(self):
        with Execution('def add5(a: int):\n return a+5\nadd5(3)') as e:
            check_question(ADD5_QUESTION_SIGNATURE)
        self.assertFeedback(e, "Instructor Feedback\nError in definition of function `add5` signature. Expected `int -> int`, instead found `int -> Any`.")

    # TODO: Finish this test once the functionality is ready!
    @unittest.skip
    def test_loading_signature_correct_type(self):
        with Execution('def add5(a: int) -> int:\n return a+5\nadd5(3)') as e:
            check_question(ADD5_QUESTION_SIGNATURE)
        self.assertFeedback(e, "Complete\nGreat work!")

    # TODO: Finish this test once the functionality is ready!
    @unittest.skip
    def test_loading_list_question(self):
        with Execution('def summate(vals: [int]) -> int:\n return sum(vals)\nsummate([1,2,3])') as e:
            check_question(LIST_SIGNATURE)
        self.assertFeedback(e, "Complete\nGreat work!")

if __name__ == '__main__':
    unittest.main(buffer=False)
