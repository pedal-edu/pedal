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
