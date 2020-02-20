import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.mistake_test_template import *
from CS1014.mistakes.instructor_histogram import *


class HistogramMistakeTests(MistakeTest):
    def test_histogram_argument_not_list(self):
        self.to_source("items = [1, 2, 3]\n"
                       "plt.hist(items)")
        self.assertFalse(histogram_argument_not_list(), "false positive")

        self.to_source("items = 0\n"
                       "plt.hist(items)")
        self.assertTrue(histogram_argument_not_list(), "false negative")

        self.to_source('import classics\n'
                       'report_list = classics.get_books(test=True)\n'
                       'for report in report_list:\n'
                       '    hist = report["bibliography"]["type"]\n'
                       '    if hist == "Text":\n'
                       '        list.append("Text")\n'
                       'plt.hist(list)\n'
                       'plt.x("test")\n'
                       'plt.y("test")\n'
                       'plt.title(list)\n')
        ret = histogram_argument_not_list()
        self.assertTrue(ret, "Didn't give message returned {} instead".format(ret))

    def test_histogram_wrong_list(self):
        self.to_source("for item in items:\n"
                       "    target.append(item)\n"
                       "plt.hist(target)")
        self.assertFalse(histogram_wrong_list(), "false positive")

        self.to_source("for item in items:\n"
                       "    if fun:\n"
                       "        target.append(item)\n"
                       "plt.hist(target)")
        self.assertFalse(histogram_wrong_list(), "false positive")

        self.to_source("for item in items:\n"
                       "    target.append(item)\n"
                       "plt.hist(item)")
        self.assertTrue(histogram_wrong_list(), "false negative")

        self.to_source("for item in items:\n"
                       "    if fun:\n"
                       "        target.append(item)\n"
                       "plt.hist(item)")
        self.assertTrue(histogram_wrong_list(), "false negative")

        self.to_source('depth = float(input("depth?"))\n'
                       'deep_quake = []\n'
                       'for quake in quake_list:\n'
                       '    quake = quake * 0.62\n'
                       '    if quake > depth:\n'
                       '        deep_quake.append(quake)\n'
                       'plt.hist(deep_quake)\n'
                       'plt.title("title")\n'
                       'plt.xlabel("title")\n'
                       'plt.ylabel("title")\n'
                       'plt.show()\n')
        self.assertFalse(histogram_wrong_list(), "false positive")
