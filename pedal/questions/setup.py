"""
Initialize and setup the Questions tool.
"""

from pedal.core.report import MAIN_REPORT, Report
from pedal.questions.constants import TOOL_NAME

import hashlib


def _name_hash(name: str) -> int:
    """ Turn a string name into a unique hashcode using MD5 """
    return hashlib.md5(name.encode('utf8')).digest()[0]


def reset(report=MAIN_REPORT):
    """
    Remove all settings for the Questions tool. Seed will be 0.

    Args:
        report: The report object

    Returns:
        This tool's data
    """
    report[TOOL_NAME] = {
        'seed': 0
    }
    return report[TOOL_NAME]


Report.register_tool(TOOL_NAME, reset)


def set_seed(seed_value, report=MAIN_REPORT):
    """
    Sets the seed that will be used in selecting questions.

    Args:
        seed_value (int or str or iterable[int]): The value to use when
            selecting questions, deterministically. If int, the same index
            will be used for all questions. If an iterable of ints, each
            one will serve as the index for the corresponding problem (throws
            an exception if the iterable isn't long enough). If a string,
            it will be hashed to a value (the hash is deterministic across
            platforms) that will be modulo'd to be in the right range for the
            pool. Presently, hashing generates values from [0, 256) so you
            need to limit your questions to 256.
        report (Report): The report object to store data and feedback in. If
            left None, defaults to the global MAIN_REPORT.
    """
    report['questions']['seed'] = seed_value
