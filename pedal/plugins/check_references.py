# Runner
from pedal.report.imperative import clear_report
import sys
import os
from io import StringIO
from contextlib import redirect_stdout
import unittest
from unittest.mock import patch, mock_open

# Arguments
GRADER_PATH = sys.argv[1]
REFERENCE_SOLUTIONS_DIR = "reference_solutions/"

# Load grader file
with open(GRADER_PATH, 'r') as grader_file:
    grader_code = grader_file.read()

# Load Pedal from dev location
PEDAL_DIR = r"C:/Users/acbart/projects/pedal/"
sys.path.insert(0, PEDAL_DIR)


# Load reference solutions


class TestReferenceSolutions(unittest.TestCase):
    maxDiff = None


def add_test(class_, name, python_file, expected_output):
    def _inner_test(self):
        captured_output = StringIO()
        with redirect_stdout(captured_output):
            # TODO: mock_open will only work if we are not anticipating
            # the student or instructor to open files...
            with patch('builtins.open', mock_open(read_data=python_file),
                       create=True):
                clear_report()
                compile(grader_code, GRADER_PATH, 'exec')
                exec(grader_code, globals())
        actual_output = captured_output.getvalue()
        self.assertEqual(actual_output, expected_output)

    setattr(class_, 'test_' + name, _inner_test)


for filename in os.listdir(REFERENCE_SOLUTIONS_DIR):
    path = os.path.join(REFERENCE_SOLUTIONS_DIR, filename)
    if path.endswith(".py"):
        text_path = path[:-2] + "txt"
        with open(path, 'r') as python_file:
            python = python_file.read()
        with open(text_path, 'r') as output_file:
            output = output_file.read()
        add_test(TestReferenceSolutions, filename[:-3], python, output)

if __name__ == "__main__":
    unittest.main()
