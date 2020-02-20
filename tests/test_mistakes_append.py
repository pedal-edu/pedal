import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.mistake_test_template import *
from CS1014.mistakes.instructor_append import *


class AppendMistakeTest(MistakeTest):
    def test_missing_append_in_iteration(self):
        self.to_source("for item in items:\n"
                       "    new_list.append(item)")
        self.assertFalse(missing_append_in_iteration(), "false positive")

        self.to_source("for item in items:\n"
                       "    if fun:\n"
                       "        new_list.append(item)")
        self.assertFalse(missing_append_in_iteration(), "false positive")

        self.to_source("for item in items:\n"
                       "    pass")
        self.assertTrue(missing_append_in_iteration(), "false negative")

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
        self.assertFalse(missing_append_in_iteration(), "false negative")

        self.to_source('depth = float(input("depth?"))\n')
        self.assertFalse(missing_append_in_iteration(), "false negative")

    def test_wrong_not_append_to_list(self):
        self.to_source("for item in items:\n"
                       "    new_list.append(item)")
        self.assertTrue(wrong_not_append_to_list(), "false negative")

        self.to_source("for item in items:\n"
                       "    if fun:\n"
                       "        new_list.append(item)")
        self.assertTrue(wrong_not_append_to_list(), "false negative")

        self.to_source("new_list = []\n"
                       "for item in items:\n"
                       "    new_list.append(item)")
        self.assertFalse(wrong_not_append_to_list(), "false positive")

        self.to_source("new_list = []\n"
                       "for item in items:\n"
                       "    if fun:\n"
                       "        new_list.append(item)")
        self.assertFalse(wrong_not_append_to_list(), "false positive")

    def test_missing_append_list_initialization(self):
        self.to_source("for item in items:\n"
                       "    target.append(item)")
        self.assertTrue(missing_append_list_initialization(), "false negative")

        self.to_source("for item in items:\n"
                       "    if fun:\n"
                       "        target.append(item)")
        self.assertTrue(missing_append_list_initialization(), "false negative")

        self.to_source("target = []\n"
                       "for item in items:\n"
                       "    target.append(item)")
        self.assertFalse(missing_append_list_initialization(), "false positive")

        self.to_source("target = []\n"
                       "for item in items:\n"
                       "    if fun:\n"
                       "        target.append(item)")
        self.assertFalse(missing_append_list_initialization(), "false positive")

    def test_wrong_append_list_initialization(self):
        self.to_source("new_list = 0\n"
                       "for item in items:\n"
                       "    new_list.append(item)")
        self.assertTrue(wrong_append_list_initialization(), "false negative")

        self.to_source("new_list = 0\n"
                       "for item in items:\n"
                       "    if fun:\n"
                       "        new_list.append(item)")
        self.assertTrue(wrong_append_list_initialization(), "false negative")

        self.to_source("new_list = []\n"
                       "for item in items:\n"
                       "    new_list.append(item)")
        self.assertFalse(wrong_append_list_initialization(), "false positive")

        self.to_source("new_list = []\n"
                       "for item in items:\n"
                       "    if fun:\n"
                       "        new_list.append(item)")
        self.assertFalse(wrong_append_list_initialization(), "false positive")

    def test_append_list_wrong_slot(self):
        self.to_source("new_list = []\n"
                       "for item in items:\n"
                       "    item.append(new_list)")
        self.assertTrue(append_list_wrong_slot(), "false negative")

        self.to_source("new_list = []\n"
                       "for item in items:\n"
                       "    if fun:\n"
                       "        item.append(new_list)")
        self.assertTrue(append_list_wrong_slot(), "false negative")

        self.to_source("new_list = []\n"
                       "for item in items:\n"
                       "    new_list.append(item)")
        self.assertFalse(append_list_wrong_slot(), "false positive")

        self.to_source("new_list = []\n"
                       "for item in items:\n"
                       "    if fun:\n"
                       "        new_list.append(item)")
        self.assertFalse(append_list_wrong_slot(), "false positive")
