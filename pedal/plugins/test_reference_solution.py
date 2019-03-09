'''
Tool for running a Grading script through a series of student reference
solutions.

python -m pedal.plugins.test_reference_solution <path to grade script>
'''

# Runner
from pedal.report.imperative import clear_report, MAIN_REPORT
from pedal.cait import parse_program
import sys
import os
from io import StringIO
from contextlib import redirect_stdout
import unittest
from unittest.mock import patch, mock_open
import argparse

# Arguments
DEFAULT_REFERENCE_SOLUTIONS_DIR = "reference_solutions/"


class TestReferenceSolutions(unittest.TestCase):
    maxDiff = None


def substitute_args(arg, student_path, seed):
    if arg == "$_STUDENT_MAIN":
        return student_path
    elif arg == "$_STUDENT_NAME":
        return seed
    return arg


def add_test(class_, name, python_file,
             expected_output_path, expected_output,
             grader_code, grader_path, grader_args, student_path):
    seed = find_seed(python_file)
    grader_args = [substitute_args(arg, student_path, seed) for arg in grader_args]
    def _inner_test(self):
        captured_output = StringIO()
        with redirect_stdout(captured_output):
            # TODO: mock_open will only work if we are not anticipating
            # the student or instructor to open files...
            with patch('builtins.open', mock_open(read_data=python_file),
                       create=True):
                with patch.object(sys, 'argv', grader_args):
                    clear_report()
                    grader_exec = compile(grader_code, grader_path, 'exec')
                    exec(grader_exec, globals())
                    #print(repr(MAIN_REPORT.feedback[0].mistake['error']))
        actual_output = captured_output.getvalue()
        if expected_output is None:
            print("File not found:", expected_output_path)
            with open(expected_output_path, 'w') as out:
                out.write(actual_output)
            print("\tCreated missing file with current output")
        else:
            self.assertEqual(actual_output, expected_output)
    setattr(class_, 'test_' + name, _inner_test)

def find_seed(python_code):
    try:
        ast = parse_program(python_code)
        for assign in ast.find_all("Assign"):
            if assign.targets[0].ast_name != "Name":
                continue
            if assign.targets[0].id == "__STUDENT_SEED__":
                if assign.value.ast_name == "Str":
                    return assign.value.s
                elif assign.value.ast_name == "Num":
                    return assign.value.n
                elif assign.value.ast_name == "List":
                    return [e.n for e in assign.value.elts]
    except SyntaxError:
        return 0
    return 0

# Load reference solutions
def add_all_tests(grader_path, reference_solutions_dir, grader_args, limit):
    # Load grader file
    with open(grader_path, 'r') as grader_file:
        grader_code = grader_file.read()
    for filename in os.listdir(reference_solutions_dir):
        if limit is not None and limit != filename:
            continue
        path = os.path.join(reference_solutions_dir, filename)
        if path.endswith(".py"):
            text_path = path[:-2] + "txt"
            with open(path, 'r') as python_file:
                python = python_file.read()
            if os.path.exists(text_path):
                with open(text_path, 'r') as output_file:
                    output = output_file.read()
            else:
                output = None
            add_test(TestReferenceSolutions, filename[:-3], python,
                     text_path, output, 
                     grader_code, grader_path, grader_args, path)


def run_tests():
    unittest.main(argv=['first-arg-is-ignored'])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run instructor grading script on a collection of reference solutions')
    parser.add_argument('grader', help='The path to the instructor grading script.')
    parser.add_argument('--path', '-p',
                        help='The path to the student reference files. If not given, assumed to be in the same folder '
                             'as the instructor grading script.',
                        default=DEFAULT_REFERENCE_SOLUTIONS_DIR)
    parser.add_argument('--args', '-a',
                        help='Pass in arguments that the grading script will use. '
                             'Variable substitutions include "$_STUDENT_MAIN".',
                        default='test_reference_solution.py,$_STUDENT_MAIN,$_STUDENT_NAME')
    parser.add_argument('--limit', '-l', help='Limit to a specific file.', default=None)
    args = parser.parse_args()
    
    # Turn the reference solutions path into an absolute filename
    if os.path.isabs(args.path):
        reference_solutions_path = args.path
    else:
        reference_solutions_path = os.path.join(os.path.dirname(args.grader), args.path)
    
    # If no reference solutions folder, let's make it
    if not os.path.exists(reference_solutions_path):
        os.mkdir(reference_solutions_path)
    
    # Fix up the passed in args
    grader_args = args.args.split(",")
    
    # Check that we actually have some files to try out
    if not os.listdir(reference_solutions_path):
        print("No reference solutions found")
    else:
        add_all_tests(args.grader, reference_solutions_path, grader_args, args.limit)
        run_tests()
