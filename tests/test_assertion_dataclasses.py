"""
Tests related to checking function definitions
"""

import unittest
from dataclasses import dataclass

from pedal import unit_test, block_function
from pedal.assertions.static import *
from pedal.assertions.commands import *
from pedal.assertions.runtime import *
from pedal.types.new_types import DictType, LiteralStr, StrType
from tests.execution_helper import Execution, ExecutionTestCase, SUCCESS_MESSAGE


class TestAssertionsDataclasses(ExecutionTestCase):
    def test_dataclasses_passes_runtime(self):
        with Execution("""
from dataclasses import dataclass

@dataclass
class Dog:
    name: str
    age: int

x = Dog("Ada", 4)
print(x)""") as e:
            @dataclass
            class Dog:
                name: str
                age: int
            self.assertFalse(check_dataclass_instance(evaluate('x'), Dog))
            #self.assertFalse(assert_dataclass_fields())
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_dataclasses_fails_runtime(self):
        with Execution("""
from dataclasses import dataclass

@dataclass
class Dog:
    name: str
    age: int

x = Dog("Ada", 4)
print(x)
x.age = "Apple"
print(x)""") as e:
            @dataclass
            class Dog:
                name: str
                age: int
            self.assertTrue(check_dataclass_instance(evaluate('x'), Dog))
            #self.assertFalse(assert_dataclass_fields())
        self.assertFeedback(e, "ERROR")

if __name__ == '__main__':
    unittest.main(buffer=False)
