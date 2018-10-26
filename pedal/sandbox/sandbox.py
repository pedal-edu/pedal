'''

queue_inputs(*args)
reset_output()
get_output()
run_student()
^ All of these work on a Sandbox object already prepared

run_code => Sandbox
run_file => Sandbox

Methods
    __init__
    Sandbox.run
    Sandbox.call
Fields
    data
    output
    raw_output
    exception
    inputs
Internals
    _temporaries
    _backups

Execution arguments:
    _as_filename='__main__'
    _modules=None
    _inputs=None
    _example=None
    _threaded=False

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
import io
import os
from unittest.mock import patch, mock_open, MagicMock
import traceback

from pedal.report import MAIN_REPORT
from pedal.sandbox import mocked
from pedal.sandbox.timeout import timeout
from pedal.sandbox.messages import EXTENDED_ERROR_EXPLANATION
    
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

_REJECT_TRACEBACK_FILE_PATTERN = re.compile(r'[./]')
    
class Sandbox:
    '''
    '''
    
    # Hooks for pre/post execution. If set to be callable functions, they will
    # be executed before and after execution (regardless of its success)
    pre_execution = None
    post_execution = None

    '''
    student.raw_output: string
    student.output: list of string/objects
    student.variables: dict
    student.functions: dict (only callables)
    '''
    def __init__(self, data=None, raw_output=None, exception=None, 
                 filename="__main__", modules=None, full_trace=False):
        # data
        if data is None:
            data = {}
        self.data = data
        # Update outputs
        self.set_output(raw_output)
        # filename
        self.filename = filename
        # Temporary data
        self.temporaries = set()
        self.backups = {}
        # Exception
        self.exception = exception
        self.exception_position = None
        # Input
        self.inputs = None
        # Modules
        self.setup_mocks(modules)
        # Settings
        self.full_trace = full_trace
        self.MAXIMUM_VALUE_LENGTH = 120
        
    def setup_mocks(self, modules):
        self.mocked_modules = {}
        self.modules = {}
        # MatPlotLib's PyPlot
        fake_module = types.ModuleType('matplotlib')
        fake_module.pyplot = types.ModuleType('pyplot')
        self.mocked_modules['matplotlib'] = fake_module
        self.mocked_modules['matplotlib.pyplot'] = fake_module.pyplot
        mock_plt = mocked.MockPlt()
        mock_plt._add_to_module(fake_module.pyplot)
        self.modules['matplotlib.pyplot'] = mock_plt
    
    @property
    def functions(self):
        return {k:v for k,v in self.data.items() if callable(v)}
    
    def set_output(self, raw_output):
        if raw_output is None:
            self.raw_output = ""
            self.output = []
        else:
            self.raw_output = raw_output
            lines = raw_output.rstrip().split("\n")
            self.output = [line.rstrip() for line in lines]
    
    def append_output(self, raw_output):
        self.raw_output += raw_output
        lines = raw_output.rstrip().split("\n")
        self.output += [line.rstrip() for line in lines]
    
    def set_input(self, inputs):
        if isinstance(inputs, tuple):
            self.inputs = _make_inputs(*inputs)
        else:
            self.inputs = inputs
        
    def purge_temporaries(self):
        ''' delete any data that have been made as temporaries '''
        for key in self.temporaries:
            if key in self.backups:
                self.data[key] = self.backups[key]
            else:
                del self.data[key]
    
    def make_temporary(self, category, name, value):
        key = '_temporary_{}_{}'.format(category, name)
        if key in self.data:
            self.backups[key] = self.data[key]
        self.temporaries.add(key)
        self.data[key] = value
        return key
    
    def run_file(filename, _as_filename=None, _modules=None, _inputs=None, 
             _example=None, _threaded=False):
        '''
        Load the given filename.
        '''
        if _as_filename is None:
            _as_filename = filename
        with open(filename, 'r') as code_file:
            code = code_file.read() + '\n'
        self.run(code, _as_filename, _modules, _inputs, _example, _threaded)
    
    def call(self, function, *args, **kwargs):
        # Make sure it's a valid function in the namespace (TODO: but what?)
        if function not in self.functions:
            pass
        _arguments = kwargs.pop('_arguments', {})
        _as_filename = kwargs.pop('_as_filename', self.filename)
        target = kwargs.pop('_target', '_')
        _modules = kwargs.pop('_modules', {})
        _inputs = kwargs.pop('_inputs', self.inputs)
        _threaded = kwargs.pop('_threaded', False)
        # With all the special args done, the remainder are regular kwargs
        kwargs = _dict_extends(_arguments, kwargs)
        # Create the actual arguments and call
        args = [self.make_temporary('arg', index, value)
                for index, value in enumerate(args)]
        kwargs = ["{}={}".format(key, self.make_temporary('kwarg', key, value))
                  for key, value in kwargs.items()]
        arguments = ", ".join(args+kwargs)
        call = "{} = {}({})".format(target, function, arguments)
        if '_example' in kwargs:
            _example = kwargs['_example']
        else:
            _example = '\nHappened when I ran:'
            #_example = self._demonstrate_call(function, args+kwargs)
        self.run(call, _as_filename, _modules, _inputs, 
                 _example=_example, _threaded=_threaded)
        self._ = self.data[target]
        return self._
    
    def run(self, code, _as_filename=None, _modules=None, _inputs=None, 
            _example=None, _threaded=False):
        '''
        _arguments=None, _as_filename=None, 
            _target = '_', _modules=None, _inputs=None, _example=None, 
            _threaded=False, 
        '''
        if _as_filename is None:
            _as_filename = self.filename
        if _inputs is None:
            if self.inputs is None:
                _inputs = _make_inputs('0', repeat='0')
            else:
                _inputs = self.inputs
        else:
            _inputs = _make_inputs(*_inputs)
        # Execute
        mocked._override_builtins(self.data, {
            'compile':   mocked._disabled_compile,
            'eval':      mocked._disabled_eval,
            'exec':      mocked._disabled_exec,
            'globals':   mocked._disabled_globals,
            'open':      mocked._restricted_open,
            'input':     _inputs,
            'raw_input': _inputs,
            'sys':       sys,
            'os':        os
        })
        # Redirect stdout/stdin as needed
        old_stdout = sys.stdout
        old_stdin = sys.stdin
        capture_stdout = io.StringIO()
        #injectin = io.StringIO(inputs)
        sys.stdout = capture_stdout
        #sys.stdin = injectin
        self.exception = None
        self.exception_position = None
        
        if callable(self.pre_execution):
            self.pre_execution()
        
        try:
            # Calling compile instead of just passing the string source to exec
            # ensures that we get meaningul filenames in the traceback when
            # tests fail or have errors.
            with patch.dict('sys.modules', self.mocked_modules):
                compiled_code = compile(code, _as_filename, 'exec')
                exec(compiled_code, self.data)
        except StopIteration:
            input_failed = True
            result= None
        except Exception as e:
            if _example is not None:
                _raise_improved_error(e, _example)
            self.exception = e
            self.exc_info = sys.exc_info()
            cl, exc, tb = sys.exc_info()
            line_number = traceback.extract_tb(tb)[-1][1]
            while tb and self._is_relevant_tb_level(tb):
                tb = tb.tb_next
            length = self._count_relevant_tb_levels(tb)
            tb_e = traceback.TracebackException(cl, exc, tb, 
                                                limit=length,
                                                capture_locals=True)
            msgLines = list(tb_e.format())
            self.exception_position = {'line': line_number}
        finally:
            sys.stdout = old_stdout
            #sys.stdin = old_stdin
            if callable(self.post_execution):
                self.post_execution()
        self.append_output(capture_stdout.getvalue())
        # Clean up
        self.purge_temporaries()
    
    def get_names_by_type(self, type, exclude_builtins=True):
        result = []
        for name, value in self.data.items():
            if isinstance(value, type):
                if exclude_builtins and name.startswith('__'):
                    continue
                result.append(name)
        return result
    
    def get_values_by_type(self, type, exclude_builtins=True):
        names = self.get_names_by_type(type, exclude_builtins)
        return [self.data[name] for name in names]
    
    def format_exception(self):
        cl, exc, tb = self.exc_info
        line_number = traceback.extract_tb(tb)[-1][1]
        while tb and self._is_relevant_tb_level(tb):
            tb = tb.tb_next
        length = self._count_relevant_tb_levels(tb)
        tb_e = traceback.TracebackException(cl, exc, tb, 
                                            limit=length,
                                            capture_locals=False)
        lines = [x.replace(', in <module>', '', 1) for x in list(tb_e.format())]
        return "Traceback:\n"+''.join(lines[1:])
        
    def _count_relevant_tb_levels(self, tb):
        length = 0
        while tb and not self._is_relevant_tb_level(tb):
            length += 1
            tb = tb.tb_next
        return length
    
    def _is_relevant_tb_level(self, tb):
        '''
        Determines if the give part of the traceback is relevant to the user.
        
        Returns:
            boolean: True means it is NOT relevant
        '''
        # Are in verbose mode?
        if self.full_trace:
            return False
        filename, _, _, _ = traceback.extract_tb(tb, limit=1)[0]
        # Is the error in this test file?
        if filename == __file__:
            return True
        # Is the error related to a file in the parent directory?
        current_directory = os.path.dirname(os.path.realpath(__file__))
        parent_directory = os.path.dirname(current_directory)
        if filename.startswith(current_directory):
            return False
        # Is the error in a local file?
        if filename.startswith('.'):
            return False
        # Is the error in an absolute path?
        if not os.path.isabs(filename):
            return False
        # Okay, it's not a student related file
        return True
    
    def _demonstrate_call(self, a_function, parameters):
        if not isinstance(a_function, str):
            a_function = a_function.__name__
        defs = ""
        for key, value in parameters.items():
            value = pprint.pformat(value, indent=2, compact=True)
            if len(value) >= MAXIMUM_VALUE_LENGTH:
                value = value[:MAXIMUM_VALUE_LENGTH-3] + "..."
            defs += "{} = {}\n".format(key, value)
        arguments = ", ".join(parameters.keys())
        code = "{defs}{name}({arguments})".format(name=a_function, defs=defs, 
                                                  arguments=arguments)
        code = code.replace("{", "{{").replace("}", "}}")
        code = indent4(code)
        code = ".\n\nThe error above occurred when I ran:\n"+code
        return code
        
class _KeyError(KeyError):
    def __str__(self):
        return BaseException.__str__(self)
        
def _append_to_error(e, message):
    e.args = (e.args[0]+message,)
    return e
        
def _raise_improved_error(e, code):
    if isinstance(e, KeyError):
        raise _copy_key_error(e, code) from None
    else:
        raise _append_to_error(e, code)

def _copy_key_error(e, code):
    new_args = (repr(e.args[0])+code,)
    new_except = _KeyError(*new_args)
    new_except.__cause__ = e.__cause__
    new_except.__traceback__ = e.__traceback__
    new_except.__context__  = e.__context__ 
    return new_except

def _threaded_execution(code, filename, inputs=None):
    pass
    
def _make_inputs(*input_list, **kwargs):
    '''
    Helper function for creating mock user input.
    
    Params:
        input_list (list of str): The list of inputs to be returned
    Returns:
        function (str=>str): The mock input function that is returned, which
                             will return the next element of input_list each
                             time it is called.
    '''
    if 'repeat' in kwargs:
        repeat = kwargs['repeat']
    else:
        repeat = None
    generator = iter(input_list)
    def mock_input(prompt=''):
        print(prompt)
        try:
            return next(generator)
        except StopIteration as SI:
            if repeat is None:
                # TODO: Make this a custom exception
                raise SI
            else:
                return repeat
    return mock_input

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
    