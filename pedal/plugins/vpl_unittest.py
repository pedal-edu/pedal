from unittest.util import safe_repr
from pedal import explain

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
        for method in methods:
            self.setUp()
            try:
                getattr(self, method)()
            except UnitTestedAssignment.AssertionException as e:
                explain(e.message)
                return False
            self.tearDown()
        return True
    def assertSimilarStrings(self, first, second, msg):
        if _normalize_string(first) != _normalize_string(second):
            return self.assertEqual(first, second, msg)
    def assertEqual(self, val1, val2, msg=None, exact=False):
        if val1 == val2:
            return
        if not exact and isinstance(val1, str) and isinstance(val2, str):
            self.assertSimilarStrings(val1, val2, msg)
        elif (not exact and isinstance(val1, (int, float)) and 
              isinstance(val2, (int, float))):
            if abs(val2-val1) <= UnitTestedAssignment.DELTA:
                return
        standardMsg = "{} != {}".format(safe_repr(val1), safe_repr(val2))
        self.fail(msg, standardMsg)

    def assertIn(self, member, container, msg=None):
        if member not in container:
            standardMsg = "{} not found in {}".format(safe_repr(member),
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

    def fail(self, message, standardMsg):
        if message is None:
            message = standardMsg
        raise UnitTestedAssignment.AssertionException(message)
        