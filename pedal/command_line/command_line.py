"""
A tool for running Pedal from the Command Line

./pedal command line interface
    simple example (single ICS, single student file)
    simple sandbox for just quickly running students code with no frills or extra behavior
        Maybe this is the "default" ICS?
    unit test a given curriculum (many ICS, many student files per)
    regrade some assignments, spit out subject/assignment/context (one ICS, many many student files)
    get summary stats from ProgSnap file (many ICS, many submissions
    Spit out the justifications alongside the potential feedback`
    Run the students code in a sandbox and spit out the runtime results

ProgSnap file with submissions AND assignments (+other info)
ProgSnap file with only submissions, ICS is separate
Single ICS file
    Single student file
    Archive Format
        Regular directory
        ZIP
        ProgSnap Folder
        ProgSnap SQL
    Structure
        Each file is a python file representing their submission:
            .+\.py
            Could have accompanying Markdown file
        Each folder is a submission
            .+/.+\.py
Folder of ICS files
    Potentially, submissions are within an accompanying "submissions" folder
    Regex for matching ICS files?



argparse options
    -i <instructor_control_script | python file or directory of scripts>
    -s <student_submission | single python file, directory of files, progsnap file>
    -o <output_file>
    -f <output format: Feedback, Grade, Debug mode, Unit Tests, research stats, Sandbox>

For each ICS we want to run
    For each student submission
        safely run it
    Potentially combine results
"""

import argparse
import os
import sys
from contextlib import redirect_stdout

from io import StringIO
from textwrap import indent

import unittest
from unittest.mock import patch

from pedal import clear_report
from pedal.core.report import MAIN_REPORT
from pedal.cait import parse_program
from pedal.command_line.mocks import MockOpen


def normalize_path(first: str, second: str):
    """
    If the `first` path is relative, creates an absolute path relative to the `second` folder.

    Args:
        first: The path to normalize
        second: The path to normalize in regards to.

    Returns:
        str: A new path.
    """
    if os.path.isabs(first):
        return first
    else:
        return os.path.join(os.path.dirname(second), first)


def find_seed(python_code):
    """
    Attempts to find a top-level variable named "__STUDENT_SEED__" inside the given python code.
    Args:
        python_code (str): A string of valid Python code.
    Returns:
        str or int or List[int]: The seed found in the file, or 0.
    """
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


def substitute_args(args, student_path, seed):
    """
    Updates the given arguments by replacing $template values with the given ones.

    Args:
        arg (List[str]):
        student_path (str):
        seed (Any):

    Returns:

    """
    for arg in args.split(","):
        if arg == "$_STUDENT_MAIN":
            yield student_path
        elif arg == "$_STUDENT_NAME":
            yield seed
        yield arg


def run_ics_on_submission(ics_filename: str, ics_contents: str, ics_args: str,
                          submission_filename: str, submission_contents: str,
                          output_format: str,
                          student: dict, course: dict, assignment: dict):
    """
    Runs the given instructor control script on the given submission, with the accompany contextualizations.

    Args:
        ics_filename (str):
        ics_contents (str):
        ics_args (str): Additional arguments for the ICS script.
        submission_filename (str):
        submission_contents (str):
        output_format (str): The format to use when running
        student (dict):
        course (dict):
        assignment (dict):

    Returns:

    """
    seed = find_seed(submission_contents)
    # TODO: figure out args
    #ics_args = list(substitute_args(ics_args, submission_filename, seed))
    ics_args = [ics_filename, {submission_filename: submission_contents},
                submission_filename, submission_contents,
                student, assignment, course, None]
    captured_output = StringIO()
    global_data = {}
    with redirect_stdout(captured_output):
        with patch('builtins.open', MockOpen(read_data=submission_contents),
                   create=True):
            with patch.object(sys, 'argv', ics_args):
                clear_report()
                grader_exec = compile(ics_contents, ics_filename, 'exec')
                exec(grader_exec, global_data)
    actual_output = captured_output.getvalue()
    return {"output": actual_output, "data": global_data, "report": MAIN_REPORT}


class Result:
    def __init__(self):
        self.results = []

    def add_case(self, submission_file_name, contents, result):
        self.results.append((submission_file_name, contents, result))
        if format == FORMAT_OPTIONS.FEEDBACK:
            print(result['filename'])
            print(indent(result['report'].result.for_console(), " " * 4))
        elif format == FORMAT_OPTIONS.GRADE:
            print(result['report'].result.score)
        elif format == FORMAT_OPTIONS.DEBUG:
            pass
        elif format == FORMAT_OPTIONS.STATS:
            assert "TODO: Aggregation of feedback into stats file is not yet supported"


