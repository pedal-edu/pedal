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
from pedal.mistakes.iteration_context import *


class SpecificMistakeTest(unittest.TestCase):
    @staticmethod
    def to_source(source):
        MAIN_REPORT.clear()
        set_source(source)
        parse_program()

    def test_wrong_list_length_8_2(self):
        self.to_source("fun = [1, 2, 3]")
        self.assertFalse(wrong_list_length_8_2(), "couldn't detect correct length list")
        self.to_source("fun = [1, 2]")
        self.assertTrue(wrong_list_length_8_2(), "couldn't detect incorrect length list")
        self.to_source("fun.append(0)")
        self.assertFalse(wrong_list_length_8_2(), "false match")

    def test_missing_list_initialization_8_2(self):
        self.to_source("fun = [1, 2]")
        self.assertTrue(missing_list_initialization_8_2(), "couldn't detect named list")
        self.to_source("shopping_cart = [1, 2, 3]")
        self.assertFalse(missing_list_initialization_8_2())
        self.to_source("fun.append(0)")
        self.assertTrue(missing_list_initialization_8_2(), "did not trigger on complete absence")

    def test_wrong_list_is_constant_8_2(self):
        self.to_source("fun = 2")
        self.assertFalse(wrong_list_is_constant_8_2(), "name incorrectly matched")

        self.to_source("shopping_cart = 2")
        self.assertTrue(wrong_list_is_constant_8_2(), "match and feedback not triggered")

        self.to_source("shopping_cart = [1, 2, 3]")
        self.assertFalse(wrong_list_is_constant_8_2(), "incorrectly matched")

    def test_list_all_zeros_8_2(self):
        self.to_source("my_list = [0, 0, 0]")
        self.assertTrue(list_all_zeros_8_2(), "didn't detect")

        self.to_source("my_list = [0, 0, 1]")
        self.assertFalse(list_all_zeros_8_2(), "False positive")

    def test_wrong_list_initialization_placement_8_3(self):
        self.to_source("length_sum = 0\n"
                       "episode_length_list = [1, 2, 3]\n"
                       "for episode in episode_length_list:\n"
                       "    length_sum = length_sum + episode\n")
        self.assertFalse(wrong_list_initialization_placement_8_3(), "incorrect trigger of feedback")

        self.to_source("length_sum = 0\n"
                       "for episode in episode_length_list:\n"
                       "    length_sum = length_sum + episode\n"
                       "episode_length_list = [1, 2, 3]\n")
        self.assertTrue(wrong_list_initialization_placement_8_3(), "incorrect trigger of feedback")

    def test_wrong_accumulator_initialization_placement_8_3(self):
        self.to_source("sum_length = 0\n"
                       "episode_length_list = [1, 2, 3]\n"
                       "for episode in episode_length_list:\n"
                       "    sum_length = sum_length + episode\n")
        self.assertFalse(wrong_accumulator_initialization_placement_8_3(), "incorrect trigger of feedback")

        self.to_source("episode_length_list = [1, 2, 3]\n"
                       "for episode in episode_length_list:\n"
                       "    sum_length = sum_length + episode\n"
                       "sum_length = 0\n")
        self.assertTrue(wrong_accumulator_initialization_placement_8_3(), "incorrect trigger of feedback")

    def test_wrong_iteration_body_8_3(self):
        self.to_source("sum_length = 0\n"
                       "episode_length_list = [1, 2, 3]\n"
                       "for episode in episode_length_list:\n"
                       "    sum_length = sum_length + episode\n")
        self.assertFalse(wrong_iteration_body_8_3(), "incorrect trigger of feedback")

        self.to_source("sum_length = 0\n"
                       "episode_length_list = [1, 2, 3]\n"
                       "sum_length = sum_length + episode\n"
                       "for episode in episode_length_list:\n")
        self.assertTrue(wrong_iteration_body_8_3(), "feedback didn't detect trigger")

    def test_wrong_print_8_3(self):
        self.to_source("items = [1, 2, 3]\n"
                       "total = 0\n"
                       "for item in items:\n"
                       "    total = total + item\n"
                       "print(total)\n")
        self.assertFalse(wrong_print_8_3(), "feedback false positive")

        self.to_source("items = [1, 2, 3]\n"
                       "total = 0\n"
                       "for item in items:\n"
                       "    total = total + item\n"
                       "    print(total)\n")
        self.assertTrue(wrong_print_8_3(), "feedback false negative when in body")

        self.to_source("items = [1, 2, 3]\n"
                       "total = 0\n"
                       "print(total)\n"
                       "for item in items:\n"
                       "    total = total + item\n")
        self.assertTrue(wrong_print_8_3(), "feedback false negative when before loop")
