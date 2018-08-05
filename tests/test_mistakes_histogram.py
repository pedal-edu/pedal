import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.mistake_test_template import *
from pedal.mistakes.instructor_histogram import *


class HistogramMistakeTests(MistakeTest):
    def test_histogram_argument_not_list(self):
        self.to_source("items = [1, 2, 3]\n"
                       "plt.hist(items)")
        self.assertFalse(histogram_argument_not_list(), "false positive")

        self.to_source("items = 0\n"
                       "plt.hist(items)")
        self.assertTrue(histogram_argument_not_list(), "false negative")

    def test_histogram_wrong_list(self):
        self.to_source("for item in items:\n"
                       "    target.append(item)\n"
                       "plt.hist(target)")
        self.assertFalse(histogram_wrong_list(), "false positive")

        self.to_source("for item in items:\n"
                       "    target.append(item)\n"
                       "plt.hist(item)")
        self.assertTrue(histogram_wrong_list(), "false negative")