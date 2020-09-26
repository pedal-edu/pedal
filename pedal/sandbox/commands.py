"""
The collection of top-level commands for the Sandbox module. Note that
most of these simply act on the current MAIN_REPORT's Sandbox instance, without
doing any logic themselves.
"""

from pedal.core.report import MAIN_REPORT
from pedal.sandbox.constants import TOOL_NAME
from pedal.sandbox.sandbox import Sandbox
from pedal.source.constants import TOOL_NAME as SOURCE_TOOL_NAME
from pedal.utilities.ast_tools import FindExecutableLines


def run(code=None, filename=None, inputs=None, threaded=None,
        after=None, before=None, report=MAIN_REPORT):
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
        report (:py:class:`pedal.core.report.Report`): The report with the
            sandbox instance.

    Returns:
        Sandbox: The sandbox instance that this was run in.
    """
    sandbox: Sandbox = report[TOOL_NAME]['sandbox']
    return sandbox.run(code=code, filename=filename, inputs=inputs,
                       threaded=threaded, after=after, before=before)


def call(function, *args, target="_", threaded=None, inputs=None,
         function_kwargs=None, args_locals=None, kwargs_locals=None,
         report=MAIN_REPORT, **kwargs):
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
        report (:py:class:`pedal.core.report.Report`): The report with the
            sandbox instance.

    Returns:
        Exception or :py:class:`~pedal.sandbox.sandbox.SandboxResult`: The
            result of calling the function will be returned, proxied behind
            a SandboxResult (which attempts to perfectly emulate that
            value). If the function call failed, the exception will be
            returned instead.
    """
    sandbox: Sandbox = report[TOOL_NAME]['sandbox']
    return sandbox.call(function, *args, target=target, threaded=threaded,
                        inputs=inputs, function_kwargs=function_kwargs,
                        args_locals=args_locals, kwargs_locals=kwargs_locals,
                        **kwargs)


def evaluate(code, target="_", threaded=None, report=MAIN_REPORT):
    """
    Evaluates the given code and assigns the result to the given target.
    Will cause an error if ``code`` is not a valid expression.

    Args:
        code (str or :py:class:`~pedal.cait.cait_node.CaitNode`):
            The code to execute. If a CaitNode, then that will be executed
            directly instead of being compiled.
        target (str): The name of the variable to assign the result to.
            Note that the result is also returned by this function.
        threaded (bool): Whether or not to run this code in a threaded
            environment, which allows for timeouts.
        report (:py:class:`pedal.core.report.Report`): The report with the
            sandbox instance.

    Returns:
        Exception or :py:class:`~pedal.sandbox.sandbox.SandboxResult`: The
            result of evaluating the code will be returned, proxied behind
            a SandboxResult (which attempts to perfectly emulate that
            value). If the function call failed, the exception will be
            returned instead.
    """
    sandbox: Sandbox = report[TOOL_NAME]['sandbox']
    return sandbox.evaluate(code, target=target, threaded=threaded)


def clear_input(report=MAIN_REPORT):
    """ Removes any existing inputs set up for the sandbox. """
    sandbox: Sandbox = report[TOOL_NAME]['sandbox']
    sandbox.clear_input()


def queue_input(*inputs, report=MAIN_REPORT):
    """
    Adds the given ``*inputs`` to be used as input during subsequent
        executions (e.g., :py:func:`pedal.sandbox.commands.run`) if the
        student's code calls :py:func:`input`. This does not remove existing
        inputs.

    Args:
        *inputs (str): One or more strings that will be set. The first string
            passed in is the first string that will be passed in as input.
        report (:py:class:`pedal.core.report.Report`): The report with the
            sandbox instance.
    """
    sandbox: Sandbox = report[TOOL_NAME]['sandbox']
    sandbox.set_input(inputs, clear=False)


