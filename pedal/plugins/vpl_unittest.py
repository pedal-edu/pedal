from unittest.util import safe_repr
from pedal import gently
from pedal.assertions.assertions import _normalize_string


class UnitTestedAssignment:
    DELTA = .001

    class AssertionException(Exception):
        def __init__(self, message):
            self.message = message

    def __init__(self):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _run_all_tests(self):
        methods = [func for func in dir(self)
                   if callable(getattr(self, func)) and
                   func.startswith('test_')]
        all_passed = True
        for method in methods:
            self.setUp()
            try:
                getattr(self, method)()
            except UnitTestedAssignment.AssertionException as e:
                gently(e.message)
                all_passed = False
            self.tearDown()
        return all_passed

    def assertSimilarStrings(self, first, second, msg):
        if _normalize_string(first) != _normalize_string(second):
            return self.assertEqual(first, second, msg, exact=True)

    def assertNotSimilarStrings(self, first, second, msg):
        if _normalize_string(first) == _normalize_string(second):
            return self.assertEqual(first, second, msg, exact=True)

    def assertLessEqual(self, val1, val2, msg=None):
        if not (val1 <= val2):
            self.fail(msg, "{} is not less than or equal to {}".format(safe_repr(val1), safe_repr(val2)))

    def assertGreaterEqual(self, val1, val2, msg=None):
        if not (val1 >= val2):
            self.fail(msg, "{} is not greater than or equal to {}".format(safe_repr(val1), safe_repr(val2)))

    def assertNotEqual(self, val1, val2, msg=None, exact=False):
        if val1 != val2:
            return
        if not exact and isinstance(val1, str) and isinstance(val2, str):
            self.assertNotSimilarStrings(val1, val2, msg)
        elif (not exact and isinstance(val1, (int, float)) and
              isinstance(val2, (int, float))):
            if abs(val2 - val1) > UnitTestedAssignment.DELTA:
                return
        standardMsg = "{} == {}".format(safe_repr(val1), safe_repr(val2))
        self.fail(msg, standardMsg)

    def assertEqual(self, val1, val2, msg=None, exact=False):
        if val1 == val2:
            return
        if not exact and isinstance(val1, str) and isinstance(val2, str):
            self.assertSimilarStrings(val1, val2, msg)
        elif (not exact and isinstance(val1, (int, float)) and
              isinstance(val2, (int, float))):
            if abs(val2 - val1) <= UnitTestedAssignment.DELTA:
                return
        standardMsg = "{} != {}".format(safe_repr(val1), safe_repr(val2))
        self.fail(msg, standardMsg)

    def assertIn(self, member, container, msg=None):
        if member not in container:
            standardMsg = "{} not found in {}".format(safe_repr(member),
                                                      safe_repr(container))
            self.fail(msg, standardMsg)

    def assertNotIn(self, member, container, msg=None):
        if member in container:
            standardMsg = "{} found in {}".format(safe_repr(member),
                                                  safe_repr(container))
            self.fail(msg, standardMsg)

    def assertTrue(self, value, msg=None):
        if not value:
            self.fail(msg, "{} is not true".format(value))

    def assertFalse(self, value, msg=None):
        if value:
            self.fail(msg, "{} is not false".format(value))

    def assertSandbox(self, sandbox, msg=None):
        if sandbox.exception is not None:
            self.fail(msg, sandbox.format_exception())

    def assertIsInstance(self, value, parent, msg=None):
        if not isinstance(value, parent):
            self.fail(msg, "{} is not an instance of {}".format(safe_repr(value), safe_repr(parent)))

    def assertHasAttr(self, object, attr, msg=None):
        if not hasattr(object, attr):
            self.fail(msg, "{} does not have an attribute named {}".format(safe_repr(object), safe_repr(attr)))

    def fail(self, message, standardMsg):
        if message is None:
            message = standardMsg
        raise UnitTestedAssignment.AssertionException(message)
