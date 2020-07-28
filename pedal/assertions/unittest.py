"""
Drop-in replacement class for unittest.TestCase.
"""
from pedal.assertions.runtime import *


class PedalTestCase:
    """
    Drop-in replacement for the existing unittest.TestCase class. Emulates
    the original interface, but also supports all the Pedal features, allowing
    an easier transition to our toolset.

    TODO: Implement the entire interface
        setUp()
        tearDown()
        setUpClass()
        tearDownClass()
        skipTest()
        subTest()
        debug()
        run()
        fail()
    """

    def assertEqual(self, left, right, msg=None, **kwargs):
        """
        Test that first and second are equal.
        If the values do not compare equal, the test will fail.
        """
        return assert_equal(left, right, explanation=msg, **kwargs)

    def assertNotEqual(self, left, right, msg=None, **kwargs):
        """
        Test that first and second are not equal.
        If the values do compare equal, the test will fail.
        """
        return assert_not_equal(left, right, explanation=msg, **kwargs)

    def assertLess(self, left, right, msg=None, **kwargs):
        """
        Test that first is less than the second.
        """
        return assert_less(left, right, explanation=msg, **kwargs)

    def assertLessEqual(self, left, right, msg=None, **kwargs):
        """
        Test that first is less than or equal to the second.
        """
        return assert_less_equal(left, right, explanation=msg, **kwargs)

    def assertGreater(self, left, right, msg=None, **kwargs):
        """
        Test that first is greater than the second.
        """
        return assert_greater(left, right, explanation=msg, **kwargs)

    def assertGreaterEqual(self, left, right, msg=None, **kwargs):
        """
        Test that first is greater than or equal to the second.
        """
        return assert_greater_equal(left, right, explanation=msg, **kwargs)

    def assertIn(self, needle, haystack, msg=None, **kwargs):
        """
        Tests that the needle is in the haystack.
        """
        return assert_in(needle, haystack, explanation=msg, **kwargs)

    def assertNotIn(self, needle, haystack, msg=None, **kwargs):
        """
        Tests that the needle is not in the haystack.
        """
        return assert_not_in(needle, haystack, explanation=msg, **kwargs)

    def assertIs(self, left, right, msg=None, **kwargs):
        """
        Test that first is second.
        """
        return assert_is(left, right, explanation=msg, **kwargs)

    def assertIsNot(self, left, right, msg=None, **kwargs):
        """
        Test that first is not second.
        """
        return assert_is_not(left, right, explanation=msg, **kwargs)

    def assertIsNone(self, expr, msg=None, **kwargs):
        """
        Test that expr is None
        """
        return assert_is_none(expr, explanation=msg, **kwargs)

    def assertIsNotNone(self, expr, msg=None, **kwargs):
        """
        Test that expr is not None
        """
        return assert_is_not_none(expr, explanation=msg, **kwargs)

    def assertTrue(self, expr, msg=None, **kwargs):
        """
        Test that expr is true
        """
        return assert_true(expr, explanation=msg, **kwargs)

    def assertFalse(self, expr, msg=None, **kwargs):
        """
        Test that expr is false
        """
        return assert_false(expr, explanation=msg, **kwargs)

    def assertLengthEqual(self, sequence, length, msg=None, **kwargs):
        """
        Test that sequence has length.
        """
        return assert_length_equal(sequence, length, explanation=msg, **kwargs)

    def assertLengthNotEqual(self, sequence, length, msg=None, **kwargs):
        """
        Test that sequence does not have length.
        """
        return assert_length_not_equal(sequence, length, explanation=msg, **kwargs)

    def assertLengthLess(self, sequence, length, msg=None, **kwargs):
        """
        Test that sequence has less than length.
        """
        return assert_length_less(sequence, length, explanation=msg, **kwargs)

    def assertLengthLessEqual(self, sequence, length, msg=None, **kwargs):
        """
        Test that sequence has less or equal to length.
        """
        return assert_length_less_equal(sequence, length, explanation=msg, **kwargs)

    def assertLengthGreater(self, sequence, length, msg=None, **kwargs):
        """
        Test that sequence has greater than length.
        """
        return assert_length_greater(sequence, length, explanation=msg, **kwargs)

    def assertLengthGreaterEqual(self, sequence, length, msg=None, **kwargs):
        """
        Test that sequence has greater or equal length.
        """
        return assert_length_greater_equal(sequence, length, explanation=msg, **kwargs)

    def assertIsInstance(self, obj, cls, msg=None, **kwargs):
        """
        Test that obj is an instance of cls.
        """
        return assert_is_instance(obj, cls, explanation=msg, **kwargs)

    def assertNotIsInstance(self, obj, cls, msg=None, **kwargs):
        """
        Test that obj is not an instance of cls.
        """
        return assert_not_is_instance(obj, cls, explanation=msg, **kwargs)

    def assertAlmostEqual(self, first, second, places=7, msg=None, delta=None, **kwargs):
        """ Test that first is approximately equal to second. """
        if places is not None:
            delta = 10**(-places)
        return assert_equal(first, second, delta=delta, explanation=msg, **kwargs)

    def assertNotAlmostEqual(self, first, second, places=7, msg=None, delta=None, **kwargs):
        """ Test that first is not approximately equal to second. """
        if places is not None:
            delta = 10**(-places)
        return assert_not_equal(first, second, delta=delta, explanation=msg, **kwargs)

    def assertRegex(self, regex, text, msg=None, **kwargs):
        """
        Test that regex matches text.
        """
        return assert_regex(regex, text, explanation=msg, **kwargs)

    def assertNotRegex(self, regex, text, msg=None, **kwargs):
        """
        Test that regex does not match text.
        """
        return assert_not_regex(regex, text, explanation=msg, **kwargs)

    assertMultiLineEqual = assert_equal
    assertSequenceEqual = assert_equal
    assertListEqual = assert_equal
    assertTupleEqual = assert_equal
    assertSetEqual = assert_equal
    assertDictEqual = assert_equal
