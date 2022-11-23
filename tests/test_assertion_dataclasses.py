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
        self.assertFeedback(e, """Wrong Fields Type
The dataclass named Dog has a field named age that is a string, but should be an integer.""")

    def test_dataclasses_fails_runtime_close(self):
        with Execution("""
from dataclasses import dataclass

@dataclass
class Dog:
    name: str
    ag: int

x = Dog("Ada", 4)
print(x)""") as e:
            @dataclass
            class Dog:
                name: str
                age: int

            self.assertTrue(check_dataclass_instance(evaluate('x'), Dog))
            # self.assertFalse(assert_dataclass_fields())
        self.assertFeedback(e, """Unknown Field
The dataclass named Dog had a field named ag but that field is not supposed to be there. Are you sure you got the name right?""")

    def test_dataclasses_fails_runtime_error(self):
        with Execution("""
from dataclasses import dataclass

@dataclass
class Dog:
    name: str
    ag: int

x = Dog("Ada")
print(x)""") as e:
            @dataclass
            class Dog:
                name: str
                age: int

            self.assertTrue(check_dataclass_instance(evaluate('x'), Dog))
            # self.assertFalse(assert_dataclass_fields())
        self.assertFeedback(e, """Incorrect Arity
The constructor function Dog was given the wrong number of arguments. You should have had 2 arguments, but instead you had 1 arguments.""")

if __name__ == '__main__':
    unittest.main(buffer=False)
