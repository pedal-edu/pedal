import unittest

from pedal import contextualize_report
from pedal.cait.cait_api import *
from pedal.core.report import MAIN_REPORT
from pedal.source import set_source, verify
from pedal.tifa import tifa_analysis


class MistakeTest(unittest.TestCase):
    @staticmethod
    def to_source(source):
        """

        Args:
            source:
        """
        MAIN_REPORT.clear()
        contextualize_report(source)
        verify()
        parse_program()
        tifa_analysis()
