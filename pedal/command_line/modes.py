"""
Simple enumeration of the Modes available for Pedal's command line.
"""
import json
import os
import sys
import traceback
from contextlib import redirect_stdout
from io import StringIO
import unittest
from textwrap import indent
from unittest.mock import patch
from pprint import pprint
import warnings
import argparse

from pedal.command_line.verify import generate_report_out, ReportVerifier
from pedal.core.report import MAIN_REPORT
from pedal.core.submission import Submission
from pedal.sandbox.result import is_sandbox_result
from pedal.utilities.files import normalize_path
from pedal.utilities.progsnap import SqlProgSnap2
from pedal.utilities.text import chomp

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(values):
        """ Trivial helper function to replace TQDM's behavior """
        yield from values


# Disable all warnings from student files
# TODO: Move this strictly into ICS and Submission execution
warnings.filterwarnings("ignore")


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
    def __init__(self, data, output, error, resolution):
        self.data = data
        self.output = output
        self.error = error
        self.resolution = resolution

    def to_json(self):
        return dict(
            output=self.output,
            error=self.error,
            resolution= self.resolution.copy()
        )


class Bundle:
    def __init__(self, config, script, submission):
        self.config = config
        self.script = script
        self.submission = submission
        self.environment = None
        self.result = None

    def to_json(self):
        return dict(
            script=self.script,
            submission=self.submission.to_json(),
            environment=self.environment,
            result=self.result.to_json()
        )

    def run_ics_bundle(self, resolver='resolve', skip_tifa=False, skip_run=False):
        """
        Runs the given instructor control script on the given submission, with the
        accompany contextualizations.
        """
        ics_args = [self.submission, self.environment]
        captured_output = StringIO()
        global_data = {}
        error = None
        resolution = None
        if self.environment:
            env = __import__('pedal.environments.' + self.environment,
                             fromlist=[''])
            global_data.update(env.setup_environment(self.submission,
                                                     skip_tifa=skip_tifa,
                                                     skip_run=skip_run).fields)
        else:
            MAIN_REPORT.contextualize(self.submission)
        with redirect_stdout(captured_output):
            with patch.object(sys, 'argv', ics_args):
                try:
                    grader_exec = compile(self.script,
                                          self.submission.instructor_file, 'exec')
                    exec(grader_exec, global_data)
                    if 'MAIN_REPORT' in global_data:
                        if not global_data['MAIN_REPORT'].resolves:
                            if resolver in global_data:
                                resolution = global_data[resolver]()
                            # TODO: Need more elegance/configurability here
                            elif self.config.resolver == 'resolve':
                                exec("from pedal.resolvers.simple import resolve", global_data)
                                resolution = global_data["resolve"]()
                        else:
                            resolution = global_data['MAIN_REPORT'].resolves[-1]
                except Exception as e:
                    error = e
        actual_output = captured_output.getvalue()
        self.result = BundleResult(global_data, actual_output, error, resolution)


