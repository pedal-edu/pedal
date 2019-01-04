from pprint import pprint
import ast
import re
import sys
import io
import os
import bdb
import string
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
    copied shallowly. If there are repeats, the second dictionary wins ties.
    
    The function is written to ensure Skulpt compatibility.
    
    Args:
        d1 (dict): The first dictionary
        d2 (dict): The second dictionary
    Returns:
        dict: The new dictionary
    '''
    d3 = {}
    for key, value in d1.items():
        d3[key] = value
    for key, value in d2.items():
        d3[key] = value
    return d3


class SandboxException(Exception):
    pass

class SandboxPreventModule(Exception):
    pass

class SandboxHasNoFunction(SandboxException):
    pass

class SandboxHasNoVariable(SandboxException):
    pass
    
class SandboxTracer(bdb.Bdb):
    def __init__(self, filename):
        super().__init__()
        self.calls = {}
        self.set_break(filename, 1)
        

class SandboxTraceback:
    def format_exception(self, _pre=""):
        if not self.exception:
            return ""
        cl, exc, tb = self.exc_info
        line_number = traceback.extract_tb(tb)[-1][1]
        while tb and self._is_relevant_tb_level(tb):
            tb = tb.tb_next
        length = self._count_relevant_tb_levels(tb)
        tb_e = traceback.TracebackException(cl, exc, tb, 
                                            limit=length,
                                            capture_locals=False)
        lines = [x.replace(', in <module>', '', 1) for x in list(tb_e.format())]
        return _pre+"\nTraceback:\n"+''.join(lines[1:])
        
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
        filename, a_, b_, _ = traceback.extract_tb(tb, limit=1)[0]
        #print(filename, self.instructor_filename, __file__, a_, b_)
        # Is the error in this test file?
        if filename == __file__:
            return True
        if filename == self.instructor_filename:
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

class SandboxResult:
    def __init__(self, value):
        self.value = value
        
class DataSandbox:
    '''
    Simplistic class that contains the functions for accessing a self-contained
    student data namespace.
    '''
    def __init__(self):
        self.data = {}
    
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
    
    def get_variables_by_type(self, type, exclude_builtins=True):
        names = self.get_names_by_type(type, exclude_builtins)
        return [(name, self.data[name]) for name in names]
    
    @property
    def functions(self):
        '''
        Retrieve a list of all the callable names in the students' namespace.
        In other words, get a list of all the functions the student defined.
        
        Returns:
            list of callables
        '''
        return {k:v for k,v in self.data.items() if callable(v)}
    
class Sandbox(DataSandbox):
    '''
    
    The Sandbox is a container that can safely execute student code and store
    the result.
    
    Attributes:
        data: The namespace produced by the students' code. This is basically
            a dictionary mapping valid python names to their values.
        raw_output (str): The exact literal results of all the `print` calls
            made so far, including the "\n" characters.
        output (list of str): The current lines of output, broken up by
            distinct print calls (not "\n" characters). Note that this will
            not have any "\n" characters unless you explicitly printed them.
        modules: A dictionary of the mocked modules (accessible by their
            imported names).
        context: A list of strings representing the code previously run through
            this sandbox.
        contextualize (bool): Whether or not to contextualize stack frames.
    '''
    
    def __init__(self, initial_data=None,
                 initial_raw_output=None, 
                 initial_exception=None, 
                 modules=None, full_trace=False, trace_execution=True,
                 threaded=False, report=None,
                 contextualize=False,
                 instructor_filename="instructor_tests.py"):
        '''
        Args:
            initial_data (dict[str:Any]): An initial namespace to provide when
                executing the students' code. The keys must be strings and
                should be valid Python names. Defaults to None, which will be
                an empty namespace.
            initial_exception (Exception): An initial exception to load into
                the Sandbox. Usually you will let the students' code generate
                its own exceptions, but if you're constructing a sandbox you
                might need to specify one. Defaults to None.
            modules: A dictionary of strings (valid python package names) that
                map to either the value True (if we provide a default
                implementation) or a user-created MockedModule.
            initial_raw_output (str): The initial printed output for the
                sandbox. Usually defaults to None to indicate a blank printed
                area.
            instructor_filename (str): The filename to display in tracebacks,
                when executing student code in instructor tests. Although you
                can specify something else, defaults to "instructor_tests.py".
        '''
        if initial_data is None:
            initial_data = {}
        self.data = initial_data
        
        # Update outputs
        self.set_output(raw_output)
        # filename
        self.filename = filename
        # Temporary data
        self._temporaries = set()
        self._backups = {}
        # Exception
        self.exception = initial_exception
        self.exception_position = None
        self.raise_exceptions_mode = False
        # Input
        self.inputs = None
        # Modules
        self.mocked_modules = {}
        self.modules = {}
        self.add_mocks(modules)
        # Settings
        self.full_trace = full_trace
        self.trace_execution = trace_execution
        self.MAXIMUM_VALUE_LENGTH = 120
        # report
        if report is None:
            report = MAIN_REPORT
        self.report = report
        # Threading
        self.threaded = threaded
        self.allowed_time = 1
        # Context
        self.context = []
        # Coverage
        self.record_coverage = False
        self.coverage_report = None
        # Hooks
        self.pre_execution = None
        self.post_execution = None
    
    def add_mocks(self, **modules):
        '''
        :param modules: Keyword listing of modules and their contents
                        (MockedModules) or True (if its one that we have a
                        default implementation for).
        :type modules: dict
        '''
        for module_name, module_data in modules.items():
            self._add_mock(module_name, module_data)
    
    def _add_mock(self, module_name, module_data):
        # MatPlotLib's PyPlot
        if module_name == 'matplotlib':
            matplotlib, modules = create_module('matplotlib.pyplot')
            self.mocked_modules.update(modules)
            if module_data is True:
                mock_plt = mocked.MockPlt()
                mock_plt._add_to_module(matplotlib.pyplot)
                self.modules['matplotlib.pyplot'] = mock_plt
            else:
                module_data._add_to_module(matplotlib.pyplot)
    
    def set_output(self, raw_output):
        '''
        Change the current printed output for the sandbox to the given value.
        If None is given, then clears all the given output (empty list for
        `output` and empty string for `raw_output`).
        
        Args:
            raw_output (str): The new raw_output for the sandbox. To compute
                the `output` attribute, the system splits and rstrips at
                newlines.
        '''
        if raw_output is None:
            #: 
            self.raw_output = ""
            self.output = []
        else:
            self.raw_output = raw_output
            lines = raw_output.rstrip().split("\n")
            self.output = [line.rstrip() for line in lines]
    
    def append_output(self, raw_output):
        '''
        Adds the string of `raw_output` to the current `raw_output` attribute.
        The added string will be split on newlines and rstripped to append
        to the `output` attribute.
        
        Args:
            raw_output (str): The new raw_output for the sandbox. To compute
                the `output` attribute, the system splits and rstrips at
                newlines.
        '''
        self.raw_output += raw_output
        lines = raw_output.rstrip().split("\n")
        self.output += [line.rstrip() for line in lines]
    
    def set_input(self, inputs):
        '''
        Queues the given value as the next arguments to the `input` function.
        '''
        if isinstance(inputs, tuple):
            self.inputs = mocked._make_inputs(*inputs)
        else:
            self.inputs = inputs
    
    def _purge_temporaries(self):
        ''' 
        Delete any variables in the namespace that have been made as
        temporaries. This happens automatically after you execute code.
        '''
        for key in self.temporaries:
            if key in self.backups:
                self.data[key] = self.backups[key]
            else:
                del self.data[key]
        self.temporaries = set()
    
    def _make_temporary(self, category, name, value):
        '''
        Create a temporary variable in the namespace for the given
        category/name. This is used to load arguments into the namespace to
        be used in function calls.
        
        Args:
            category (str): A categorical division for the temporary variable
                that can help keep the namespace distinctive - there are a
                few different kinds of categories (e.g., for regular positional
                args, star args, kwargs).
            name (str): A distinctive ID for this variable. The final variable
                name will be "_temporary_<category>_<name>".
            value: The value for this argument.
        Returns:
            str: The new name for the temporary variable.
        '''
        key = '_temporary_{}_{}'.format(category, name)
        if key in self.data:
            self.backups[key] = self.data[key]
        self.temporaries.add(key)
        self.data[key] = value
        return key
    
    def run_file(filename, as_filename=None, modules=None, inputs=None, 
                 example=None, threaded=None):
        '''
        Load the given filename and execute it within the current namespace.
        '''
        if _as_filename is None:
            _as_filename = filename
        with open(filename, 'r') as code_file:
            code = code_file.read() + '\n'
        self.run(code, as_filename, modules, inputs, example, threaded)
    
    def call(self, function, *args, **kwargs):
        '''
        Args:
            function (str): The name of the function to call that was defined
                by the user.
            target (str): The new variable in the namespace to assign to. By
                default this will be "_". If you use None, then no variable
                will be assigned to. Note that this could overwrite a variable
                in the user namespace.
                TODO: Add a feature to prevent user namespace overwriting.
            input (list of str): The strings to send in to calls to input.
                You can also pass in a generator to construct strings
                dynamically.
            threaded (bool): Whether or not the function execution should be
                executed in a separate thread. Defaults to True. This prevents
                timeouts from occuring in the students' code (a TimeOutError
                will be thrown after 3 seconds).
        Returns:
            If the call was successful, returns the result of executing the
            code. Otherwise, it will return an Exception relevant to the
            failure (might be a SandboxException, might be a user-space
            exception).
        '''
        # Confirm that the function_name exists
        if function not in self.functions:
            if function not in self.data:
                return SandboxHasNoVariable()
            else:
                return SandboxHasNoFunction()
        # Parse kwargs for any special arguments.
        as_filename = kwargs.pop('as_filename', self.instructor_filename)
        target = kwargs.pop('target', '_')
        modules = kwargs.pop('modules', {})
        inputs = kwargs.pop('inputs', self.inputs)
        threaded = kwargs.pop('threaded', self.threaded)
        contextualize = kwargs.pop('contextualize', self.contextualize)
        raise_exceptions = kwargs.pop('raise_exceptions', self.raise_exceptions_mode)
        # With all the special args done, the remainder are regular kwargs
        kwargs = _dict_extends(_arguments, kwargs)
        # Create the actual arguments and call
        actual_call, student_call = self._construct_call(function, args, kwargs)
        if contextualize:
            self.context.append(student_call)
        self.run(actual_call, as_filename, modules, inputs, 
                 example=example, threaded=threaded,
                 contextualize=contextualize,
                 raise_exceptions=raise_exceptions)
        if self.exception is None:
            self._ = self.data[target]
            return SandboxResult(self._)
        else:
            return self.exception

    def _construct_call(self, function, args, kwargs):
        str_args = [self.make_temporary('arg', index, value)
                for index, value in enumerate(args)]
        str_kwargs = ["{}={}".format(key, self.make_temporary('kwarg', key, value))
                  for key, value in kwargs.items()]
        arguments = ", ".join(str_args+str_kwargs)
        call = "{}({})".format(function, arguments)
        if target is None:
            actual = call
        else:
            actual = "{} = {}".format(target, call)
        student_call = call if target is "_" else actual
        return actual, student_call
        
    def run(self, code, as_filename=None, modules=None, inputs=None, 
            example=None, threaded=None, raise_exceptions=False,
            context=None):
        '''
        Actually execute the code
        '''
        # Redirect stdout/stdin as needed
        old_stdout = sys.stdout
        # Handle any threading if necessary
        if threaded is None:
            threaded = self.threaded
        if threaded:
            try:
                return timeout(self.allowed_time, self.run, code, _as_filename, 
                               _modules, _inputs, _example, False, 
                               _raise_exceptions, _context)
            except TimeoutError as self.exception:
                sys.stdout = old_stdout
                error_message = ("Time out error while running: <pre>{}</pre>"
                                 .format(code=code))
                self.report.attach("Timeout Error",
                                   tool='Sandbox', category='Runtime',
                                   section=self.report['source']['section'],
                                   mistakes={'message': error_message, 
                                             'error': self.exception})
                return self.exception
        if _as_filename is None:
            _as_filename = self.filename
        if _inputs is None:
            if self.inputs is None:
                _inputs = mocked._make_inputs('0', repeat='0')
            else:
                _inputs = self.inputs
        else:
            _inputs = mocked._make_inputs(*_inputs)
        # Override builtins and mock stuff out
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
        capture_stdout = io.StringIO()
        sys.stdout = capture_stdout
        self.exception = None
        self.exception_position = None
        
        if callable(self.pre_execution):
            self.pre_execution()
        
        # Patch in dangerous built-ins
        pedal_patch = patch('pedal', side_effect=SandboxPreventModule)
        pedal_patch.start()
        time_sleep_patch = patch('time.sleep', return_value=None)
        time_sleep_patch.start()
        if self.record_coverage:
            self.start_coverage(code, _as_filename)
        try:
            with patch.dict('sys.modules', self.mocked_modules):
                # Compile and run student code
                compiled_code = compile(code, _as_filename, 'exec')
                if self.trace_execution:
                    self.trace = SandboxTracer(_as_filename)
                    db.run(compiled_code, self.data)
                else:
                    exec(compiled_code, self.data)
        except StopIteration:
            input_failed = True
            result= None
        except Exception as self.exception:
            if _example is not None:
                self.exception = _raise_improved_error(self.exception, "\n\nThe above occurred when I ran:\n<pre>"+_example+"</pre>")
                self.example = _example
            elif _context is not None:
                self.exception = _raise_improved_error(self.exception, "\n\n"+_context)
                self.example = _context
            cl, exc, tb = self.exc_info = sys.exc_info()
            line_number = traceback.extract_tb(tb)[-1][1]
            while tb and self._is_relevant_tb_level(tb):
                tb = tb.tb_next
            length = self._count_relevant_tb_levels(tb)
            tb_e = traceback.TracebackException(cl, exc, tb, 
                                                limit=length,
                                                capture_locals=True)
            msgLines = [x.replace(', in <module>', '', 1) for x in list(tb_e.format())]
            self.exception_position = {'line': line_number}
        finally:
            if self.record_coverage:
                self.coverage_report = self.stop_coverage()
            time_sleep_patch.stop()
            pedal_patch.stop()
            sys.stdout = old_stdout
            #sys.stdin = old_stdin
            if callable(self.post_execution):
                self.post_execution()
        self.append_output(capture_stdout.getvalue())
        # Clean up
        self.purge_temporaries()
        if _raise_exceptions:
            self.raise_any_exceptions()