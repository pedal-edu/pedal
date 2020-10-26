"""
File containing the Sandbox class.

TODO: Handle sys.argv

"""

import sys
import io
from itertools import zip_longest
from unittest.mock import patch

from pedal.core.feedback_category import FeedbackCategory
from pedal.core.report import MAIN_REPORT
from pedal.utilities.exceptions import ExpandedTraceback, improve_builtin_exceptions
from pedal.sandbox.data import SandboxVariable, SandboxContextKind, \
    SandboxContext, SandboxModules
from pedal.sandbox import mocked
from pedal.sandbox.constants import TOOL_NAME
from pedal.sandbox.feedbacks import runtime_error, EXCEPTION_FF_MAP
from pedal.sandbox.exceptions import SandboxHasNoFunction, SandboxHasNoVariable
from pedal.sandbox.timeout import timeout
from pedal.sandbox.result import SandboxResult
from pedal.sandbox.tracer import TRACER_STYLES


class Sandbox:
    """
    Args:
        report (:py:class:`~pedal.core.report.Report`): The report that this
            Sandbox is attached to.

    Attributes:
        data (dict[str, Any]): The namespace that the context are occurring in.
            Note that this is mutable.
        result: TODO
        output (list[str]): The list of strings that have been printed to the
            console by :py:func:`print`. Note that line endings have been removed
            using :py:func:`string.rstrip`.
        inputs (list[str]): The list of strings that will be passed to
            :py:func:`input`.
        raw_output (str): A concatenated string of all the text that was printed
            to console. No changes have been made to the text.
        exception (Exception or None): The exception that occurred during the
            most recent execution, or None if nothing happened.
        feedback: TODO
        modules.plots: TODO
        modules.turtles: TODO
        target: TODO
        allowed_time (int): How long to allow before stopping execution.
        tracer_style (str): TODO
        _context (list[SandboxContext]): The history of executions made in
            this sandbox.
        _next_context_id (int): The ID of the next execution context.
        _current_patches (list[Patch]): A stack of patches that are currently
            being used. This allows recursive patching behavior.
        MAXIMUM_TEMPORARY_LENGTH (int): How long to allow arguments to be before
            turning them into temporary variables.
    """

    MAXIMUM_TEMPORARY_LENGTH = 25

    def __init__(self, report=MAIN_REPORT):
        self.report = report
        # Namespace
        self.data = {}
        self.result = None
        self.exception = None
        self.feedback = None
        # Contextualization
        self._context = []
        self._current_context = None
        self._next_context_id = 0
        self._context_group_start = []
        # Patching
        self._current_patches = []
        self._current_stdout = []
        # Temporary Variables
        self._temporary_variables = set()
        self._backup_variables = {}
        # Modules
        self._module_overrides = {}
        self.modules = SandboxModules()
        self.clear_mocks()
        self.clear_data()
        # Inputs
        self.inputs = []
        # Outputs
        self.raw_output = ""
        self.output = []
        # Target
        self.target = None

        # Proxying results
        self.result_proxy_class = SandboxResult
        # Show the full traceback
        self.full_traceback = False
        # Use threading?
        self.threaded = False
        self.allowed_time = 3
        # Tracer Styles
        self.tracer_style = 'none'

    ############################################################################
    # Execution (run/call/eval)

    def _execute_with_timeout(self, code, filename, kind):
        """
        Execute the given code, but stop after `self.allowed_time`.
        Args:
            code (str):
            filename (str):
            kind (:py:class:`pedal.sandbox.sandbox_mixins.SandboxContextKind`):

        Returns:
            :py:class:`pedal.sandbox.sandbox.Sandbox`
        """
        try:
            return timeout(self.allowed_time, self._execute,
                           code, filename, kind, False)
        except TimeoutError as timeout_exception:
            self._stop_patches()
            self._capture_exception(timeout_exception, sys.exc_info(),
                                    code, filename)
            return self

    def _execute(self, code, filename, kind, threaded, **meta):
        # Handle any threading if necessary
        if threaded:
            return self._execute_with_timeout(code, filename, kind)

        self.clear_exception()
        context = SandboxContext(self._next_context_id, code, filename, kind,
                                 self.target, [], "",
                                 self.exception, self.report.submission, **meta)
        self._context.append(context)

        # Patch in dangerous built-ins
        # Override builtins and mock stuff out
        self._start_mocking(context)
        try:
            # TODO: Support CaitNode and Ast (needs skulpt to support compile better)
            compiled_code = compile(code, filename, 'exec')
            with self.trace.as_filename(filename, code):
                exec(compiled_code, self.data)
        except Exception as user_exception:
            self._stop_mocking(context)
            self._capture_exception(user_exception, sys.exc_info(),
                                    code, filename)
        else:
            self._stop_mocking(context)

        self._next_context_id += 1
        return self

    def run(self, code=None, filename=None, inputs=None, threaded=None,
            after=None, before=None):
        """
        If both ``code`` and ``filename`` are None, then the submission's
        main file will be executed. If ``code`` is given but ``filename`` is
        not, then it is assumed to be instructor code.

        Args:
            code (str or :py:class:`~pedal.cait.cait_node.CaitNode` or None):
                The code to execute.
            filename (str or None): The filename to use for this code.
            inputs (list[str]): Optional inputs to be passed to
                :py:func:`~pedal.sandbox.Sandbox.set_input`.
            threaded (bool): Whether or not to run this code in a threaded
                environment, which allows for timeouts.
            after (str): Code to run after this code (without a filename).
            before (str): Code to run before this code (without a filename).


        Returns:
            Sandbox: This sandbox instance.
        """
        if threaded is None:
            threaded = self.threaded
        if code is None:
            if filename is None:
                filename = self.report.submission.main_file
            code = self.report.submission.files[filename]
        elif filename is None:
            filename = self.report.submission.instructor_file
        if inputs is not None:
            self.set_input(inputs)
        if before is not None:
            self._execute(before, filename, SandboxContextKind.RUN, threaded)
        self.target = None
        self._execute(code, filename, SandboxContextKind.RUN, threaded)
        if after is not None:
            self._execute(after, filename, SandboxContextKind.RUN, threaded)
        return self

    def call(self, function, *args, target="_", threaded=None,
             inputs=None, function_kwargs=None,
             args_locals=None, kwargs_locals=None, **kwargs):
        """
        Execute the given function from the student's namespace.

        The ``args_locals`` and ``kwargs_locals`` values allow you to
        use student's local variables as arguments, instead of literal values.
        They actually support any arbitrary Python code, it will be injected
        without modification.

        Args:
            function (str): The name of the function to call.
            *args (Any): Any number of positional arguments to be passed to
                the called function.
            target (str): The variable to assign the result of this call to.
                Defaults to ``"_"``.
            threaded (bool): Whether or not to run this code in a threaded
                environment, which allows for timeouts.
            inputs (str or list[str]):
            function_kwargs (dict[str, Any]): Additional keyword arguments
                that could not be passed in directly via ``**kwargs`` (perhaps
                because they conflict with an existing parameter like
                ``target``).
            args_locals (list[str]): A list of names (or any valid Python
                expression) that will be passed as positional arguments to
                the function (as opposed to actual values). If any value is
                None (or if the list is too short), then the corresponding
                position argument from ``*args`` will be used instead.
            kwargs_locals (dict[str, str]): A dictionary of keyword argument
                names mapped to local names (or any valid Python expression),
                that will be used as keyword parameters similar to
                ``args_locals``.
            **kwargs (): Additional keyword arguments passed to the called
                function.

        Returns:
            Exception or :py:class:`~pedal.sandbox.sandbox.SandboxResult`: The
                result of calling the function will be returned, proxied behind
                a SandboxResult (which attempts to perfectly emulate that
                value). If the function call failed, the exception will be
                returned instead.
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
        # Handle convenience setup
        if inputs is not None:
            self.set_input(inputs)
        if function_kwargs is not None:
            kwargs.update(function_kwargs)
        if args_locals is None:
            args_locals = []
        if kwargs_locals is None:
            kwargs_locals = []
        # Make the call and evaluate it
        self.target = target
        actual, student, arguments = self._construct_call(function, args, kwargs,
                                                          args_locals, kwargs_locals,
                                                          target)
        context_id = self._next_context_id
        self._execute(actual, self.report.submission.instructor_file,
                      SandboxContextKind.CALL, threaded=threaded,
                      called=function, args=arguments)
        self._purge_temporaries()
        return self._handle_result(target, context_id)

    def evaluate(self, code, target="_", threaded=None):
        """
        Evaluates the given code and assigns the result to the given target.
        Will cause an error if ``code`` is not a valid expression.

        # TODO: Clean up syntax error.

        Args:
            code (str or :py:class:`~pedal.cait.cait_node.CaitNode`):
                The code to execute. If a CaitNode, then that will be executed
                directly instead of being compiled.
            target (str): The name of the variable to assign the result to.
                Note that the result is also returned by this function.
            threaded (bool): Whether or not to run this code in a threaded
                environment, which allows for timeouts.

        Returns:
            Exception or :py:class:`~pedal.sandbox.sandbox.SandboxResult`: The
                result of evaluating the code will be returned, proxied behind
                a SandboxResult (which attempts to perfectly emulate that
                value). If the function call failed, the exception will be
                returned instead.
        """
        self.target = target
        code = f"{target} = {code}"
        context_id = self._next_context_id
        self._execute(code, self.report.submission.instructor_file,
                      SandboxContextKind.EVAL, threaded=threaded)
        return self._handle_result(target, context_id)

    def _handle_result(self, target, context_id):
        """ Determine the appropriate return value (either an exception or the
        value stored in target. Also updates self.result. """
        if self.exception is None:
            self.result = self.data[target]
            if self.result_proxy_class is not None:
                self.result = self.result_proxy_class(self.result,
                                                      context_id=context_id,
                                                      sandbox=self)
            return self.result
        else:
            if self.result_proxy_class is not None:
                self.exception = self.result_proxy_class(self.exception,
                                                         context_id=context_id,
                                                         sandbox=self)
            return self.exception

    ############################################################################
    # Context (history of executions)

    def get_context(self, context_id: int = None):
        """
        Retrieve the most recent contexts.

        Returns:
            list[:py:class:`pedal.sandbox.sandbox_mixins.SandboxContext`]: The
                most recent execution, or executions if currently in a group.

        """
        # TODO: Test off-by-one-errors
        if context_id is None:
            if not self._context_group_start:
                return self._context[-1:]
            else:
                return self._context[self._context_group_start[-1]:]
        else:
            if not self._context_group_start:
                return [self._context[context_id]]
            else:
                for past_context_group_starts in self._context_group_start[::-1]:
                    if past_context_group_starts < context_id+1:
                        return self._context[past_context_group_starts:context_id+1]
                return self._context[:context_id+1]

    def _guess_context(self, target_name):
        """
        Tries to figure out the best context for the given target_name, by
        first checking whether the target was ever used in a CALL or EVAL.
        If it fails to find it, then it uses the most recent RUN. Otherwise,
        it just just returns None.

        Returns:
            :py:class:`pedal.sandbox.data.SandboxContext` or None: The found
                context, or None.
        """
        # Was it a target for a CALL or EVAL?
        for context in self._context[::-1]:
            if context.kind in (SandboxContextKind.EVAL, SandboxContextKind.CALL):
                if context.target == target_name:
                    return context
        # Just get the last run
        for context in self._context[::-1]:
            if context.kind == SandboxContextKind.RUN:
                return context
        # Okay just give up
        return None

    def start_grouping_context(self):
        """ Any subsequent executions will be grouped. """
        self._context_group_start.append(self._next_context_id)

    def stop_grouping_context(self):
        """ Stop grouping subsequent executions. """
        self._context_group_start.pop()

    def clear_context(self):
        """ Removes the history of any previous executions. """
        self._context_group_start.clear()
        self._context.clear()

    ############################################################################
    # Tracing
    def _set_tracer_style(self, tracer_style):
        if tracer_style is None:
            tracer_style = 'none'
        self._tracer_style = tracer_style.lower()
        self.trace = TRACER_STYLES[tracer_style.lower()]()

    def _get_tracer_style(self):
        return self._tracer_style

    tracer_style = property(_get_tracer_style, _set_tracer_style)

    def clear_tracer(self):
        """ Stop tracing in this sandbox. """
        self.tracer_style = 'none'

    ############################################################################
    # Exception Handling

    def _capture_exception(self, exception, exc_info, code, filename):
        self.exception = improve_builtin_exceptions(exception)
        # Load in any extra data
        context = self.get_context()
        line_offsets = {}
        show_filenames = {filename} - {self.report.submission.instructor_file}
        hide_filenames = {filename}
        files = self.report.submission.get_files_lines()
        if filename not in files:
            files[filename] = code.split("\n")
        if self.report.submission is not None:
            lines = self.report.submission.get_lines()
            show_filenames.update(self.report.submission.files.keys())
            line_offsets = self.report.submission.line_offsets
        else:
            lines = code.split("\n")
        # Create a better traceback
        traceback = ExpandedTraceback(self.exception, exc_info,
                                      self.full_traceback,
                                      hide_filenames,
                                      line_offsets,
                                      show_filenames,
                                      lines, files)
        if filename == self.report.submission.instructor_file:
            priority = FeedbackCategory.SPECIFICATION
        else:
            priority = FeedbackCategory.RUNTIME

        runtime_error_function = EXCEPTION_FF_MAP.get(type(self.exception),
                                                      runtime_error)
        self.feedback = runtime_error_function(exception=self.exception, context=[context],
                                               traceback=traceback, location=traceback.line_number,
                                               report=self.report, priority=priority)
        return False

    def clear_exception(self):
        """ Removes the latest exception information """
        self.exception = None
        self.feedback = None

    ############################################################################
    # Patching and Mocking

    def _start_mocking(self, context: SandboxContext):
        """ Mock input, output, builtins, and modules """
        # Handle input tracking
        self.mock_function('input', self._track_inputs(context.inputs))
        # Override builtin functions
        self.reset_builtins()
        builtins = self._module_overrides.pop('__builtins__', {})
        for name, value in builtins.items():
            if value is True:
                self.data['__builtins__'][name] = mocked.ORIGINAL_BUILTINS[name]
                self.data[name] = mocked.ORIGINAL_BUILTINS[name]
            elif value is False:
                self.data['__builtins__'][name] = mocked.disabled_builtin(name)
                self.data[name] = mocked.disabled_builtin(name)
            else:
                self.data['__builtins__'][name] = value
                self.data[name] = value
        # Override sys modules
        overridden_modules = sys.modules.copy()
        for name, value in self._module_overrides.items():
            if value is not True:
                overridden_modules[name] = value
        self._module_overrides['__builtins__'] = builtins
        # And do the patches
        self._current_stdout.append(io.StringIO())
        self._start_patches(
            patch.dict('sys.modules', overridden_modules),
            patch('sys.stdout', self._current_stdout[-1]),
            patch('time.sleep', return_value=None),
        )

    def _stop_mocking(self, context: SandboxContext):
        """ Turn off any patches, store output """
        self._stop_patches()
        current_stdout = self._current_stdout.pop()
        self.append_output(current_stdout.getvalue(), context)

    # Patching Functionality
    def _start_patches(self, *patches):
        """ Helper function to start and keep track of multiple patches """
        self._current_patches.append(patches)
        for a_patch in patches:
            a_patch.start()

    def _stop_patches(self):
        """ Helper function to end any tracked patches """
        if not self._current_patches:
            return
        patches = self._current_patches.pop()
        for a_patch in patches:
            a_patch.stop()

    def clear_mocks(self):
        """ Removes any module or builtin overrides currently in effect. """
        self._module_overrides.clear()
        self.modules.clear()
        self.reset_default_overrides()

    def reset_default_overrides(self):
        """
        Resets the list of blocked functions and modules to its starting
        state. This blocks ``compile``, ``eval``, ``exec``, ``globals``,
        and provides mocked versions of ``open`` and ``import`` that are
        more restricted. It also blocks the ``pedal`` module.
        """
        self._module_overrides['__builtins__'] = {}
        self.block_function('compile')
        self.block_function('eval')
        self.block_function('exec')
        self.block_function('globals')
        self.mock_function('open', mocked._restricted_open)
        self.mock_function('__import__', mocked._restricted_import)
        # TODO: This breaks coverage for some reason; it's a builtin?
        self.block_module('pedal')
        self.mock_module('turtle', mocked.MockTurtle(), 'turtles')
        self.mock_module('matplotlib.pyplot', mocked.MockPlt(), 'plotting')

    def mock_function(self, function_name, new_version):
        self._module_overrides['__builtins__'][function_name] = new_version

    def allow_function(self, function_name):
        self._module_overrides['__builtins__'][function_name] = True

    def block_function(self, function_name):
        self._module_overrides['__builtins__'][function_name] = False

    def allow_module(self, module_name):
        """

        Args:
            module_name (str):

        Returns:

        """
        self._module_overrides[module_name] = True
        return self

    def mock_module(self, module_name, new_version, friendly_name=None):
        """ Create a mocked version of this module. """
        if friendly_name is None:
            friendly_name = module_name
        mocked_modules = self.modules.new_module(new_version, module_name, friendly_name)
        for name, mocked_version in mocked_modules.items():
            if name not in self._module_overrides or not self._module_overrides[name]:
                self._module_overrides[name] = mocked_version
        return self

    def block_module(self, module_name):
        """
        Prevent the module from being loaded in student code.

        Args:
            module_name (str): The name of the module to prevent, as it would
                be used by import (e.g., ``"matplotlib.pyplot"``).

        Returns:
            Sandbox: This sandbox.
        """
        self._module_overrides[module_name] = mocked.BlockedModule(module_name)
        return self

    ############################################################################
    # Code generation

    def _construct_call(self, function, args, kwargs, args_locals, kwargs_locals,
                        target):
        """ Turn the given strings into an actual function call string. """
        str_args = [arg_name if arg_name is not None else
                    self._make_temporary('arg', str(index), arg_value)
                    for index, (arg_value, arg_name)
                    in enumerate(zip_longest(args, args_locals))]
        str_kwargs = ["{}={}".format(key,
                                     self._make_temporary('kwarg', key, value))
                      if key not in kwargs_locals else
                      kwargs_locals[key]
                      for key, value in kwargs.items()]
        arguments = ", ".join(str_args + str_kwargs)
        call = f"{function}({arguments})"
        if target is None:
            actual = call
        else:
            actual = f"{target} = {call}"
        student_call = call if target == "_" else actual
        return actual, student_call, arguments

    def _purge_temporaries(self):
        """
        Delete any variables in the namespace that have been made as
        temporaries. This happens automatically after you execute code.
        """
        for key in self._temporary_variables:
            if key in self._backup_variables:
                self.data[key] = self._backup_variables[key]
            else:
                del self.data[key]
        self._temporary_variables.clear()

    def _make_temporary(self, category, name, value):
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
        if len(repr(value)) <= self.MAXIMUM_TEMPORARY_LENGTH:
            return repr(value)
        key = '_temporary_{}_{}'.format(category, name)
        if key in self.data:
            self._backup_variables[key] = self.data[key]
        self._temporary_variables.add(key)
        self.data[key] = value
        return key

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


    ############################################################################
    # Data Namespace Management

    def clear_data(self):
        # Temporary data
        self.data.clear()
        self._temporary_variables.clear()
        self._backup_variables.clear()
        self.reset_builtins()

    def reset_builtins(self):
        self.data['__builtins__'] = {}
        for name, value in mocked._default_builtins.items():
            self.data['__builtins__'][name] = value

    def set_student_data(self, new_data):
        """
        Overwrites the existing student data with the keys and values from
        the ``new_data``. This copies the data over, but does not modify the
        reference to ``data``'s dictionary.

        Args:
            new_data (dict[str, Any]): The new data.

        Returns:

        """
        self.clear_data()
        for key, value in new_data.items():
            self.data[key] = value

    def get_names_by_type(self, type, exclude_builtins=True):
        """

        Args:
            type:
            exclude_builtins:

        Returns:

        """
        result = []
        for name, value in self.data.items():
            if isinstance(value, type):
                if exclude_builtins and name.startswith('__'):
                    continue
                result.append(name)
        return result

    def get_values_by_type(self, type, exclude_builtins=True):
        """

        Args:
            type:
            exclude_builtins:

        Returns:

        """
        names = self.get_names_by_type(type, exclude_builtins)
        return [self.data[name] for name in names]

    def get_variables_by_type(self, type, exclude_builtins=True):
        """

        Args:
            type:
            exclude_builtins:

        Returns:

        """
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
        """

        Returns:

        """
        return {k: SandboxVariable(k, v) for k, v in self.data.items()}

    def __getitem__(self, item):
        value, exception = None, None
        try:
            value = self.data[item]
        except KeyError:
            exception = NameError(f"NameError: name '{item}' is not defined")
        filename = self.report.submission.instructor_file
        context_id = self._next_context_id
        best_context = self._guess_context(item)
        if best_context is None:
            context = SandboxContext(context_id, str(item), filename,
                                     SandboxContextKind.GETITEM, item, [], "",
                                     exception, self.report.submission)
        else:
            context = best_context.clone(context_id)
            context.target = str(item)
            context.exception = exception
        self._context.append(context)
        self._next_context_id += 1

        if self.result_proxy_class is not None:
            return self.result_proxy_class(value, context_id=context_id,
                                           sandbox=self)
        return value

    ############################################################################
    # Useful Dunders

    #def __repr__(self):
    #    return "Sandbox({})".format()

    def __str__(self):
        return "Sandbox(contexts={context_count})".format(context_count=len(self._context))

    ############################################################################
    # Input Handling

    def clear_input(self):
        """ Removes any inputs queued. """
        self.set_input(None)
        return self

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
            self.inputs = inputs
        return self

    def _track_inputs(self, context_inputs):
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
            self._context[-1].inputs.append(value_entered)
            #context_inputs.append(value_entered)
            return value_entered

        return _input_tracker

    ############################################################################
    # Output Handling

    def clear_output(self):
        """ Remove any output currently attached to this sandbox. """
        # Update outputs
        self.raw_output = ""
        self.output.clear()
        return self

    def append_output(self, raw_output, context):
        """
        Adds the string of `raw_output` to the current `raw_output` attribute.
        The added string will be split on newlines and rstripped to append
        to the `output` attribute.

        Args:
            raw_output (str): The new raw_output for the sandbox. To compute
                the `output` attribute, the system splits and rstrips at
                newlines.
            context (:py:class:`pedal.sandbox.data.SandboxContext`): The
                currently executing context, where this output will be recorded.
        """
        self.raw_output += raw_output
        context.output = raw_output
        if self.raw_output:
            lines = raw_output.rstrip().split("\n")
            lines = [line.rstrip() for line in lines]
            self.output.extend(lines)

    def clear(self):
        """ Removes any existing data in this sandbox. """
        self.clear_data()
        self.clear_context()
        self.clear_mocks()
        self.clear_exception()
        self.clear_input()
        self.clear_output()
        self.clear_tracer()