def set_input(inputs, clear=True, report=MAIN_REPORT):
    """
    Sets the given ``inputs`` to be used as input during subsequent
        executions (e.g., :py:func:`pedal.sandbox.commands.run`) if the
        student's code calls :py:func:`input`. Unless the ``clear`` parameter
        is set to False, this removes existing inputs.

    Args:
        inputs (str or list[str]): One or more strings that will be set. The
            first string passed in is the first string that will be passed in
            as input.
        clear (bool): Whether or not to remove any existing inputs set up
            in the sandbox.
        report (:py:class:`pedal.core.report.Report`): The report with the
            sandbox instance.
    """
    sandbox: Sandbox = report[TOOL_NAME]['sandbox']
    sandbox.set_input(inputs, clear=clear)


def get_input(report=MAIN_REPORT):
    """
    Retrieves the current inputs that are available for execution.

    Args:
        report (:py:class:`pedal.core.report.Report`): The report with the
            sandbox instance.

    Returns:
        list[str]: The current list of inputs available for execution. The first
            element of this list is the next string that will be passed to the
            next student call of :py:func:`input`.
    """
    sandbox: Sandbox = report[TOOL_NAME]['sandbox']
    return sandbox.inputs


def clear_output(report=MAIN_REPORT):
    """ Removes any existing outputs associated with the sandbox. """
    sandbox: Sandbox = report[TOOL_NAME]['sandbox']
    sandbox.clear_output()


def get_output(report=MAIN_REPORT):
    """ Retrieves the current output (whatever the student has printed) since
    execution began. """
    sandbox: Sandbox = report[TOOL_NAME]['sandbox']
    return sandbox.output


def get_exception(report=MAIN_REPORT):
    """ Returns an exception if one occurred during the last execution,
    otherwise returns None. """
    sandbox: Sandbox = report[TOOL_NAME]['sandbox']
    return sandbox.exception


def clear_student_data(report=MAIN_REPORT):
    """ Removes any data in the student namespace. """
    sandbox: Sandbox = report[TOOL_NAME]['sandbox']
    sandbox.clear_data()


def get_student_data(report=MAIN_REPORT):
    """
    Retrieves the current data in the student namespace. Note that this is
    the data itself - modifying the dictionary will modify the data in the
    students' namespace for subsequent executions!

    Args:
        report (:py:class:`pedal.core.report.Report`): The report with the
            sandbox instance.

    Returns:
        dict[str, Any]: The student's data namespace, mapping names to the
            values themselves.
    """
    sandbox: Sandbox = report[TOOL_NAME]['sandbox']
    return sandbox.data


def get_sandbox(report=MAIN_REPORT):
    """
    Retrieves the current sandbox instance attached to this report.
    Typically, this is used to retrieve the sandbox without running the
    students' code.

    Args:
        report (:py:class:`pedal.core.report.Report`): The report with the
            sandbox instance.

    Returns:
        :py:class:`pedal.sandbox.Sandbox`: The sandbox instance.
    """
    return report[TOOL_NAME]['sandbox']


def clear_sandbox(report=MAIN_REPORT):
    """ Removes any existing data within the current sandbox instance. """
    sandbox: Sandbox = report[TOOL_NAME]['sandbox']
    sandbox.clear()


def get_trace(report=MAIN_REPORT):
    """
    Retrieves the set of line that have been traced (recognized as executed).

    Args:
        report (:py:class:`pedal.core.report.Report`): The report with the
            sandbox instance.

    Returns:
        set[int]: The set of lines that have been executed in the student's
            code.
    """
    sandbox: Sandbox = report[TOOL_NAME]['sandbox']
    return sandbox.trace.lines - sandbox.trace.missing


def start_trace(report=MAIN_REPORT):
    """ Start tracing using the coverage module. """
    sandbox: Sandbox = report[TOOL_NAME]['sandbox']
    sandbox.tracer_style = 'coverage'


