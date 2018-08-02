import unittest
import ast
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pedal.cait.stretchy_tree_matching import *
from pedal.cait.easy_node import *
from pedal.source import set_source
from pedal.tifa import tifa_analysis
from pedal.report import MAIN_REPORT, clear_report
from pedal.cait.cait_api import *


class AppendMistakeTest(unittest.TestCase):
    def setUp(self):
        MAIN_REPORT.clear()

