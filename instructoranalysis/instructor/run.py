'''

Common desires:

Run a file with student's code
run(filename)
    run('canvas_analyzer.py') -> execute main function
    load('canvas_analyzer'.py) -> Do not execute main function
    
    *args: positional arguments
    **kwargs: named arguments
    
    _parameters or _arguments ?: {str : ANY}
    _modules: {str : ANY}
    _inputs: [str] or generator
    _example: str

Run the given string as code
run(code)

Run a specific function from the students' code
run(function_name)
    student = run('canvas_analyzer.py')
    student.run('main')
    student_print_user = report.run('print_user')

Run the code/function again, but under different circumstances
    run('canvas_analyzer.py')

Run with the given stdin, parameters, or global variables
    run(code, _inputs=['first', 'second', 'third'])
    run(code, _inputs=special_input_function)
    run(code, parameters={'first_argument': 5})
    run(code, first_argument=5)
    
    run(code, _globals={})
    Default stdin is a special generator that just keeps returning values

Disable certain modules, built-in functions
    student = run('canvas_analyzer.py', _modules=)

Provide alternative implementation for certain modules
    MatPlotLib should be able to be swapped out
    time.sleep becomes pass

Handle the output, variables, exceptions, or global state
    output vs. raw_output: get formatted lines or 
    
    student.raw_output: string
    student.output: list of string/objects
    student.variables: dict
    student.functions: dict (only callables)

Give an explanation of the run:
    Have a default explanation based on the values given, but allow a symbolic
    explanation too.
    
Ensure student has the right version of a file based on hashes, and ensure
    that student has not modified the files
Minimum python version

Handle golden files?

String normalization for improved comparisons

'''


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
    
class RunReport:
    def __init__(self, variables=None, raw_output=None):
        if variables is None:
            variables = {}
        if raw_output is None:
            raw_output = ""
        self.variables = variables
        self.raw_output = raw_output
        lines = raw_output.rstrip().split("\n")
        self.output = [line.rstrip() for line in lines]
    
    def run(self, function):
        


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

def _threaded_execution(code, filename, inputs=None):
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
def _regular_execution(code, filename, inputs=None):
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
    injectin = io.StringIO(inputs)
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
    return RunReport(student_locals, output)

def run(code, filename="__main__.py", inputs=None, threaded=False):
    if threaded and threading is not None:
        return _threaded_execution(code, filename, inputs)
    else:
        return _regular_execution(code, filename, inputs)

def run_file(filename, inputs, threaded=False):
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
    