class AbstractPipeline:
    """ Generic pipeline for handling all the phases of executing instructor
    control scripts on submissions, and reformating the output. """

    def __init__(self, config):
        if isinstance(config, dict):
            # TODO: Include default argument automatically
            config = argparse.Namespace(**config)
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
                    self.submissions.append(Bundle(self.config, scripts_contents, new_submission))
        # Otherwise, if the submission is a single file:
        # Maybe it's a Progsnap DB file?
        elif given_submissions.endswith('.db'):
            for script, scripts_contents in all_scripts:
                self.load_progsnap(given_submissions, instructor_code=scripts_contents)
        # Otherwise, must just be a single python file.
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
                self.submissions.append(Bundle(self.config, scripts_contents, new_submission))

    progsnap_events_map = {
        'run': 'Run.Program',
        'edit': 'File.Edit',
        'last': 'File.Edit'
    }

    def load_progsnap(self, path, instructor_code=None):
        script_file_name, script_file_extension = os.path.splitext(path)
        if script_file_extension in ('.db',):
            with SqlProgSnap2(path, cache=self.config.cache) as progsnap:
                if self.config.progsnap_profile:
                    progsnap.set_profile(self.config.progsnap_profile)
                link_filters = {}
                include_scripts = self.config.include_scripts
                if include_scripts:
                    link_filters['Assignment'] = {}
                    if include_scripts.startswith('name='):
                        link_filters['Assignment']['X-Name'] = include_scripts[5:]
                    elif include_scripts.startswith('id='):
                        link_filters['Assignment']['AssignmentId'] = include_scripts[3:]
                    elif include_scripts.startswith('url='):
                        link_filters['Assignment']['X-URL'] = include_scripts[4:]
                    else:
                        link_filters['Assignment']['X-URL'] = include_scripts
                event_type = self.progsnap_events_map[self.config.progsnap_events]
                events = progsnap.get_events(event_filter={'EventType': event_type},
                                             link_filters=link_filters, limit=self.config.limit)
            if self.config.progsnap_events == 'last':
                events = [e for e in {
                    (event['student_email'], event['assignment_name']): event
                    for event in sorted(events, key=lambda e: e['event_id'])}.values()]
            for event in events:
                if instructor_code is None:
                    scripts_contents = event['on_run']
                new_submission = Submission(
                    main_file='answer.py', main_code=event['submission_code'].decode('utf-8'),
                    instructor_file='instructor.py',
                    execution=dict(client_timestamp=event['client_timestamp'],
                                   event_id=event['event_id']),
                    user=dict(email=event['student_email'],
                              first=event['student_first'],
                              last=event['student_last']),
                    assignment=dict(name=event['assignment_name'],
                                    url=event['assignment_url']),
                )
                self.submissions.append(Bundle(self.config, instructor_code, new_submission))
            # raise ValueError("TODO: ProgSnap DB files not yet supported")
            # Progsnap Zip
        elif script_file_extension in ('.zip',):
            raise ValueError("TODO: Zip files not yet supported")

    def load_submissions(self):
        given_script = self.config.instructor
        if self.config.ics_direct:
            # TODO: Allow non-progsnap ics_direct
            self.load_progsnap(self.config.submissions, instructor_code=given_script)
        elif is_progsnap(given_script):
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
            bundle.run_ics_bundle(resolver=self.config.resolver,
                                  skip_tifa=self.config.skip_tifa,
                                  skip_run=self.config.skip_run)

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
            elif bundle.result.resolution:
                # report = bundle.result.data['MAIN_REPORT']
                print(bundle.result.resolution.title)
                print(bundle.result.resolution.message)
            else:
                print("No feedback determined.")


class RunPipeline(AbstractPipeline):
    def process_output(self):
        for bundle in self.submissions:
            print(bundle.submission.instructor_file,
                  bundle.submission.main_file)
            if bundle.result.error:
                print(bundle.result.error)
            elif bundle.result.resolution:
                report = bundle.result.data['MAIN_REPORT']
                generate_report_out(None, self.config.environment, report)
            else:
                print("No feedback determined.")


class StatsPipeline(AbstractPipeline):
    def run_control_scripts(self):
        for bundle in tqdm(self.submissions):
            bundle.run_ics_bundle(resolver='stats_resolve', skip_tifa=self.config.skip_tifa,
                                  skip_run=self.config.skip_run)

    def process_output(self):
        total = 0
        errors = 0
        final = []
        for bundle in self.submissions:
            if bundle.result.error:
                print(bundle.result.error)
                errors += 1
            else:
                final.append(bundle.to_json())
            total += 1
        if self.config.output is not None:
            print(final)
            print("Total Processed:", total)
            print("Errors:", errors)
            pedal_json_encoder = PedalJSONEncoder()
            if self.config.output == 'stdout':
                print(pedal_json_encoder.encode(final))
            else:
                with open(self.config.output, 'w') as output_file:
                    print(pedal_json_encoder.encode(final), file=output_file)
        return final


class PedalJSONEncoder(json.JSONEncoder):
    """
    Custom JSON Encoder to handle weird Pedal values nested in Feedback Functions,
    including things like SandboxResult.
    """
    def _iterencode(self, o, markers=None):
        if is_sandbox_result(o):
            return super()._iterencode(o._actual_value, markers)
        else:
            return super()._iterencode(o, markers)

    def default(self, obj):
        return '<not serializable>'


