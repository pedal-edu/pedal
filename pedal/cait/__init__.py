"""
A package of tools for capturing student code by matching it against patterns.
"""

NAME = 'CAIT'
SHORT_DESCRIPTION = "Captures instructor code patterns within student code."
DESCRIPTION = '''
'''
REQUIRES = ['Source']
OPTIONALS = ['TIFA']

from pedal.cait.cait_api import (find_match, find_matches,
                                 parse_program,
                                 find_submatches, find_expr_sub_matches,
                                 def_use_error, data_state, data_type,
                                 expire_cait_cache)
