"""
Useful booleans to determine what version of Python we are using.
"""

import sys

IS_PYTHON_36 = sys.version_info[:2] == (3, 6)
IS_PYTHON_37 = sys.version_info[:2] == (3, 7)
IS_PYTHON_38 = sys.version_info[:2] == (3, 8)
IS_AT_LEAST_PYTHON_38 = sys.version_info[:2] >= (3, 8)
IS_AT_LEAST_PYTHON_39 = sys.version_info[:2] >= (3, 9)
IS_AT_LEAST_PYTHON_310 = sys.version_info[:2] >= (3, 10)
IS_AT_LEAST_PYTHON_311 = sys.version_info[:2] >= (3, 11)