class VerifyPipeline(AbstractPipeline):
    def process_output(self):
        for bundle in self.submissions:
            bundle.run_ics_bundle(resolver=self.config.resolver, skip_tifa=self.config.skip_tifa,
                                  skip_run=self.config.skip_run)
            if bundle.result.error:
                raise bundle.result.error
            # Now get the expected output
            base = os.path.splitext(bundle.submission.main_file)[0]
            test_name = os.path.basename(base)
            if os.path.exists(base + ".out"):
                verifier = ReportVerifier(base + ".out", self.config.environment)
                self.add_case(test_name, bundle.result, verifier)
            else:
                if self.config.create_output:
                    report = bundle.result.data['MAIN_REPORT']
                    generate_report_out(base + ".out", self.config.environment, report)
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
                # return f"{self.id().__name__} (Test{config.instructor})"

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
        if 'MAIN_REPORT' not in bundle_result.data:
            # TODO: Better error message here
            raise Exception("No MAIN_REPORT found; did you import Pedal?")
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
                entire_actual += field + ": " + actual_value + "\n"
                entire_expected += field + ": " + expected_value + "\n"
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
            self.fail(
                "Expected output file was not found next to the instructor file. Perhaps you meant to use --create_output?")

        setattr(self.TestReferenceSolutions, "test_" + name, new_test)
        self.tests.append("test_" + name)

    def run_cases(self):
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(self.TestReferenceSolutions)
        runner = unittest.TextTestRunner()
        runner.run(suite)


class GradePipeline(AbstractPipeline):
    def process_output(self):
        if self.config.output == 'stdout':
            self.print_bundles(sys.stdout)
        else:
            with open(self.config.output, 'w') as output_file:
                self.print_bundles(output_file)

    def print_bundles(self, target):
        for bundle in self.submissions:
            print(bundle.result.output, file=target)
            if bundle.result.error:
                raise bundle.result.error
            # This info is not sent to the output target, just to stdout
            print(bundle.submission.instructor_file,
                  bundle.submission.main_file,
                  bundle.result.data['MAIN_REPORT'].result.score *
                  bundle.result.data['MAIN_REPORT'].result.success,
                  sep=", ")


class SandboxPipeline(AbstractPipeline):
    """ Run the given script in a sandbox. """

    ICS = """from pedal import *
verify()
run()"""

    def load_submissions(self):
        # Use first argument as student submissions
        given_script = self.config.instructor
        # ... either a single file
        if os.path.isfile(given_script):
            scripts = [given_script]
        # ... or a directory of files
        else:
            scripts = os.listdir(given_script)
        # Then create submission to run
        for script in scripts:
            script_file_name, script_file_extension = os.path.splitext(script)
            if script_file_extension in ('.py',):
                load_error = None
                try:
                    with open(script, 'r') as scripts_file:
                        scripts_contents = scripts_file.read()
                except Exception as e:
                    load_error = e
                new_submission = Submission(
                    main_file="answer.py", main_code=scripts_contents,
                    instructor_file=script, load_error=load_error
                )
                self.submissions.append(Bundle(self.config, self.ICS, new_submission))

    def process_output(self):
        # Print output
        # Print runtime exceptions, if any
        for bundle in self.submissions:
            if bundle.result.error:
                traceback.print_tb(bundle.result.error.__traceback__)
                print(bundle.result.error)
                continue
            sandbox = bundle.result.data['MAIN_REPORT']['sandbox']['sandbox']
            output = [sandbox.raw_output]
            if sandbox.feedback:
                output.append(sandbox.feedback.message)
            print("\n".join(output))


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
                    print(indent(bundle.result.output, " " * 4))
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
    # Runs the instructor control script and outputs all feedback
    RUN = 'run'
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
        RUN: RunPipeline,
        FEEDBACK: FeedbackPipeline,
        GRADE: GradePipeline,
        STATS: StatsPipeline,
        SANDBOX: SandboxPipeline,
        VERIFY: VerifyPipeline,
        DEBUG: DebugPipeline
    }
