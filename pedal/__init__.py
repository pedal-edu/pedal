"""
A package for analyzing student code.
"""
import sys
import os

# Core Commands
from pedal.core.report import MAIN_REPORT
from pedal.core.submission import Submission
from pedal.core.commands import *
from pedal.source import *
from pedal.sandbox.commands import *
from pedal.cait import *
from pedal.assertions.commands import *

student: Sandbox

# Am I being run as Pedal, or via Python?
# Check if an environment was set via CLI
# Load in a submission file if it was given

# Did the user pass in our special flag or set an environment variable?
PEDAL_AS_LIBRARY_FLAG = '--PEDAL_AS_LIBRARY' in sys.argv
try:
    PEDAL_AS_LIBRARY_FLAG = os.environ['PEDAL_AS_LIBRARY']
except (AttributeError, KeyError):
    pass

def is_common_tool(command_line_context):
    return command_line_context.endswith('pydevconsole.py')

# If we get command line arguments and we're not told to be a library...
if sys.argv and not PEDAL_AS_LIBRARY_FLAG:
    # Only import if we HAVE sysargs
    from pedal.command_line.command_line import main, parse_args
    command_line_context = sys.argv[0]
    # Running this as a module
    if command_line_context == "-m":
        # Emulate the console_script mode
        pass
    # Running this via the console_script ``pedal``
    elif command_line_context.endswith('pedal'):
        # We get to do all the hijinx!
        pass
    # Otherwise, assume Python file that has the complete instructor grading script.
    elif is_common_tool(command_line_context):
        pass
    else:
        # We need to just use the parameters to set things up, don't run.
        # Need to setup environment, and make appropriate variables available.
        if len(sys.argv) > 1:
            args = parse_args(True)
            args.instructor = sys.argv[0]
            main(args)
