import unittest
from pedal.cait.cait_api import *
from pedal.report import MAIN_REPORT
from pedal.source import set_source


class MistakeTest(unittest.TestCase):
    @staticmethod
    def to_source(source):
        MAIN_REPORT.clear()
        set_source(source)
        parse_program()