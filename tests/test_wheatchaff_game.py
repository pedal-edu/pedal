"""
Tests related to checking function definitions
"""

import unittest
from dataclasses import dataclass

from pedal import unit_test, block_function, set_source, clear_report
from pedal.assertions.static import *
from pedal.assertions.commands import *
from pedal.assertions.runtime import *
from pedal.resolvers import simple
from pedal.types.new_types import DictType, LiteralStr, StrType
from tests.execution_helper import Execution, ExecutionTestCase, SUCCESS_MESSAGE


def correct(a, b):
    if not b:
        return "0%"
    return str(100 * a // b) + "%"


def no_b_check(a, b):
    return str(100 * a // b) + "%"


def really_bad(a, b):
    return "0%"


class TestAssertionsWheatChaffGame(ExecutionTestCase):
    def test_wheatcaff_game_valid(self):
        clear_report()
        set_source("""
from bakery import assert_equal

assert_equal(divide(1, 1), "100%")
""")
        game = wheat_chaff_game('divide', {'correct': correct}, {})
        self.assertTrue(game)

    def test_wheatcaff_game_not_valid(self):
        clear_report()
        set_source("""
from bakery import assert_equal

assert_equal(divide(1, 1), "30%")
        """)
        game = wheat_chaff_game('divide', {'correct': correct}, {})
        self.assertFalse(game)

    def test_wheatcaff_game_thorough(self):
        clear_report()
        set_source("""
from bakery import assert_equal

assert_equal(divide(1, 0), "0%")
""")
        game = wheat_chaff_game('divide', {}, {'bad': no_b_check})
        self.assertTrue(game)

    def test_wheatcaff_game_not_thorough(self):
        clear_report()
        set_source("""
from bakery import assert_equal

assert_equal(divide(1, 1), "100%")
        """)
        game = wheat_chaff_game('divide', {}, {'bad': no_b_check})
        self.assertFalse(game)

    def test_wheatchaff_game_thorough_valid(self):
        clear_report()
        set_source("""
from bakery import assert_equal

assert_equal(divide(1, 1), "100%")
assert_equal(divide(1, 0), "0%")
        """)
        game = wheat_chaff_game('divide', {'correct': correct}, {'bad': no_b_check})
        self.assertTrue(game)

    def test_wheatchaff_game_not_thorough_not_valid(self):
        clear_report()
        set_source("""
from bakery import assert_equal

assert_equal(divide(1, 1), "0%")
        """)
        game = wheat_chaff_game('divide', {'correct': correct}, {'bad': really_bad})
        self.assertFalse(game)
        final = simple.resolve()
        self.assertEqual("""
I ran your test cases against some of my own implementations of divide.
I had 1 programs I expected to pass, and 1 programs I expected to fail.
Your tests did not pass 1 of my good programs.
Your tests did not catch 1 of my bad programs.

Here are the names for the good programs that incorrectly failed on your test cases:
    correct
Here are the names for the bad programs that incorrectly passed your tests:
    bad""", final.message.rstrip())

if __name__ == '__main__':
    unittest.main(buffer=False)
