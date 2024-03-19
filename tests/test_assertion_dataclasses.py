"""
Tests related to checking function definitions
"""

import unittest
from dataclasses import dataclass
from textwrap import dedent

from pedal import unit_test, block_function
from pedal.assertions.static import *
from pedal.assertions.commands import *
from pedal.assertions.runtime import *
from pedal.types.new_types import DictType, LiteralStr, StrType
from pedal.utilities.system import IS_AT_LEAST_PYTHON_38
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

    @unittest.skipIf(not IS_AT_LEAST_PYTHON_38, "Cannot subscript literals in Python 3.7")
    def test_weird_forecast_issue(self):
        @dataclass
        class WeatherOptions:
            raining: bool
            cloudy: bool
            snowing: bool

        @dataclass
        class Measurement:
            amount: int
            automatic: bool

        @dataclass
        class Report:
            temperature: int
            rainfall: list[Measurement]
            weather: WeatherOptions

        @dataclass
        class Forecast:
            when: str
            where: str
            reports: list[Report]

        CLASSES = [Forecast, Report, Measurement, WeatherOptions]
        NAMES = ["Forecast", "Report", "Measurement", "WeatherOptions"]
        main_program = dedent("""from dataclasses import dataclass
from bakery import assert_equal

@dataclass
class Measurement:
    amount: int
    automatic: bool

@dataclass
class WeatherOptions:
    raining:bool
    cloudy: bool
    snowing: bool

@dataclass
class Report:
    temperature: int
    rainfall: list[Measurement]
    weather: WeatherOptions

@dataclass
class Forecast:
    when: str
    where: str
    reports: list[Report]

def total_rainfall(forecasts: list[Forecast]) -> int:
    total = 0
    for forecast in forecasts:
        for report in forecast.reports:
            for rain in report.rainfall:
                total = total + rain.amount
    return total



List1 = [
    Forecast("Tuesday", "Dover", [
        Report(20,
               [Measurement(30, True)], 
               WeatherOptions(True, True, False))
    ])
]
List2 = [
    Forecast("Wednesday", "Newark", [
        Report(30,
               [Measurement(40, True), Measurement(25, True)],
               WeatherOptions(True, True, False))
    ])
]
assert_equal(total_rainfall(List1), 30)
assert_equal(total_rainfall(List2), 65)""")
        with Execution(main_program):
            for name, dc in zip(NAMES, CLASSES):
                self.assertFalse(ensure_dataclass(dc, priority='instructor'))
                self.assertFalse(assert_is_instance(evaluate(name), type))
                #
            # self.assertFalse(assert_dataclass_fields())
        #self.assertFeedback(e, """Incorrect Arity
        #The constructor function Dog was given the wrong number of arguments. You should have had 2 arguments, but instead you had 1 arguments.""")

if __name__ == '__main__':
    unittest.main(buffer=False)
