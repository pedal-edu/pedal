from pprint import pprint
import ast
import re
import sys
import io
import os
import string
from unittest.mock import patch

from pedal.report import MAIN_REPORT
from pedal.sandbox import mocked
from pedal.sandbox.exceptions import (SandboxTraceback, SandboxHasNoFunction,
                                      SandboxStudentCodeException,
                                      SandboxHasNoVariable, _add_context_to_error)
from pedal.sandbox.timeout import timeout
from pedal.sandbox.messages import EXTENDED_ERROR_EXPLANATION
from pedal.sandbox.result import SandboxResult
from pedal.sandbox.tracer import (SandboxCallTracer, SandboxCoverageTracer,
                                  SandboxBasicTracer)


def _dict_extends(d1, d2):
    """
    Helper function to create a new dictionary with the contents of the two
    given dictionaries. Does not modify either dictionary, and the values are
    copied shallowly. If there are repeats, the second dictionary wins ties.

    The function is written to ensure Skulpt compatibility.

    Args:
        d1 (dict): The first dictionary
        d2 (dict): The second dictionary
    Returns:
        dict: The new dictionary
    """
    d3 = {}
    for key, value in d1.items():
        d3[key] = value
    for key, value in d2.items():
        d3[key] = value
    return d3


class SandboxVariable:
    def __init__(self, name, value):
        self.name = name
        self.value = value


class DataSandbox:
    """
    Simplistic Mixin class that contains the functions for accessing a
    self-contained student data namespace.
    """

    def __init__(self):
        super().__init__()
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
        """
        Retrieve a list of all the callable names in the students' namespace.
        In other words, get a list of all the functions the student defined.

        Returns:
            list of callables
        """
        return {k: v for k, v in self.data.items() if callable(v)}

    @property
    def var(self):
        return {k: SandboxVariable(k, v) for k, v in self.data.items()}

    def __repr__(self):
        return ""

