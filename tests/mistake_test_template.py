import unittest
from pedal.cait.cait_api import *
from pedal.core import MAIN_REPORT
from pedal.source import set_source
from pedal.tifa import tifa_analysis


class MistakeTest(unittest.TestCase):
    @staticmethod
    def to_source(source):
        MAIN_REPORT.clear()
        set_source(source)
        parse_program()
        tifa_analysis()
