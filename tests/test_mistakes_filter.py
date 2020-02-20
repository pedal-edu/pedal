import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.mistake_test_template import *
from CS1014.mistakes.instructor_filter import *


class FilterMistakeTests(MistakeTest):
    def test_missing_if_in_for(self):
        self.to_source("for item in items:\n"
                       "    if item < 20:\n"
                       "        print(item)")
        self.assertFalse(missing_if_in_for(), "false positive")

        self.to_source("for item in items:\n"
                       "    print(item < 20):\n")
        self.assertTrue(missing_if_in_for(), "false negative")

    def test_append_not_in_if(self):
        self.to_source("if item < 20:\n"
                       "    _list.append(item)")
        self.assertFalse(append_not_in_if(), "false positive")

        self.to_source("if item < 20:\n"
                       "    print(item)")
        self.assertTrue(append_not_in_if(), "false negative")
