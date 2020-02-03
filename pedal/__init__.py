"""
A package for analyzing student code.

TODO: Fix up all the tool's imports
TODO: Add documentation for each one
TODO: Rework MAIN_REPORT keyword arg for all tools
TODO: Set up command line
TODO: Rework Source module
TODO: Improve feedback tracking for all the tools
TODO: Fix up imports everywhere to be consistent, particularly for the modules themselves
"""

# Probably want to import useful stuff from:
#   report
#   source
#   sandbox
#   tifa
#   cait
#   resolver
#   etc.

# Core Commands
from pedal.core.commands import *
# Source
from pedal.source import (set_source, check_section_exists, next_section,
                          set_source_file)
# CAIT
from pedal.cait import (find_match, find_matches,
                        parse_program,
                        find_submatches, find_expr_sub_matches,
                        def_use_error, data_state, data_type,
                        expire_cait_cache)
# TIFA
from pedal.tifa import tifa_analysis
# Sandbox
from pedal.sandbox.sandbox import run, reset
