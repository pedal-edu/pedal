"""
Simple enumeration of the Modes available for Pedal's command line.
"""
import os
import sys
from contextlib import redirect_stdout
from io import StringIO
import unittest
from textwrap import indent
from unittest.mock import patch
from pprint import pprint

from pedal.command_line.verify import generate_report_out, ReportVerifier
from pedal.core.report import MAIN_REPORT
from pedal.core.submission import Submission
from pedal.utilities.files import normalize_path
from pedal.utilities.text import chomp


def is_progsnap(path):
    """ Determines if this is a ProgSnap file or folder. """
    if os.path.isfile(path):
        name, extension = os.path.splitext(path)
        return extension in ('.zip', '.db')
    else:
        # Does it have all the necessary components?
        return os.path.isfile(os.path.join(path, 'MainTable.csv'))


def get_python_files(paths):
    result = {}
    for path in paths:
        name, ext = os.path.splitext(path)
        if ext != ".py":
            continue
        with open(path, 'r') as submission_file:
            contents = submission_file.read()
        result[path] = contents
    return result


class BundleResult:
    def __init__(self, data, output, error):
        self.data = data
        self.output = output
        self.error = error


class Bundle:
    def __init__(self, script, submission):
        self.script = script
        self.submission = submission
        self.environment = None
        self.result = None

    def run_ics_bundle(self):
        """
        Runs the given instructor control script on the given submission, with the
        accompany contextualizations.
        """
        ics_args = [self.submission, self.environment]
        captured_output = StringIO()
        global_data = {}
        error = None
        if self.environment:
            env = __import__('pedal.environments.'+self.environment,
                             fromlist=[''])
            global_data.update(env.setup_environment(self.submission).fields)
        else:
            MAIN_REPORT.contextualize(self.submission)
        with redirect_stdout(captured_output):
            with patch.object(sys, 'argv', ics_args):
                try:
                    grader_exec = compile(self.script,
                                          self.submission.instructor_file, 'exec')
                    exec(grader_exec, global_data)
                    if ('MAIN_REPORT' in global_data and
                            not global_data['MAIN_REPORT'].resolves and
                            'resolve' in global_data):
                        global_data['resolve']()
                except Exception as e:
                    error = e
        actual_output = captured_output.getvalue()
        self.result = BundleResult(global_data, actual_output, error)


class AbstractPipeline:
    """ Generic pipeline for handling all the phases of executing instructor
    control scripts on submissions, and reformating the output. """
    def __init__(self, config):
        self.config = config
        self.submissions = []
        self.result = None

    def execute(self):
        self.load_submissions()
        self.setup_execution()
        self.run_control_scripts()
        return self.process_output()

    def load_file_submissions(self, scripts):
        # Get instructor control scripts
        all_scripts = []
        for script in scripts:
            script_file_name, script_file_extension = os.path.splitext(script)
            # Single Python file
            if script_file_extension in ('.py',):
                with open(script, 'r') as scripts_file:
                    scripts_contents = scripts_file.read()
                all_scripts.append((script, scripts_contents))
        given_submissions = self.config.submissions
        # If submission is a directory, use it as a directory adjacent to each ics
        if os.path.isdir(given_submissions):
            for script, scripts_contents in all_scripts:
                directory_pattern = given_submissions
                submission_dir = normalize_path(directory_pattern, script)
                submission_files = [
                    os.path.join(submission_dir, sub)
                    for sub in os.listdir(submission_dir)
                ]
                subs = get_python_files(submission_files)
                for main_file, main_code in subs.items():
                    new_submission = Submission(
                        main_file=main_file, main_code=main_code,
                        instructor_file=script
                    )
                    self.submissions.append(Bundle(scripts_contents, new_submission))
        # Otherwise, if the submission is a single file:
        else:
            main_file = given_submissions
            load_error = None
            try:
                with open(given_submissions, 'r') as single_submission_file:
                    main_code = single_submission_file.read()
            except OSError as e:
                # Okay, file does not exist. Load error gets triggered.
                main_code = None
                load_error = e
            for script, scripts_contents in all_scripts:
                new_submission = Submission(
                    main_file=main_file, main_code=main_code,
                    instructor_file=script, load_error=load_error
                )
                self.submissions.append(Bundle(scripts_contents, new_submission))

    def load_progsnap(self, path):
        script_file_name, script_file_extension = os.path.splitext(path)
        if script_file_extension in ('.db',):
            assert "TODO: ProgSnap DB files not yet supported"
            # Progsnap Zip
        elif script_file_extension in ('.zip',):
            assert "TODO: Zip files not yet supported"

    def load_submissions(self):
        given_script = self.config.instructor
        if is_progsnap(given_script):
            self.load_progsnap(given_script)
        elif os.path.isfile(given_script):
            self.load_file_submissions([given_script])
        else:
            python_files = os.listdir(given_script)
            self.load_file_submissions(python_files)


    def setup_execution(self):
        for bundle in self.submissions:
            bundle.environment = self.config.environment

    def run_control_scripts(self):
        for bundle in self.submissions:
            bundle.run_ics_bundle()

    def process_output(self):
        for bundle in self.submissions:
            print(bundle.submission.instructor_file,
                  bundle.submission.main_file,
                  bool(bundle.result.error))


class FeedbackPipeline(AbstractPipeline):
    def process_output(self):
        for bundle in self.submissions:
            print(bundle.submission.instructor_file,
                  bundle.submission.main_file)
            if bundle.result.error:
                print(bundle.result.error)
            else:
                report = bundle.result.data['MAIN_REPORT']
                print(report.result.title)
                print(report.result.message)


