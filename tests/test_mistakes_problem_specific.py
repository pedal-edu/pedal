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

    def test_missing_target_slot_empty_8_4(self):
        self.to_source("for ___ in pages_count_list:\n"
                       "    pass")
        self.assertTrue(missing_target_slot_empty_8_4(), "false negative")

        self.to_source("for item in pages_count_list:\n"
                       "    pass")
        self.assertFalse(missing_target_slot_empty_8_4(), "false positive")

    def test_missing_addition_slot_empty_8_4(self):
        self.to_source("sum_pages + ___")
        self.assertTrue(missing_addition_slot_empty_8_4(), "false negative")

        self.to_source("sum_pages + fun")
        self.assertFalse(missing_addition_slot_empty_8_4(), "False positive with name")

        self.to_source("sum_pages + 0")
        self.assertFalse(missing_addition_slot_empty_8_4(), "False positive with num")

    def test_wrong_names_not_agree_8_4(self):
        self.to_source("for item1 in pages_count_list:\n"
                       "    sum_pages = item2 + sum_pages")
        self.assertTrue(wrong_names_not_agree_8_4(), "false negative")

        self.to_source("for item1 in pages_count_list:\n"
                       "    sum_pages = sum_pages + item2")
        self.assertTrue(wrong_names_not_agree_8_4(), "false negative")

        self.to_source("for item1 in pages_count_list:\n"
                       "    sum_pages = item1 + sum_pages")
        self.assertFalse(wrong_names_not_agree_8_4(), "false positive")

        self.to_source("for item1 in pages_count_list:\n"
                       "    sum_pages = sum_pages + item1")
        self.assertFalse(wrong_names_not_agree_8_4(), "false positive")

    def test_wrong_modifying_list_8_5(self):
        self.to_source("i_list = [20473, 27630, 17849, 19032, 16378]")
        self.assertFalse(wrong_modifying_list_8_5(), "false positive")

        self.to_source("i_list = [20473, 27630, 17849, 19032, 0]")
        self.assertTrue(wrong_modifying_list_8_5(), "false negative")

    def test_wrong_modifying_list_8_6(self):
        self.to_source("i_list = [2.9, 1.5, 2.3, 6.1]")
        self.assertFalse(wrong_modifying_list_8_6(), "false positive")

        self.to_source("i_list = [2.9, 1.5, 2.3, 0]")
        self.assertTrue(wrong_modifying_list_8_6(), "false negative")

    def test_wrong_should_be_counting(self):
        self.to_source("for item in items:\n"
                       "    accu = accu + item")
        self.assertTrue(wrong_should_be_counting(), "false negative")

        self.to_source("for item in items:\n"
                       "    accu = accu + 1")
        self.assertFalse(wrong_should_be_counting(), "false positive")

    def test_wrong_should_be_summing(self):
        self.to_source("for item in items:\n"
                       "    accu = accu + item")
        self.assertFalse(wrong_should_be_summing(), "false positive")

        self.to_source("for item in items:\n"
                       "    accu = accu + 1")
        self.assertTrue(wrong_should_be_summing(), "false negative")

    def test_missing_addition_slot_empty(self):
        self.to_source("dum + ___")
        self.assertTrue(missing_addition_slot_empty(), "false negative")

        self.to_source("dum + fun")
        self.assertFalse(missing_addition_slot_empty(), "False positive with name")

        self.to_source("dum + 0")
        self.assertFalse(missing_addition_slot_empty(), "False positive with num")

    def test_wrong_cannot_sum_list(self):
        self.to_source("for item in items:\n"
                       "    i_sum = i_sum + items")
        self.assertTrue(wrong_cannot_sum_list(), "false negative")

        self.to_source("for item in items:\n"
                       "    i_sum = i_sum + item")
        self.assertFalse(wrong_cannot_sum_list(), "false positive")

    def test_missing_no_print(self):
        self.to_source("print(12)")
        self.assertFalse(missing_no_print(), "false positive")

        self.to_source("fun = 10 + 11")
        self.assertTrue(missing_no_print(), "false negative")

    def test_missing_counting_list(self):
        self.to_source("for item in items:\n"
                       "    item_sum = item_sum + 1")
        self.assertFalse(missing_counting_list(), "false positive")

        self.to_source("for item in items:\n"
                       "    item_sum = item_sum + item")
        self.assertTrue(missing_counting_list(), "false negative")

        self.to_source("for item in items:\n"
                       "    items.append(1)")
        self.assertTrue(missing_counting_list(), "false negative")

    def test_missing_summing_list(self):
        self.to_source("for item in items:\n"
                       "    item_sum = item_sum + 1")
        self.assertTrue(missing_summing_list(), "false negative")

        self.to_source("for item in items:\n"
                       "    item_sum = item_sum + item")
        self.assertFalse(missing_summing_list(), "false positive")

        self.to_source("for item in items:\n"
                       "    items.append(1)")
        self.assertTrue(missing_summing_list(), "false negative")

    def test_missing_zero_initialization(self):
        self.to_source("it_sum = 0\n"
                       "for item in items:\n"
                       "    it_sum = it_sum + 1")
        self.assertFalse(missing_zero_initialization(), "false positive")

        self.to_source("it_sum = 0\n"
                       "it_sum = it_sum + 1")
        self.assertFalse(missing_zero_initialization(), "false positive")

        self.to_source("for item in items:\n"
                       "    it_sum = it_sum + 1")
        self.assertTrue(missing_zero_initialization(), "false negative")

        self.to_source("for item in items:\n"
                       "    it_sum = it_sum + 1\n"
                       "it_sum = 0\n")
        self.assertTrue(missing_zero_initialization(), "false negative")

    def test_wrong_printing_list(self):
        self.to_source("for item in items:\n"
                       "    print(item)")
        self.assertTrue(wrong_printing_list(), "false negative")

        self.to_source("for item in items:\n"
                       "new_item_list.append(item)")
        self.assertFalse(wrong_printing_list(), "false positive")

    def test_missing_average(self):
        self.to_source("for item in items:\n"
                       "    total = total + item\n"
                       "    count = count + 1\n"
                       "average = total/count")
        self.assertFalse(missing_average(), "false positive")

        self.to_source("for item in items:\n"
                       "    total = total + item\n"
                       "    count = count + 1\n"
                       "average = total/total")
        self.assertTrue(missing_average(), "false negative")

    def test_warning_average_in_iteration(self):
        self.to_source("for item in items:\n"
                       "    total = total + item\n"
                       "    count = count + 1\n"
                       "average = total/count")
        self.assertFalse(warning_average_in_iteration(), "false positive")

        self.to_source("for item in items:\n"
                       "    total = total + item\n"
                       "    count = count + 1\n"
                       "    average = total/count\n")
        self.assertTrue(warning_average_in_iteration(), "false negative")

    def test_wrong_average_denominator(self):
        self.to_source("for item in items:\n"
                       "    total = total + item\n"
                       "    count = count + 1\n"
                       "average = total/count")
        self.assertFalse(wrong_average_denominator(), "false positive")

        self.to_source("for item in items:\n"
                       "    total = total + item\n"
                       "    count = count + 1\n"
                       "average = total/total\n")
        self.assertTrue(wrong_average_denominator(), "false negative")

    def test_wrong_average_numerator(self):
        self.to_source("for item in items:\n"
                       "    total = total + item\n"
                       "    count = count + 1\n"
                       "average = total/count")
        self.assertFalse(wrong_average_numerator(), "false positive")

        self.to_source("for item in items:\n"
                       "    total = total + item\n"
                       "    count = count + 1\n"
                       "average = count/count\n")
        self.assertTrue(wrong_average_numerator(), "false negative")

    def test_wrong_compare_list(self):
        self.to_source("for item in items:\n"
                       "    if item < 2:\n"
                       "        print(item)")
        self.assertFalse(wrong_compare_list(), "false positive")

        self.to_source("for item in items:\n"
                       "    if items < 2:\n"
                       "        print(item)")
        self.assertTrue(wrong_compare_list(), "false negative")

    def test_wrong_for_inside_if(self):
        self.to_source("for item in items:\n"
                       "    if item < 2:\n"
                       "        print(item)")
        self.assertFalse(wrong_for_inside_if(), "false positive")

        self.to_source("if items < 2:\n"
                       "    for item in items:\n"
                       "        print(item)")
        self.assertTrue(wrong_for_inside_if(), "false negative")

    def test_wrong_list_initialization_9_1(self):
        self.to_source('rainfall_list = weather.get("Precipitation","Location","Blacksburg, VA")')
        self.assertFalse(wrong_list_initialization_9_1(), "false positive")

        self.to_source('rainfall_list = weather.get("Precipitation","Location","Blacksburg, PA")')
        self.assertTrue(wrong_list_initialization_9_1(), "false negative")

    def test_wrong_accumulator_initialization_9_1(self):
        self.to_source("rainfall_sum = 0")
        self.assertFalse(wrong_accumulator_initialization_9_1(), "false positive")

        self.to_source('rainfall_list = weather.get("Precipitation","Location","Blacksburg, PA")')
        self.assertTrue(wrong_accumulator_initialization_9_1(), "false negative")

    def test_wrong_accumulation_9_1(self):
        self.to_source("rainfall_sum = _item_ + rainfall")
        self.assertTrue(wrong_accumulation_9_1(), "false negative")

        self.to_source("rainfall_sum = rainfall_sum + rainfall")
        self.assertFalse(wrong_accumulation_9_1(), "false positive")

    def test_wrong_list_initialization_placement_9_1(self):
        self.to_source("rainfall_sum = 0\n"
                       "rainfall_list = [1, 2, 3]\n"
                       "for rainfall in rainfall_list:\n"
                       "    pass\n")
        self.assertFalse(wrong_list_initialization_placement_9_1(), "false positive")

        self.to_source("rainfall_sum = 0\n"
                       "for rainfall in rainfall_list:\n"
                       "    pass\n"
                       "rainfall_list = [1, 2, 3]\n")
        self.assertTrue(wrong_list_initialization_placement_9_1(), "false negative")

        self.to_source("rainfall_sum = 0\n"
                       "for rainfall in rainfall_list:\n"
                       "    rainfall_list = [1, 2, 3]\n")
        self.assertTrue(wrong_list_initialization_placement_9_1(), "false negative")

    def test_wrong_print_9_1(self):
        self.to_source("for item in items:\n"
                       "    rainfall_sum = 0")
        self.assertFalse(wrong_iteration_body_9_1(), "false positive")

        self.to_source("for item in items:\n"
                       "    pass")
        self.assertFalse(wrong_iteration_body_9_1(), "false negative")