def stop_trace(report=MAIN_REPORT):
    """ Stop whatever tracing is going on. """
    sandbox: Sandbox = report[TOOL_NAME]['sandbox']
    sandbox.clear_tracer()


def check_coverage(report=MAIN_REPORT):
    """
    Checks that all the statements in the program have been executed.
    This function only works when a tracer_style has been set in the sandbox,
    or you are using an environment that automatically traces calls (e.g.,
    BlockPy).

    Args:
        report (Report): The Report to draw source code from; if not given,
            defaults to MAIN_REPORT.
    Returns:
        set[int]: If the source file was not parsed, None is returned.
            Otherwise, returnes the set of unexecuted lines.
        float: The ratio of unexected to total executable lines.
    """
    if not report[SOURCE_TOOL_NAME]['success']:
        return None, 0
    lines_executed = set(get_trace())
    # TODO: Why... does -1 get returned sometimes?
    if -1 in lines_executed:
        lines_executed.remove(-1)
    student_ast = report[SOURCE_TOOL_NAME]['ast']
    visitor = FindExecutableLines()
    visitor.visit(student_ast)
    lines_in_code = set(visitor.lines)
    unexecuted_lines = lines_in_code - lines_executed
    if lines_in_code:
        coverage_ratio = len(lines_executed)/len(lines_in_code)
    else:
        coverage_ratio = 0
    return unexecuted_lines, coverage_ratio


def clear_mocks(report=MAIN_REPORT):
    """ Reset mocked modules and functions to their defaults. """
    sandbox: Sandbox = report[TOOL_NAME]['sandbox']
    sandbox.clear_mocks()


def mock_function(function_name, new_version, report=MAIN_REPORT):
    """ Provide a custom version of the built-in function. """
    sandbox: Sandbox = report[TOOL_NAME]['sandbox']
    sandbox.mock_function(function_name, new_version)


def allow_function(function_name, report=MAIN_REPORT):
    """ Explicitly allow students to use the given function. """
    sandbox: Sandbox = report[TOOL_NAME]['sandbox']
    sandbox.allow_function(function_name)


def block_function(function_name, report=MAIN_REPORT):
    """ Cause an error if students call the given function. """
    sandbox: Sandbox = report[TOOL_NAME]['sandbox']
    sandbox.block_function(function_name)


def allow_module(module_name, report=MAIN_REPORT):
    """ Explicitly allow students to use the given module. """
    sandbox: Sandbox = report[TOOL_NAME]['sandbox']
    sandbox.allow_module(module_name)


def mock_module(module_name, new_version, friendly_name=None, report=MAIN_REPORT):
    """
    Provide an alternative version of the given module.

    Args:
        module_name (str): The importable name of the module.
        new_version (dict | :py:class:`pedal.sandbox.mocked.MockModule`): The
            new version of the module, either as a dictionary of fields/values
            or a fully created MockModule.
        friendly_name (str): The internal name to use to store the data for this
            module, accessible via Sandbox's `modules` field.
        report (:py:class:`pedal.core.report.Report`): The report with the
            sandbox instance.
    """
    sandbox: Sandbox = report[TOOL_NAME]['sandbox']
    sandbox.mock_module(module_name, new_version, friendly_name=friendly_name)


def block_module(module_name, report=MAIN_REPORT):
    """ Cause an error if students use the given module. """
    sandbox: Sandbox = report[TOOL_NAME]['sandbox']
    sandbox.block_module(module_name)


class CommandBlock:
    """
    Context Manager for creating instructor blocks of code that will
    be shown together to the student.

    TODO: What about named points where you can "rewind" the state to?
    """

    sandbox: Sandbox

    def __init__(self, report=MAIN_REPORT):
        self.sandbox = report[TOOL_NAME]['sandbox']

    def __enter__(self):
        self.sandbox.start_grouping_context()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sandbox.stop_grouping_context()


# TODO: Deprecate these!
reset_output = clear_output
