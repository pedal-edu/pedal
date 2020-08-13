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
    Just one parameter then
ProgSnap file with only submissions, ICS is separate
    Two parameters
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

Config settings
    seed
    create_missing_outputs
"""

import argparse
from pedal.command_line.modes import MODES


def main(args=None):
    """
    Actually runs Pedal from the command line.

    Args:
        args (argparse.Namespace): The arguments parsed from the command line.
    """
    # Get command line arguments, unless we were explicitly given them.
    if args is None:
        args = parse_args()
    pipeline = MODES.PIPELINES[args.mode]
    return pipeline(args).execute()


def parse_args(reduced_mode=False):
    """ Parse the arguments passed into the command line. """
    parser = argparse.ArgumentParser(description='Run instructor control '
                                                 'script on student submissions.')
    parser.add_argument('mode', help="What kind of Pedal analysis you're running",
                        choices=list(MODES.PIPELINES))
    if not reduced_mode:
        parser.add_argument('instructor', help='The path to the instructor control '
                                               'script, or multiple scripts.')
    parser.add_argument('submissions', help='The path to the student submissions.'
                                            ' Defaults to a folder named '
                                            'submissions adjacent to the '
                                            'instructor control script.',
                        default='submissions',
                        nargs='?')
    # TODO: Handle output to file
    parser.add_argument('--output', '-o',
                        help='The output path for the result. Defaults to stdout.',
                        default=None)
    parser.add_argument('--config', '-c',
                        help="Uses the configuration file to get settings.")
    parser.add_argument('--create_output',
                        help="In verify mode, creates any missing outputs.",
                        action='store_true')
    parser.add_argument('--environment', '-e',
                        help="Sets the environment context for this script, which"
                             " can run special setups and override tools as"
                             " needed.", default=None)
    parser.add_argument('--instructor_name',
                        help="Sets the name of the instructor file to something"
                             " more friendly. If not given, then will default"
                             " to the instructor filename.", default=None)
    '''
    parser.add_argument('--include_submissions', help='An optional REGEX filter '
                                                      'to only include certain submissions')
    parser.add_argument('--exclude_submissions', help='An optional REGEX filter '
                                                      'to remove certain submissions')
    parser.add_argument('--include_scripts', help='An optional REGEX filter to '
                                                  'only include certain scripts')
    parser.add_argument('--exclude_scripts', help='An optional REGEX filter to '
                                                  'remove certain scripts')
    parser.add_argument('--parallel_scripts', help="Which style to use for "
                                                   "running scripts in parallel.",
                        choices=["threads", "processes", "none"])
    '''
    args = parser.parse_args()
    if args.instructor_name is None:
        args.instructor_name = args.instructor
    return args


if __name__ == '__main__':
    main()

# If scripts is a single python file
# If scripts is a folder
# If scripts is a zip file
# If scripts is a ProgSnap SQL file
