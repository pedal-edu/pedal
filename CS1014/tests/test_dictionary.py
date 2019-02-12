import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tests.mistake_test_template import *
from CS1014.dictionaries import *


class DictionaryMistakeTest(MistakeTest):
    def test_print_str_key(self):
        key = "Price"
        std_1 = "print('{}')".format(key)
        std_2 = "print(['{}'])".format(key)

        self.to_source(std_1)
        str_ret = print_str_key(keys=["Price", "Title"])
        self.assertTrue(str_ret == "Printing key {} instead of key-value"
                                   "<br><br><i>(print_dict_str)<i></br>".format(key))

        self.to_source(std_2)
        str_ret = print_str_key(keys=["Price", "Title"])
        self.assertTrue(str_ret == "Printing key {} instead of key-value"
                                   "<br><br><i>(print_dict_str)<i></br>".format(key))