class Sandbox(DataSandbox):
    """

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
        output_contexts (dict[str:list[str]]): The output for each call context.
        call_id (int): The current call_id of the most recent call. Is
            initially 0, indicating the original sandbox creation.
        modules: A dictionary of the mocked modules (accessible by their
            imported names).
        context: A list of strings representing the code previously run through
            this sandbox via .call.
        contextualize (bool): Whether or not to contextualize stack frames.
    """

    CONTEXT_MESSAGE = (
        "\n\nThe error above occurred when I ran:<br>\n<pre>{context}</pre>"
    )
    FILE_CONTEXT_MESSAGE = (
        "\n\nThe error above occurred when I ran your file: {filename}"
    )
    INPUT_CONTEXT_MESSAGE = (
        "And entered the inputs:\n```\n{inputs}\n```"
    )
    TRACER_STYLES = {
        'coverage': SandboxCoverageTracer,
        'calls': SandboxCallTracer,
        'none': SandboxBasicTracer,
    }

    def __init__(self, initial_data=None,
                 initial_raw_output=None,
                 initial_exception=None,
                 modules=None, full_traceback=False,
                 tracer_style='none',
                 threaded=False, report=None,
                 context=None, result_proxy=SandboxResult,
                 instructor_filename="instructor_tests.py",
                 allowed_functions=None):
        """
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
                implementation) or a user-created MockedModule. By default,
                we mock out the following modules:
                * matplotlib
                * pedal
            context (False, None, or list[str]): How to contextualize calls by
                default in this Sandbox. False means no contextualization.
                None (default) means contextualize automatically. If you give
                a list[str], then it assumes you want to contextualize
                automatically but starting off with the given strings.
            initial_raw_output (str): The initial printed output for the
                sandbox. Usually defaults to None to indicate a blank printed
                area.
            instructor_filename (str): The filename to display in tracebacks,
                when executing student code in instructor tests. Although you
                can specify something else, defaults to "instructor_tests.py".
        """
        super().__init__()
        if initial_data is None:
            initial_data = {}
        self.data = initial_data

        # Context
        self.call_id = 0
        self.target_contexts = {self.call_id: []}
        self.call_contexts = {self.call_id: []}
        self.input_contexts = {self.call_id: []}
        self.context = context
        self.keep_context = False
        # Update outputs
        self.set_output(initial_raw_output)
        # filename
        self.instructor_filename = instructor_filename
        # Temporary data
        self._temporaries = set()
        self._backups = {}
        # Exception
        self.exception = initial_exception
        self.exception_position = None
        self.exception_formatted = None
        self.report_exceptions_mode = False
        self.raise_exceptions_mode = False
        # Input
        self.set_input(None)
        self._input_tracker = self._track_inputs()
        # Modules
        if modules is None:
            modules = {'matplotlib': True,
                       'pedal': mocked.MockPedal()
                       }
        self.mocked_modules = {}
        self.modules = {}
        self.add_mocks(modules)
        self.mocked_functions = {
            'compile': mocked._disabled_compile,
            'eval': mocked._disabled_eval,
            'exec': mocked._disabled_exec,
            'globals': mocked._disabled_globals,
            'open': mocked._restricted_open,
            '__import__': mocked._restricted_import,
        }
        if allowed_functions is not None:
            for function_name in allowed_functions:
                if function_name in self.mocked_functions:
                    del self.mocked_functions[function_name]
        # Patching
        self._current_patches = []
        # Settings
        self.full_traceback = full_traceback
        self.MAXIMUM_VALUE_LENGTH = 120
        # Tracer Styles
        self.tracer_style = tracer_style
        # Proxying results
        self.result_proxy = result_proxy
        # report
        if report is None:
            report = MAIN_REPORT
        self.report = report
        # Threading
        self.threaded = threaded
        self.allowed_time = 3

    def _set_tracer_style(self, tracer_style):
        self._tracer_style = tracer_style.lower()
        self.trace = self.TRACER_STYLES[tracer_style.lower()]()

    def _get_tracer_style(self):
        return self._tracer_style

    tracer_style = property(_get_tracer_style, _set_tracer_style)

    def add_mocks(self, modules):
        """
        :param modules: Keyword listing of modules and their contents
                        (MockedModules) or True (if its one that we have a
                        default implementation for).
        :type modules: dict
        """
        for module_name, module_data in modules.items():
            self._add_mock(module_name, module_data)

    def _add_mock(self, module_name, module_data):
        # MatPlotLib's PyPlot
        if module_name == 'matplotlib':
            matplotlib, modules = mocked.create_module('matplotlib.pyplot')
            self.mocked_modules.update(modules)
            if module_data is True:
                mock_plt = mocked.MockPlt()
                mock_plt._add_to_module(matplotlib.pyplot)
                self.modules['matplotlib.pyplot'] = mock_plt
            else:
                module_data._add_to_module(matplotlib.pyplot)
        else:
            root, modules = mocked.create_module(module_name)
            self.mocked_modules.update(modules)
            self.modules[module_name] = module_data
            module_data._add_to_module(root)

    def set_output(self, raw_output):
        """
        Change the current printed output for the sandbox to the given value.
        If None is given, then clears all the given output (empty list for
        `output` and empty string for `raw_output`).

        Args:
            raw_output (str): The new raw_output for the sandbox. To compute
                the `output` attribute, the system splits and rstrips at
                newlines.
        """
        if raw_output is None:
            self.raw_output = ""
            self.output = []
            self.output_contexts = {self.call_id: list(self.output)}
        else:
            self.raw_output = raw_output
            lines = raw_output.rstrip().split("\n")
            self.output = [line.rstrip() for line in lines]
            self.output_contexts[self.call_id] = list(self.output)

    def append_output(self, raw_output):
        """
        Adds the string of `raw_output` to the current `raw_output` attribute.
        The added string will be split on newlines and rstripped to append
        to the `output` attribute.

        Args:
            raw_output (str): The new raw_output for the sandbox. To compute
                the `output` attribute, the system splits and rstrips at
                newlines.
        """
        self.raw_output += raw_output
        lines = raw_output.rstrip().split("\n")
        lines = [line.rstrip() for line in lines]
        if self.raw_output:
            self.output.extend(lines)
            self.output_contexts[self.call_id].extend(lines)

    def set_input(self, inputs, clear=True):
        """
        Queues the given value as the next arguments to the `input` function.
        """
        if inputs is None:
            self.inputs = []
        if clear:
            self.inputs.clear()
        if isinstance(inputs, str):
            self.inputs.append(inputs)
        elif isinstance(inputs, (list, tuple)):
            self.inputs.extend(inputs)
        elif inputs is not None:
            # TODO: intelligently handle custom generator
            self.inputs = inputs

    def _track_inputs(self):
        """
        Wraps an input function with a tracker.
        """

        def _input_tracker(*args, **kwargs):
            if args:
                prompt = args[0]
            else:
                prompt = ""
            print(prompt)
            if self.inputs:
                value_entered = self.inputs.pop(0)
            else:
                # TODO: Make this smarter, more elegant in choosing IF we should repeat 0
                value_entered = '0'
            self.input_contexts[self.call_id].append(value_entered)
            return value_entered

        return _input_tracker

    def _purge_temporaries(self):
        """
        Delete any variables in the namespace that have been made as
        temporaries. This happens automatically after you execute code.
        """
        for key in self._temporaries:
            if key in self._backups:
                self.data[key] = self.backups[key]
            else:
                del self.data[key]
        self._temporaries = set()

    def _is_long_value(self, value):
        return len(repr(value)) > 25

    def _make_temporary(self, category, name, value, context):
        """
        Create a temporary variable in the namespace for the given
        category/name. This is used to load arguments into the namespace to
        be used in function calls. Temporaries are only created if the value's
        repr length is too long, as defined by _is_long_value.

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
        """
        if isinstance(value, SandboxVariable):
            return value.name
        if not self._is_long_value(value):
            return repr(value)
        key = '_temporary_{}_{}'.format(category, name)
        if key in self.data:
            self._backups[key] = self.data[key]
        self._temporaries.add(key)
        self.data[key] = value
        if context is None:
            self.call_contexts[self.call_id].append("{} = {}".format(key, value))
        return key

    def run_file(self, filename, as_filename=None, modules=None, inputs=None,
                 threaded=None, context=None, report_exceptions=None,
                 raise_exceptions=None):
        """
        Load the given filename and execute it within the current namespace.
        
        Args:
            context (False, None, or list[str]): The context to give any
                exceptions. If None, then the recorded context will be used. If
                a string, tracebacks will be shown with the given context. If
                False, no context will be given.
        """
        if as_filename is None:
            as_filename = filename
        with open(filename, 'r') as code_file:
            code = code_file.read() + '\n'
        self.run(code, as_filename, modules, inputs, threaded,
                 context, report_exceptions, raise_exceptions)

    def list(self, *args):
        pass

    def call(self, function, *args, **kwargs):
        """
        Args:
            function (str): The name of the function to call that was defined
                by the user.
            as_filename (str): The filename to use when calling this function.
                Defaults to the instructor filename, since you are calling
                code on the student's behalf.
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
            context (False, None, or list[str]): The context to give any
                exceptions. If None, then the recorded context will be used. If
                a string, tracebacks will be shown with the given context. If
                False, no context will be given.
            keep_context (bool): Whether or not to stay in the current context,
                or to start a new one. Defaults to False.
        Returns:
            If the call was successful, returns the result of executing the
            code. Otherwise, it will return an Exception relevant to the
            failure (might be a SandboxException, might be a user-space
            exception).
        """
        # Confirm that the function_name exists
        if function not in self.functions:
            if function not in self.data:
                self.exception = SandboxHasNoVariable(
                    "The function {function} does not exist.".format(function=function)
                )
            else:
                self.exception = SandboxHasNoFunction(
                    "The variable {function} is not a function.".format(function=function)
                )
            return self.exception
        # Parse kwargs for any special arguments.
        as_filename = kwargs.pop('as_filename', self.instructor_filename)
        target = kwargs.pop('target', '_')
        modules = kwargs.pop('modules', {})
        inputs = kwargs.pop('inputs', None)
        threaded = kwargs.pop('threaded', self.threaded)
        context = kwargs.pop('context', self.context)
        keep_context = kwargs.pop('keep_context', self.keep_context)
        report_exceptions = kwargs.pop('report_exceptions', self.report_exceptions_mode)
        raise_exceptions = kwargs.pop('raise_exceptions', self.raise_exceptions_mode)
        # Create the actual arguments and call
        if not keep_context or not self.call_id:
            self.call_id += 1
            self.output_contexts[self.call_id] = []
            self.call_contexts[self.call_id] = []
            self.input_contexts[self.call_id] = []
        # Always update the target context to be most recent
        self.target_contexts[self.call_id] = target
        actual, student = self._construct_call(function, args, kwargs, target,
                                               context)
        if context is None:
            context = student
        # if context is None:
        # self.call_contexts[self.call_id].append(student_call)
        # if context is not False:
        #    self.call_contexts[self.call_id] = context
        self.run(actual, as_filename=as_filename, modules=modules,
                 inputs=inputs, threaded=threaded,
                 context=context, keep_context=keep_context,
                 report_exceptions=report_exceptions,
                 raise_exceptions=raise_exceptions)
        self._purge_temporaries()
        if self.exception is None:
            self._ = self.data[target]
            if self.result_proxy is not None:
                self._ = self.result_proxy(self._, call_id=self.call_id,
                                           sandbox=self)
            return self._
        else:
            # TODO: Might need to wrap this in case the student was supposed
            # to return an exception - weird circumstance though
            return self.exception

    def make_safe_variable(self, name):
        """
        Tries to construct a safe variable name in the current namespace, based
        off the given one. This is accomplished by appending a "_" and a number
        of increasing value until no comparable name exists in the namespace.
        This is particularly useful when you want to create a variable name to
        assign to, but you are concerned that the user might have a variable
        with that name already, which their code relies on.
        
        Args:
            name (str): A desired target name.
        Returns:
            str: A safe target name, based off the given one.
        """
        current_addition = ""
        attempt_index = 2
        while name + current_addition in self.data:
            current_addition = "_{}".format(attempt_index)
            attempt_index += 1
        return name + current_addition

    def _construct_call(self, function, args, kwargs, target, context):
        str_args = [self._make_temporary('arg', index, value, context)
                    for index, value in enumerate(args)]
        str_kwargs = ["{}={}".format(key,
                                     self._make_temporary('kwarg', key, value, context))
                      for key, value in kwargs.items()]
        arguments = ", ".join(str_args + str_kwargs)
        call = "{}({})".format(function, arguments)
        if target is None:
            actual = call
        else:
            actual = "{} = {}".format(target, call)
        student_call = call if target is "_" else actual
        return actual, student_call

    def _start_patches(self, *patches):
        self._current_patches.append(patches)
        for patch in patches:
            patch.start()

    def _stop_patches(self):
        patches = self._current_patches.pop()
        for patch in patches:
            patch.stop()

    def _capture_exception(self, exception, exc_info, report_exceptions,
                           raise_exceptions, context, keep_context,
                           as_filename="", code=""):
        self.exception = exception
        if context is not False:
            if context is None or keep_context:
                contexts = self.call_contexts[self.call_id]
                if context is not None:
                    contexts.append(context)
                context = '\n'.join(contexts)#[1:])
            if context.strip():
                context = self.CONTEXT_MESSAGE.format(context=context)
                inputs = self.input_contexts[self.call_id]
                if inputs is not None and inputs:
                    inputs = "\n".join(inputs)
                    context += "\n"+self.INPUT_CONTEXT_MESSAGE.format(inputs=inputs)
            else:
                context = self.FILE_CONTEXT_MESSAGE.format(filename=self.report['source']['filename'])
            self.exception = _add_context_to_error(self.exception, context)
        line_offset = self.report['source'].get('line_offset', 0)
        student_filename = self.report['source'].get('filename', as_filename)
        if 'lines' in self.report['source']:
            lines = self.report['source']['lines']
        else:
            lines = code.split("\n")
        traceback = SandboxTraceback(self.exception, exc_info,
                                     self.full_traceback,
                                     self.instructor_filename,
                                     line_offset, student_filename,
                                     lines)
        self.exception_position = {'line': traceback.line_number}
        self.exception_formatted = traceback.format_exception()
        self.exception_name = str(self.exception.__class__)[8:-2]
        # Do we add the exception to the report?
        if report_exceptions is False:
            return True
        if report_exceptions is None and not self.report_exceptions_mode:
            return True
        self.report.attach(self.exception_name,
                           group=self.report.group,
                           category='Runtime', tool='Sandbox',
                           mistake={'message': self.exception_formatted,
                                    'error': self.exception})
        if raise_exceptions is True:
            raise SandboxStudentCodeException(self.exception)
        return False

    def run(self, code, as_filename=None, modules=None, inputs=None,
            threaded=None, report_exceptions=True, raise_exceptions=False,
            context=False, keep_context=False):
        """
        Execute the given string of code in this sandbox.
        
        Args:
            code (str): The string of code to be executed.
            as_filename (str): The filename to use when executing the code -
                this is cosmetic, technically speaking, it has no relation
                to anything on disk. It will be present in tracebacks.
                Defaults to Source's filename.
            modules (dict[str:Module]): Modules to mock.
            inputs (list[str]): The inputs to give from STDIN, as a list of
                strings. You can also give a function that emulates the
                input function; e.g., consuming a prompt (str) and producing
                strings. This could be used to make a more interactive input
                system.
            context (str): The context to give any exceptions.
                If None, then the recorded context will be used. If a string,
                tracebacks will be shown with the given context. If False,
                no context will be given (the default).
            threaded (bool): whether or not to run this code in a separate
                thread. Defaults to :attribute:`Sandbox.threaded`.
            report_exceptions (bool): Whether or not to capture exceptions.
        """
        # Handle any threading if necessary
        if threaded is None:
            threaded = self.threaded
        if threaded:
            try:
                return timeout(self.allowed_time, self.run, code, as_filename,
                               modules, inputs, False,
                               report_exceptions, raise_exceptions,
                               context, keep_context)
            except TimeoutError as timeout_exception:
                self._capture_exception(timeout_exception, sys.exc_info(),
                                        report_exceptions, raise_exceptions,
                                        context, keep_context, as_filename,
                                        code)
                return self
        
        if as_filename is None:
            as_filename = os.path.basename(self.report['source']['filename'])
            # todo: earlier version of inputs being made?
        if inputs is not None:
            self.set_input(inputs)
        # Override builtins and mock stuff out
        mocked_functions = self.mocked_functions.copy()
        mocked_functions['input'] = self._input_tracker
        mocked_functions['raw_input'] = self._input_tracker
        mocked_functions['sys'] = sys
        mocked_functions['os'] = os
        mocked._override_builtins(self.data, mocked_functions)

        self.exception = None
        self.exception_position = None
        self.exception_formatted = None

        # Patch in dangerous built-ins
        x = sys.stdout
        capture_stdout = io.StringIO()
        self._start_patches(
            patch.dict('sys.modules', self.mocked_modules),
            patch('sys.stdout', capture_stdout),
            patch('time.sleep', return_value=None),
        )
        # TODO: Hack, add more flexibile way to specify unusable modules
        for module in list(sys.modules.keys()):
            if module.startswith('pedal.'):
                del sys.modules[module]
        try:
            compiled_code = compile(code, as_filename, 'exec')
            with self.trace._as_filename(as_filename, code):
                exec(compiled_code, self.data)
        except Exception as user_exception:
            self._stop_patches()
            info = sys.exc_info()
            self._capture_exception(user_exception, info,
                                    report_exceptions, raise_exceptions,
                                    context, keep_context, as_filename,
                                    code)
        else:
            self._stop_patches()
        finally:
            self.append_output(capture_stdout.getvalue())
        if context is None:
            self.call_contexts[self.call_id].append(code)
        elif isinstance(context, str):
            self.call_contexts[self.call_id].append(context)
        elif context is not False:
            self.call_contexts[self.call_id] = context
        return self


def run(initial_data=None, initial_raw_output=None, initial_exception=None,
        allowed_functions=None,
        modules=None, inputs=None, report_exceptions=True, raise_exceptions=False,
        context=None,
        full_traceback=False, tracer_style='none', threaded=False,
        result_proxy=SandboxResult,
        instructor_filename="instructor_tests.py",
        code=None, as_filename=None, report=None):
    if report is None:
        report = MAIN_REPORT
    if 'run' not in report['sandbox']:
        report['sandbox']['settings'] = [
            initial_data, initial_raw_output, initial_exception, modules,
            full_traceback, tracer_style, threaded, report, context,
            result_proxy, instructor_filename, allowed_functions
        ]
        report['sandbox']['run'] = Sandbox(*report['sandbox']['settings'])

    sandbox = report['sandbox']['run']
    if code is None:
        code = report['source']['code']
    sandbox.run(code, as_filename, modules, inputs, threaded,
                report_exceptions, raise_exceptions, context=context, keep_context=False)
    return sandbox


def reset(report=None):
    if report is None:
        report = MAIN_REPORT
    if 'settings' in report['sandbox']:
        report['sandbox']['run'] = Sandbox(*report['sandbox']['settings'])
    else:
        run(report=report)
