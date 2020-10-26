__name__ = 'f'
from pprint import pprint
import inspect
d1 = []
d2 = []
def mock_input1(*prompt):
    print("<A>")
    stack = inspect.stack()
    pprint(stack)
    print([id(f.frame.f_globals) for f in stack])
    d1.append("1")
    return 1
def mock_input2(*prompt):
    print("<B>")
    stack = inspect.stack()
    pprint(stack)
    print([id(f.frame.f_globals) for f in stack])
    d2.append("2")
    return 2
first = """
def x():
    return input()
"""
second = "y = x()"
d = {'input': mock_input1}
print(id(d))
# First exec, define x
exec(compile(first, "first.py", "exec"), d)
exec(compile(second, "second.py", "exec"), d)
d['input'] = mock_input2
exec(compile(second, "third.py", "exec"), d)
print(d1)
print(d2)
