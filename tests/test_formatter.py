import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pedal.core.commands import *
from pedal.tifa import tifa_analysis
from pedal.core.formatting import Formatter
from pedal import MAIN_REPORT, Submission, run
from pedal.resolvers import simple


class TestCode(unittest.TestCase):

    def test_custom_formatter(self):
        clear_report()

        class CustomFormatter(Formatter):
            def name(self, value):
                return f"<code>{value}</code>"
            def line(self, line_number):
                return f"<a href=''>{line_number}</a>"

        contextualize_report(Submission(main_code="alpha=0"))
        set_formatter(CustomFormatter)
        tifa_analysis()

        if get_all_feedback():
            print(get_all_feedback()[0].message)

        final = simple.resolve()
        self.assertEqual(final.message,
                         "The variable <code>alpha</code> was given a value on line <a href=''>1</a>, but was never used after that.")


if __name__ == '__main__':
    unittest.main(buffer=False)
