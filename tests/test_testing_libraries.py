"""
Tests related to using alternative testing libraries
"""

import unittest

from pedal import unit_test, block_function, set_source, clear_report
from pedal.assertions.static import *
from pedal.assertions.commands import *
from pedal.assertions.runtime import *
from pedal.resolvers import simple
from pedal.types.new_types import DictType, LiteralStr, StrType
from tests.execution_helper import Execution, ExecutionTestCase, SUCCESS_MESSAGE


STUDENT_TEST_CODE_DIVIDE = """
import unittest

def divide(a, b):
    return a / b

class TestDivide(unittest.TestCase):
    def test_divide_success(self):
        self.assertEqual(divide(1, 1), 1)
    def test_divide_error(self):
        self.assertEqual(divide(1, 0), 0)
    def test_divide_failure(self):
        self.assertEqual(divide(1, 2), 2)
"""

class TestUnittest(ExecutionTestCase):
    def test_unittest_library(self):
        clear_report()
        set_source(STUDENT_TEST_CODE_DIVIDE)
        run()
        ensure_unittest_tests()
        final = simple.resolve()
        self.assertEqual("""2/3 of your unit tests are not passing.""", final.message.rstrip())

    def test_unittest_library_explicit(self):
        clear_report()
        set_source(STUDENT_TEST_CODE_DIVIDE+'\nunittest.main(exit=False)')
        run()
        ensure_unittest_tests()
        final = simple.resolve()
        self.assertEqual("""2/3 of your unit tests are not passing.""", final.message.rstrip())

if __name__ == '__main__':
    unittest.main(buffer=False)
