import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.mistake_test_template import *
from CS1014.mistakes.instructor_iteration import *
from pedal.core.report import MAIN_REPORT

class IterationMistakes(MistakeTest):
    def test_wrong_target_is_list(self):
        self.to_source("items = [1, 2, 3]\n"
                       "for item in items:\n"
                       "    pass")
        self.assertFalse(wrong_target_is_list(), "false positive")

        self.to_source("items = [1, 2, 3]\n"
                       "for items in item:\n"
                       "    pass\n"
                       "items = [1, 2, 3]")
        self.assertTrue(wrong_target_is_list(), "false negative (safe version)")

        # TODO: TIFA Discussion: items gets technically overwritten...
        self.to_source("items = [1, 2, 3]\n"
                       "for items in item:\n"
                       "    pass")
        self.assertTrue(wrong_target_is_list(), "false negative")

        self.to_source("credits = [1, 2, 3]\n"
                       "for credit in credits:\n"
                       "    print(credit)")
        self.assertFalse(wrong_target_is_list())

    def test_wrong_list_repeated_in_for(self):
        self.to_source("item = [1, 2, 3]\n"
                       "for item in item:\n"
                       "    pass\n"
                       "item = [1, 2, 3]")
        self.assertTrue(wrong_list_repeated_in_for(), "false negative (safe version)")

        # TODO: TIFA Discussion: item gets technically overwritten, but should it be list?
        self.to_source("item = [1, 2, 3]\n"
                       "for item in item:\n"
                       "    pass\n")
        self.assertTrue(wrong_list_repeated_in_for(), "false negative")

    def test_missing_iterator_initialization(self):
        self.to_source("items = 0\n"
                       "for item in items:\n"
                       "    pass")
        self.assertTrue(missing_iterator_initialization(), "false negative")

        self.to_source("for item in ___:\n"
                       "    pass")
        self.assertTrue(missing_iterator_initialization(), "false negative")

        self.to_source("items = [1, 2, 3]\n"
                       "for item in items:\n"
                       "    pass\n"
                       "items = [1, 2, 3]")
        self.assertFalse(missing_iterator_initialization(), "false positive")

    def test_wrong_iterator_not_list(self):
        self.to_source("items = 0\n"
                       "for item in items:\n"
                       "    pass")
        self.assertTrue(wrong_iterator_not_list(), "false negative")

        self.to_source("items = [1, 2, 3]\n"
                       "for item in items:\n"
                       "    pass\n"
                       "items = [1, 2, 3]")
        self.assertFalse(wrong_iterator_not_list(), "false positive")

    def test_missing_target_slot_empty(self):
        self.to_source("for ___ in items:\n"
                       "    pass")
        self.assertTrue(missing_target_slot_empty(), "False negative")

        self.to_source("for item in items:\n"
                       "    pass")
        self.assertFalse(missing_target_slot_empty(), "False positive")

    def test_list_not_initialized_on_run(self):
        self.to_source("for item in items:\n"
                       "    pass")
        self.assertTrue(list_not_initialized_on_run(), "false negative")

    def test_list_initialization_misplaced(self):
        self.to_source("items = [1, 2, 3]\n"
                       "for item in items:\n"
                       "    pass")
        self.assertFalse(list_initialization_misplaced(), "false positive")

        self.to_source("for item in items:\n"
                       "    pass\n"
                       "items = [1, 2, 3]")
        self.assertTrue(list_initialization_misplaced(), "false negative")

    def test_missing_for_slot_empty(self):
        self.to_source("for ___ in items:\n"
                       "    pass")
        self.assertTrue(missing_for_slot_empty(), "False negative")

        self.to_source("for item in ___:\n"
                       "    pass")
        self.assertTrue(missing_for_slot_empty(), "False negative")

        self.to_source("for item in items:\n"
                       "    pass")
        self.assertFalse(missing_for_slot_empty(), "False positive")

    def test_wrong_target_reassigned(self):
        self.to_source("for item in items:\n"
                       "    item = 12")
        self.assertTrue(wrong_target_reassigned(), "false negative")

        self.to_source("pages_count_list = [345, 414, 278, 510]\n"
                       "sum_pages = 0\n"
                       "for pages_count in pages_count_list:\n"
                       "    sum_pages = sum_pages + pages_count\n"
                       "print(sum_pages)\n")
        self.assertFalse(wrong_target_reassigned(), "false positive")

        self.to_source("for item in items:\n"
                       "    if stuff:\n"
                       "        item = 12")
        self.assertTrue(wrong_target_reassigned(), "false negative")

        self.to_source("for item in items:\n"
                       "    pass")
        self.assertFalse(wrong_target_reassigned(), "false positive")


if __name__ == '__main__':
    unittest.main(buffer=False)
