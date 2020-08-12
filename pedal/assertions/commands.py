"""
Unifying collection of all the commands in ``pedal.assertions``.
"""
from pedal.sandbox.commands import call
from pedal.assertions.static import *
from pedal.assertions.runtime import *


def unit_test(function, *tests, **kwargs):
    with assert_group(function) as group_result:
        for test in tests:
            args, expected = test
            assert_equal(call(function, *args), expected)
    return not group_result
