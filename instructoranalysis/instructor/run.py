import ast
import re
import types
import sys
    
import mocked
from timeout import timeout

try:
    import io
except:
    io = None


_REJECT_TRACEBACK_FILE_PATTERN = re.compile(r'[./]')

def _override_builtins(namespace):
    '''
    Construct a new namespace based on the `namespace` and the original
    `__builtins__`, suitable for `exec`.
    '''
    # Obtain the dictionary of built-in methods, which might not exist in
    # some python versions (e.g., Skulpt)
    try:
        __builtins__
    except NameError:
        default_builtins = {}
    else:
        if type(__builtins__) is types.ModuleType:
            default_builtins = __builtins__.__dict__
        else:
            default_builtins = __builtins__

    # Create a shallow copy of the dictionary of built-in methods. Then,
    # we'll take specific ones that are unsafe and replace them.
    safe_globals = {}
    safe_globals["__builtins__"] = default_builtins.copy()
    for name, function in namespace.items():
        mocked._original_builtins[name] = default_builtins[name]
        safe_globals["__builtins__"][name] = function
        
    return safe_globals

def _threaded_execution(code):
    pass

from unittest.mock import patch, mock_open, MagicMock
fake_module = types.ModuleType('matplotlib')
fake_module.pyplot = types.ModuleType('pyplot')
MOCKED_MODULES = {
        'matplotlib': fake_module,
        'matplotlib.pyplot': fake_module.pyplot,
        }
fake_module.pyplot.secret = "Hello world"

@patch.dict(sys.modules, MOCKED_MODULES)
def _regular_execution(code, filename, mocked_input=None):
    student_locals = _override_builtins({
        'compile':  mocked._disabled_compile,
        'eval':     mocked._disabled_eval,
        'exec':     mocked._disabled_exec,
        'globals':  mocked._disabled_globals,
        'open':     mocked._restricted_open,
    })
    # Redirect stdout/stdin as needed
    old_stdout = sys.stdout
    old_stdin = sys.stdin
    capture_stdout = io.StringIO()
    injectin = io.StringIO(mocked_input)
    sys.stdout = capture_stdout
    sys.stdin = injectin
    try:
        # Calling compile instead of just passing the string source to exec
        # ensures that we get meaningul filenames in the traceback when tests
        # fail or have errors.
        compiled_code = compile(code, filename, 'exec')
        exec(compiled_code, student_locals, student_locals)
    finally:
        sys.stdout = old_stdout
        sys.stdin = old_stdin
    output = capture_stdout.getvalue()
    return (student_locals, output)

def run(code, filename="__main__.py", threaded=False):
    if threaded and threading is not None:
        return _threaded_execution(code)
    else:
        return _regular_execution(code, filename)

def run_file(filename, threaded=False):
    with open(filename, 'r') as code_file:
        code = code_file.read() + '\n'
    return run(code, filename, threaded)

if __name__ == "__main__":
    code = """
import matplotlib.pyplot as plt
print(plt.secret)
"""
    (student_locals, output) = run(code)
    for name, value in student_locals.items():
        if name == "__builtins__":
            print(name, ":", "Many things:", len(value))
        else:
            print(name, ":", value)
    