"""
A package for analyzing student code.
"""

# Probably want to import useful stuff from:
#   report
#   source
#   sandbox
#   tifa
#   cait
#   resolver
#   etc.

from pedal.cait import (find_match, find_matches,
                        parse_program,
                        find_submatches, find_expr_sub_matches,
                        def_use_error, data_state, data_type,
                        expire_cait_cache)
from pedal.report.imperative import (suppress, explain, compliment,
                                     give_partial, gently, set_success)
from pedal.sandbox.sandbox import run, reset
from pedal.tifa import tifa_analysis
from pedal.source import set_source, check_section_exists, next_section
