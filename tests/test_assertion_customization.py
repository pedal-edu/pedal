"""
Test cases for assertion customization functionality.
These tests verify that template interpolation and custom parameters work correctly.
"""
import unittest
from tests.execution_helper import Execution, ExecutionTestCase, SUCCESS_MESSAGE


class TestAssertionCustomization(ExecutionTestCase):

    def test_assert_equal_custom_assertion_template(self):
        """Test that assertion_message template interpolation works"""
        with Execution('5') as e:
            from pedal.assertions.runtime import assert_equal
            assert_equal(1, 2, assertion_message="{left} was not {right}")
        self.assertFeedback(e, """Failed Instructor Test
Student code failed instructor test.
1 was not 2
""")

    def test_assert_equal_custom_assertion_parameter_name(self):
        """Test that 'assertion' parameter also works"""
        with Execution('5') as e:
            from pedal.assertions.runtime import assert_equal
            assert_equal(1, 2, assertion="Expected {left} but got {right}")
        self.assertFeedback(e, """Failed Instructor Test
Student code failed instructor test.
Expected 1 but got 2
""")

    def test_assert_equal_custom_explanation_template(self):
        """Test that explanation template interpolation works"""
        with Execution('5') as e:
            from pedal.assertions.runtime import assert_equal
            assert_equal(1, 2, explanation="The values {left} and {right} should be equal")
        self.assertFeedback(e, """Failed Instructor Test
Student code failed instructor test.
    1 != 2The values 1 and 2 should be equal""")

    def test_assert_equal_complex_types_template(self):
        """Test template interpolation with complex data types"""
        with Execution('5') as e:
            from pedal.assertions.runtime import assert_equal
            assert_equal([1, 2, 3], {'a': 1}, assertion_message="List {left} is not dict {right}")
        self.assertFeedback(e, """Failed Instructor Test
Student code failed instructor test.
List [1, 2, 3] is not dict {'a': 1}
""")

    def test_assert_equal_custom_expected_verb(self):
        """Test that custom expected_verb parameter works (requires sandbox context)"""
        with Execution('def add(a, b): return a-b', run_tifa=False) as e:
            from pedal.assertions.runtime import assert_equal
            assert_equal(e.student.call('add', 1, 2), 3, expected_verb="to equal exactly")
        self.assertIn("to equal exactly", e.final.message)

    def test_assert_length_equal_template_interpolation(self):
        """Test template interpolation works for different assertion types"""
        with Execution('5') as e:
            from pedal.assertions.runtime import assert_length_equal
            assert_length_equal([1, 2], 5, assertion_message="Length of {left} should be {right}")
        self.assertFeedback(e, """Failed Instructor Test
Student code failed instructor test.
Length of [1, 2] should be 5
""")

    def test_assert_in_template_interpolation(self):
        """Test template interpolation with assert_in"""
        with Execution('5') as e:
            from pedal.assertions.runtime import assert_in
            assert_in(5, [1, 2, 3], assertion_message="{left} not found in {right}")
        self.assertFeedback(e, """Failed Instructor Test
Student code failed instructor test.
5 not found in [1, 2, 3]
""")

    def test_assertion_template_fallback_on_error(self):
        """Test that template with missing variables falls back to literal"""
        with Execution('5') as e:
            from pedal.assertions.runtime import assert_equal
            assert_equal(1, 2, assertion_message="{left} was not {missing_variable}")
        self.assertFeedback(e, """Failed Instructor Test
Student code failed instructor test.
{left} was not {missing_variable}
""")

    def test_assertion_false_disables_message(self):
        """Test that assertion=False disables assertion message"""
        with Execution('5') as e:
            from pedal.assertions.runtime import assert_equal
            assert_equal(1, 2, assertion=False)
        self.assertFeedback(e, """Failed Instructor Test
Student code failed instructor test.
""")

    def test_multiple_custom_parameters(self):
        """Test that multiple custom parameters work together"""
        with Execution('5') as e:
            from pedal.assertions.runtime import assert_equal
            assert_equal(1, 2, 
                        assertion_message="Values {left} and {right} differ",
                        explanation="This is a custom explanation with {left}")
        self.assertFeedback(e, """Failed Instructor Test
Student code failed instructor test.
Values 1 and 2 differ
This is a custom explanation with 1""")


if __name__ == '__main__':
    unittest.main()