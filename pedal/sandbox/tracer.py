from bdb import Bdb
import sys


class RecursionDetected(Exception):
    pass


class RecursionDetector(Bdb):
    def do_clear(self, arg):
        pass

    def __init__(self, *args):
        Bdb.__init__(self, *args)
        self.stack = set()

    def user_call(self, frame, argument_list):
        code = frame.f_code
        if code in self.stack:
            raise RecursionDetected
        self.stack.add(code)
        print(len(self.stack))

    def user_return(self, frame, return_value):
        if frame.f_code in self.stack:
            self.stack.remove(frame.f_code)


def test_recursion(code):
    detector = RecursionDetector()
    detector.set_trace()
    try:
        detector.run(code)
    except RecursionDetected:
        return True
    else:
        return False
    finally:
        sys.settrace(None)


recursive_solution = """
def x(num):
    if x:
        return x(num-1)
    return "Done"
"""
nonrecursive_solution = """
def y(num):
    return "Done"
"""

assert test_recursion(recursive_solution)
assert not test_recursion(nonrecursive_solution)
