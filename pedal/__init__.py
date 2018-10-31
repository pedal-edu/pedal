'''
A package for analyzing student code.
'''

# Probably want to import useful stuff from:
#   report
#   source
#   sandbox
#   tifa
#   cait
#   resolver
#   etc.

from pedal.cait.cait_api import parse_program, find_match, find_matches
from pedal.report.imperative import (suppress, explain, compliment,
                                     give_partial)
from pedal.sandbox.sandbox import run, reset