class StatsPipeline(AbstractPipeline):
    pass


class VerifyPipeline(AbstractPipeline):
    def process_output(self):
        for bundle in self.submissions:
            bundle.run_ics_bundle()
            if bundle.result.error:
                raise bundle.result.error
            # Now get the expected output
            base = os.path.splitext(bundle.submission.main_file)[0]
            test_name = os.path.basename(base)
            if os.path.exists(base+".out"):
                verifier = ReportVerifier(base+".out", self.config.environment)
                self.add_case(test_name, bundle.result, verifier)
            else:
                if self.config.create_output:
                    report = bundle.result.data['MAIN_REPORT']
                    generate_report_out(base+".out", self.config.environment, report)
                    self.skip_case(test_name)
                else:
                    self.error_case(test_name, bundle.result)
        self.run_cases()

    def __init__(self, config):
        super().__init__(config)

        class TestReferenceSolutions(unittest.TestCase):
            __module__ = 'VerifyTestCase'
            __qualname__ = config.instructor_name
            maxDiff = None
            def __str__(self):
                return f"{config.instructor}, using {self._testMethodName[5:]}.py"
                #return f"{self.id().__name__} (Test{config.instructor})"
            def __repr__(self):
                return str(self)
        self.TestReferenceSolutions = TestReferenceSolutions
        self.tests = []

    def add_case(self, name, bundle_result, verifier):
        """ Add this ``name`` as a new test. """
        if bundle_result.output.strip():
            print(bundle_result.output)
        error = bundle_result.error if bundle_result.error else None
        if error:
            print(error)
        actual = bundle_result.data['MAIN_REPORT'].result.to_json()
        error = bundle_result.error
        expected_fields = verifier.get_final()
        def new_test(self):
            if error:
                raise error
            entire_actual, entire_expected = "", ""
            differing_fields = []
            for field, value in expected_fields:
                self.assertIn(field, actual, msg="Field was not in feedback.")
                actual_value = chomp(str(actual[field]).strip())
                expected_value = chomp(str(value))
                entire_actual += field+": "+actual_value+"\n"
                entire_expected += field+": "+expected_value+"\n"
                if expected_value != actual_value:
                    differing_fields.append(field)
            differing_fields = ', '.join(f"'{field}'" for field in differing_fields)
            self.assertEqual(entire_expected, entire_actual,
                             msg=f"Wrong value for {differing_fields} in {name}.")

        setattr(self.TestReferenceSolutions, "test_" + name, new_test)
        self.tests.append("test_" + name)

    def skip_case(self, name):
        def new_test(self):
            self.skipTest("Output did not exist; created.")
        setattr(self.TestReferenceSolutions, "test_" + name, new_test)
        self.tests.append("test_" + name)

    def error_case(self, name, bundle_result):
        def new_test(self):
            self.fail("Expected output file was not found next to the instructor file. Perhaps you meant to use --create_output?")
        setattr(self.TestReferenceSolutions, "test_" + name, new_test)
        self.tests.append("test_" + name)

    def run_cases(self):
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(self.TestReferenceSolutions)
        runner = unittest.TextTestRunner()
        runner.run(suite)


class GradePipeline(AbstractPipeline):
    def process_output(self):
        for bundle in self.submissions:
            for bundle in self.submissions:
                print(bundle.result.output)
                if bundle.result.error:
                    raise bundle.result.error
                print(bundle.submission.instructor_file,
                      bundle.submission.main_file,
                      bundle.result.data['MAIN_REPORT'].result.score*
                      bundle.result.data['MAIN_REPORT'].result.success,
                      sep=", ")


class SandboxPipeline(AbstractPipeline):
    """ Run the given script in a sandbox. """
    def load_submissions(self):
        self.control_scripts = [
            """
            
            """
        ]

    def process_output(self):
        # Print output
        # Print runtime exceptions, if any
        sandbox = self.result['report']['sandbox']
        output = [sandbox.raw_output]
        if sandbox.error:
            output.append(str(sandbox.error))
        return "\n".join(output)


class DebugPipeline(AbstractPipeline):
    def process_output(self):
        for bundle in self.submissions:
            for bundle in self.submissions:
                print(bundle.submission.instructor_file,
                      bundle.submission.main_file)
                if bundle.result.error:
                    print(bundle.result.error)
                else:
                    print("Output:")
                    print(indent(bundle.result.output, " "*4))
                    report = bundle.result.data['MAIN_REPORT']
                    print("Feedback:")
                    for feedback in report.feedback:
                        print("\t", feedback, repr(feedback.fields))
                    print("Final Feedback")
                    pprint(report.result.to_json())


class MODES:
    """
    The possible modes that Pedal can be run in.
    """
    # Get just the feedback for submissions
    FEEDBACK = 'feedback'
    # Get just the score/correctness
    GRADE = 'grade'
    # Check against expected output
    VERIFY = 'verify'
    # Output all the feedback objects
    STATS = 'stats'
    # Run the file as student code using the sandbox
    SANDBOX = 'sandbox'
    # Output as much information as possible
    DEBUG = 'debug'

    PIPELINES = {
        FEEDBACK: FeedbackPipeline,
        GRADE: GradePipeline,
        STATS: StatsPipeline,
        SANDBOX: SandboxPipeline,
        VERIFY: VerifyPipeline,
        DEBUG: DebugPipeline
    }