class VerifyResults(Result):
    def __init__(self):
        super().__init__()

        class TestReferenceSolutions(unittest.TestCase):
            maxDiff = None

        self.TestReferenceSolutions = TestReferenceSolutions
        self.tests = []

    def add_case(self, submission_file_name, contents, result):
        with open(submission_file_name + ".txt", "r") as output_file:
            output_contents = output_file.read()

        if result and result[-1] == "\n":
            result = result[:-1]

        def new_test(self):
            self.assertEqual(result, output_contents)
        test_name = os.path.basename(submission_file_name)
        setattr(self.TestReferenceSolutions, "test_"+test_name, new_test)
        self.tests.append("test_"+test_name)
        # assert "TODO: Unit test style verification not yet supported"

    def run_cases(self):
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(self.TestReferenceSolutions)
        runner = unittest.TextTestRunner()
        runner.run(suite)


class FORMAT_OPTIONS:
    """
    The possible valid output options
    """
    FEEDBACK = 'feedback'
    GRADE = 'grade'
    DEBUG = 'debug'
    VERIFY = 'verify'
    STATS = 'stats'
    SANDBOX = 'sandbox'
    ALL_OPTIONS = [FEEDBACK, GRADE, DEBUG, VERIFY, STATS, SANDBOX]
    CONSTRUCTORS = {
        VERIFY: VerifyResults
    }


def main(args=None):
    """
    Actually runs Pedal from the command line.

    Args:
        args:

    Returns:

    """
    if args is None:
        args = parse_args()
    result = FORMAT_OPTIONS.CONSTRUCTORS[args.format]()
    if os.path.isfile(args.script):
        script_file_name, script_file_extension = os.path.splitext(args.script)
        if script_file_extension in ('.py',):
            submissions = normalize_path(args.submissions, args.script)
            if os.path.isfile(submissions):
                submission_paths = [submissions]
            else:
                submission_paths = [normalize_path(sub, submissions) for sub in os.listdir(submissions)]
            for submission_path in submission_paths:
                submission_file_name, submission_file_extension = os.path.splitext(submission_path)
                if submission_file_extension != ".py":
                    continue
                # TODO: add in student/course/assignment info
                with open(args.script, 'r') as scripts_file:
                    scripts_contents = scripts_file.read()
                with open(submission_path, 'r') as submission_file:
                    submission_contents = submission_file.read()
                print(submission_file_name)
                single_result = run_ics_on_submission(args.script, scripts_contents, args.args,
                                               "answer.py", submission_contents,
                                               args.format,
                                               {'filename': submission_path}, {}, {})
                single_result['filename'] = submission_path
                result.add_case(submission_file_name, submission_contents, single_result['output'])
            result.run_cases()
        elif script_file_extension in ('.db',):
            assert "TODO: ProgSnap DB files not yet supported"
        elif script_file_extension in ('.zip', ):
            assert "TODO: Zip files not yet supported"
    else:
        assert "TODO: Folders of grading scripts not yet supported"


def parse_args():
    parser = argparse.ArgumentParser(description='Run instructor control script on student submissions.')
    parser.add_argument('format', help='The format for the results',
                        choices=FORMAT_OPTIONS.ALL_OPTIONS)
    parser.add_argument('script', help='The path to the instructor control script, or multiple scripts.')
    parser.add_argument('submissions', help='The path to the student submissions. Defaults to a folder named '
                                            'submissions adjacent to the instructor control script.',
                        default='submissions')
    parser.add_argument('output', help='The output path for the result',
                        nargs='?', default=None)
    parser.add_argument('--args', '-a',
                        help='Pass in arguments that the grading script will use. '
                             'Variable substitutions include "$_STUDENT_MAIN".',
                        default='$_STUDENT_MAIN,$_STUDENT_NAME')
    parser.add_argument('--include_submissions', help='An optional REGEX filter to only include certain submissions')
    parser.add_argument('--exclude_submissions', help='An optional REGEX filter to remove certain submissions')
    parser.add_argument('--include_scripts', help='An optional REGEX filter to only include certain scripts')
    parser.add_argument('--exclude_scripts', help='An optional REGEX filter to remove certain scripts')
    parser.add_argument('--parallel_scripts', help="Which style to use for running scripts in parallel.",
                        choices=["threads", "processes", "none"])
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    main()

# If scripts is a single python file
# If scripts is a folder
# If scripts is a zip file
# If scripts is a ProgSnap SQL file
