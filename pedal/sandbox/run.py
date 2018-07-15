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
    _filename: str
    _threaded: bool

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
    
    

Give an explanation of the run:
    Have a default explanation based on the values given, but allow a symbolic
    explanation too.
    
Ensure student has the right version of a file based on hashes, and ensure
    that student has not modified the files
Minimum python version

Handle golden files?

String normalization for improved comparisons
'''

from pprint import pprint
import ast
import re
import types
import sys
    
from pedal.sandbox import mocked
from pedal.sandbox.timeout import timeout

try:
    import io
except:
    io = None
    
def _dict_extends(d1, d2):
    '''
    Helper function to create a new dictionary with the contents of the two
    given dictionaries. Does not modify either dictionary, and the values are
    copied shallowly. If there are repeates, the second dictionary wins ties.
    
    The function is written to ensure Skulpt compatibility.
    
    Args:
        d1 (dict): The first dictionary
        d2 (dict): The second dictionary
    
    '''
    d3 = {}
    for key, value in d1.items():
        d3[key] = value
    for key, value in d2.items():
        d3[key] = value
    return d3
    
def run_code(code, _as_filename='__main__', _modules=None, _inputs=None, 
             _example=None, _threaded=False):
    '''
    Load the given code, but do so as the __main__ file - thereby running
    any code guarded by __name__==__main__.
    '''
    return _regular_execution(code, _as_filename, {}, _modules=_modules, 
                              _inputs=_inputs, _example=_example, _threaded=_threaded)
    
def load(filename, _as_filename=None, _modules=None, _inputs=None, 
         _example=None, _threaded=False):
    '''
    Load the given filename.
    '''
    if _as_filename is None:
        _as_filename = filename
    with open(filename, 'r') as code_file:
        code = code_file.read() + '\n'
    return load_code(code, _as_filename, {}, _modules=_modules, 
                     _inputs=_inputs, _example=_example, _threaded=_threaded)
    
class RunReport:
    '''
    student.raw_output: string
    student.output: list of string/objects
    student.variables: dict
    student.functions: dict (only callables)
    '''
    def __init__(self, variables=None, raw_output=None, exception=None, filename="__main__"):
        # variables
        if variables is None:
            variables = {}
        self.variables = variables
        # functions
        self.functions = {k:v for k,v in variables.items() if callable(v)}
        # Update outputs
        self.set_output(raw_output)
        # filename
        self.filename = filename
        # Temporary variables
        self.temporaries = set()
        self.backups = {}
        # Exception
        self.exception = exception
    
    def set_output(self, raw_output):
        # raw_output
        if raw_output is None:
            raw_output = ""
        self.raw_output = raw_output
        # output
        lines = raw_output.rstrip().split("\n")
        self.output = [line.rstrip() for line in lines]
        
    def purge_temporaries(self):
        ''' delete any variables that have been made as temporaries '''
        for key in self.temporaries:
            if key in self.backups:
                self.variables[key] = self.backups[key]
            else:
                del self.variables[key]
    
    def make_temporary(self, category, name, value):
        key = '_temporary_{}_{}'.format(category, name)
        if key in self.variables:
            self.backups[key] = self.variables[key]
        self.temporaries.add(key)
        self.variables[key] = value
        return key
    
    def run(self, function, *args, **kwargs):
        '''
        _arguments=None, _as_filename=None, 
            _target = '_', _modules=None, _inputs=None, _example=None, 
            _threaded=False, 
        '''
        _arguments = kwargs.pop('_arguments', {})
        _as_filename = kwargs.pop('_as_filename', self.filename)
        target = kwargs.pop('_target', '_')
        _modules = kwargs.pop('_modules', {})
        _inputs = kwargs.pop('_inputs', None)
        _example = kwargs.pop('_example', None)
        _threaded = kwargs.pop('_threaded', False)
        # With all the special args done, the remainder are regular kwargs
        kwargs = _dict_extends(_arguments, kwargs)
        # Make sure it's a valid function in the namespace (TODO: but what?)
        if function not in self.functions:
            pass
        # Create the actual arguments and call
        args = [self.make_temporary('arg', index, value)
                for index, value in enumerate(args)]
        kwargs = ["{}={}".format(key, self.make_temporary('kwarg', key, value))
                  for key, value in kwargs.items()]
        arguments = ", ".join(args+kwargs)
        call = "{} = {}({})".format(target, function, arguments)
        # Execute
        result = _regular_execution(call, self.filename, self.variables)
        self._steal_results(result)
        self._ = self.variables[target]
        # Clean up
        self.purge_temporaries()
        return result
        
    def _steal_results(self, other):
        self.exception = other.exception
        self.set_output(other.raw_output)

_REJECT_TRACEBACK_FILE_PATTERN = re.compile(r'[./]')

def _threaded_execution(code, filename, inputs=None):
    pass
    
def _make_inputs(*input_list, repeat=None):
    '''
    Helper function for creating mock user input.
    
    Params:
        input_list (list of str): The list of inputs to be returned
    Returns:
        function (str=>str): The mock input function that is returned, which
                             will return the next element of input_list each
                             time it is called.
    '''
    generator = iter(input_list)
    def mock_input(prompt=''):
        print(prompt)
        try:
            return next(generator)
        except StopIteration as SI:
            if repeat is None:
                raise SI
            else:
                return repeat
    return mock_input

from unittest.mock import patch, mock_open, MagicMock
fake_module = types.ModuleType('matplotlib')
fake_module.pyplot = types.ModuleType('pyplot')
MOCKED_MODULES = {
        'matplotlib': fake_module,
        'matplotlib.pyplot': fake_module.pyplot,
        }
fake_module.pyplot.secret = "Hello world"

'''
Hooks for pre/post execution. If set to be callable functions, they will
be executed before and after execution (regardless of its success)
'''
pre_execution = None
post_execution = None

@patch.dict(sys.modules, MOCKED_MODULES)
def _regular_execution(code, filename, namespace, _inputs=None, **kwargs):
    '''
    Given the args and kwargs, construct a relevant function call.
    Make the parameters' values available as locals? Or globals perhaps?
    
    Args:
        code (str): The code to be executed
    '''
    if _inputs is None:
        _inputs = []
    mocked._override_builtins(namespace, {
        'compile':  mocked._disabled_compile,
        'eval':     mocked._disabled_eval,
        'exec':     mocked._disabled_exec,
        'globals':  mocked._disabled_globals,
        'open':     mocked._restricted_open,
        'input':    _make_inputs(*_inputs),
        'raw_input':    _make_inputs(*_inputs),
    })
    # Redirect stdout/stdin as needed
    old_stdout = sys.stdout
    old_stdin = sys.stdin
    capture_stdout = io.StringIO()
    #injectin = io.StringIO(inputs)
    sys.stdout = capture_stdout
    #sys.stdin = injectin
    exception = None
    if callable(pre_execution):
        pre_execution()
    try:
        # Calling compile instead of just passing the string source to exec
        # ensures that we get meaningul filenames in the traceback when tests
        # fail or have errors.
        compiled_code = compile(code, filename, 'exec')
        exec(compiled_code, namespace)
    except StopIteration:
        input_failed = True
        result= None
    except Exception as e:
        '''if example is None:
            code = _demonstrate_call(a_function, parameters)
        else:
            code = example
        _raise_improved_error(e, code)'''
        exception = e
    finally:
        sys.stdout = old_stdout
        #sys.stdin = old_stdin
    if callable(post_execution):
        post_execution()
    output = capture_stdout.getvalue()
    return RunReport(namespace, output, exception=exception)

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
    