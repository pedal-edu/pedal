"""

$> pedal debug unit_test_examples.py student_code.py --environment blockpy
"""

from pedal import *

assert_equal(call("add", 1, 2), 5)
assert_output(student, "Hello world")
ensure_literal("5")
