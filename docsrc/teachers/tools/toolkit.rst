Toolkit
=======


The Toolkit is composed of several collections of useful functions. They are loosely related within their
collections, but distinctive in their purpose. Some are Feedback Functions, and some are simply useful
utility functions.

Utility
-------

The biggest category of Toolkit functions is the Utility submodule. Most of the utility functions
allow you to make statements about the students' source code.

Imported as::

    from pedal.cait.find_node import *

.. function:: is_top_level(ast_node: CaitNode) -> bool

    Determines if the `ast_node` is at the top-level of the program.
    Correctly handles expression statements (so a print call on its own will be
    considered a statement, even though its technically an expression).


.. function:: no_nested_function_definitions(muted=False) -> bool

    Returns `True` if there are any functions defined inside of other functions.
    Also attaches feedback, although that can be muted.

    .. feedback_function:: pedal.toolkit.utilities.no_nested_function_definitions

.. function:: function_prints(function_name: str = None) -> bool

    Determines if there is a print statement inside of any functions. If `function_name` is given,
    then only that function will be checked.

.. function:: find_function_calls(name: str, root = None) -> List[CaitNode]

    Returns a list of CaitNodes representing all of the function calls that
    were found. This includes both methods and regular functions. You can
    filter by the given `name`.

.. function:: function_is_called(name: str) -> int

    Returns the number of times that the given function name is called.

.. function:: only_printing_variables() -> bool

    Determines whether the user is only printing variables, as opposed to
    literal values.

.. function:: find_prior_initializations(node: CaitNode) -> List[CaitNode]

    Given a Name node, returns a list of all the assignment
    statements that incorporate that Name node prior to that line. Returns
    None if no Name is given.

.. function:: prevent_unused_result(muted: bool = False) -> List[CaitNode]

    Returns a list of any function calls where the function being called
    typically has a return value that should be assigned or used in an
    expression, but was instead thrown away.

    .. feedback_function:: pedal.toolkit.utilities.prevent_unused_result

.. function:: prevent_builtin_usage(function_names: [str], muted=False) -> str:

    Determines the name of the first function in `function_names` that is
    called, or returns `None`; also attaches feedback.

    .. feedback_function:: pedal.toolkit.utilities.prevent_builtin_usage

.. function:: find_negatives(root: CaitNode = None) -> List[float]

    Returns all the occurrences of the given literal negative number in the source
    code. Can optionally filter at the given subtree.

.. function:: prevent_literal(*literals: Any, muted=False) -> False or Any

    Confirms that the literal is not in the code, returning False if it is not.
    You can use literal strings, integers, floats, booleans, and None.

    .. feedback_function:: pedal.toolkit.utilities.prevent_literal

.. function:: ensure_literal(*literals: Any, muted=False) -> False or Any

    Confirms that the literal IS in the code, returning False if it is not.
    You can use literal strings, integers, floats, booleans, and None.

    .. feedback_function:: pedal.toolkit.utilities.ensure_literal

.. function:: prevent_advanced_iteration(muted=False):

    Attaches feedback if a `while` loop is in the source code,
    or any of the built-in list handling functions are used like
    `sum`, `len`, `sorted`, etc.

.. function:: ensure_operation(op_name: str, root: CaitNode = None, muted=False) -> CaitNode

    Determines if the given operator `op_name` is used anywhere, returning the
    node of it if it is. Otherwise, returns `False`. You can specify the operator
    as a string like `"+"` or `"<<"`. Supports all comparison, boolean, binary, and unary operators.

    .. feedback_function:: pedal.toolkit.utilities.ensure_operation

.. function:: prevent_operation(op_name: str, root: CaitNode = None, muted= False) -> CaitNode

    Determines if the given operator `op_name` is NOT used anywhere, returning the
    node of it if it is. Otherwise, returns `False`. You can specify the operator
    as a string like `"+"` or `"<<"`. Supports all comparison, boolean, binary, and unary operators.

    .. feedback_function:: pedal.toolkit.utilities.prevent_operation

.. function:: find_operation(op_name: str, root: CaitNode=None) -> CaitNode

    Returns the first occurrence of the operator `op_name` in the source code.
    Otherwise returns `False`. You can specify the operator
    as a string like `"+"` or `"<<"`. Supports all comparison, boolean, binary, and unary operators.

.. function:: ensure_assignment(variable_name: str, type: str = None, value: Any = None, root:CaitNode = None, muted=False) -> bool

    Consumes a variable name and returns the first location that it is assigned to; if it is never assigned,
    then it will return `False` instead. You can also specify the variable's
    `type` and `value` too.

Functions
---------

The functions submodule contains a bunch of utilities for

.. function:: all_documented()

    Feedback Function. Determines if all the functions and classes have a  docstring.

.. function:: match_function(name: str)

    Finds the function definition with the given name.

.. function:: match_parameters(name: str, *types: Any, returns=Any, root: CaitNode = None)

    Feedback function to determine if the parameters and return type match for the given function.

.. function:: match_signature(name: str, length: int, *parameters: str):

    Feedback function to determine if the function with the given name
    has `length` number of parameters. Optionally can check that their
    names match what is given in `parameters`.

.. function:: unit_test(name: str, *tests: ...)

    Complex function for conveniently testing whether a function returns
    the expected value. Formats the output into an HTML table.
    Expects the `name` of the function as a string.

    The format of the tests is as follows: each test is a sequence of
    arguments, with the last value in the sequence representing the expected
    return value. If the last value is a tuple, it expected to have the
    output as the first element and a tip for that case as the second element.
    It intelligently handles floating point values.

    This function provides many different kinds of feedback depending on
    the mistake made in the function.

.. function:: output_test(name: str, *tests: ...)

    Complex function for conveniently testing whether a function prints
    the expected value. Formats the output into an HTML table.
    Expects the `name` of the function as a string.

    The format of the tests is as follows: each test is a sequence of
    arguments, with the last value in the sequence representing the expected
    printed output. If the last value is a tuple, it expected to have the
    output as the first element and a tip for that case as the second element.
    It supports the output being a single string

    This function provides many different kinds of feedback depending on
    the mistake made in the function.

.. function:: check_coverage()

    Checks that all the statements in the program have been executed.
    This function only works when a tracer_style has been set in the sandbox,
    or you are using an environment that automatically traces calls (e.g.,
    BlockPy).

.. function:: ensure_coverage(percentage: float = .5, destructive = False)

    Provides some feedback if the students' code has coverage below the
    given percentage.
    Note that this avoids destroying the current sandbox instance stored on the
    report, if there is one present.

.. function:: ensure_cisc108_tests(test_count)

    Provides some feedback if the student has not called the `assert_equal` library
    from the CISC108 external module a sufficient number of times.
    TODO: This should not be part of Pedal!

Files
-----

Provides some helper functions for checking constraints about files.

.. function:: files_not_handled_correctly(*filenames: str, muted=False)

    Statically detect if files have been opened and closed correctly.
    This is only useful in the case of very simplistic file handling.
    Does handle both old style explicit `open`/`close`, and also `with` style
    operations.

    .. feedback_function:: pedal.toolkit.files.open_without_arguments

Upload
------

Module for checking uploaded files to ensure that they have a certain
structure to their documentation. Built explicitly for one of our courses,
so should probably not be used.

Signatures
----------

.. function:: function_signature(function_name: str, returns: Any= None, yields: Any=None, prints: Any=None, raises: Any=None)

    A very sophisticated function for checking the signature of a function.
    Actually parses the docstring (Napoleon format) and checks that the parameters,
    returns, prints, and other sections all have the correct information.
    You can pass in strings as the types, or even use the actual types.
    TODO: Finish documenting.

Records
-------

.. function:: check_record_instance(record_instance: Any, record_type: dict, instance_identifier: str, type_identifier: str)

    A very sophisticated function that determines if a given value (`record_instance`)
    matches the given `record_type`. A record type and record instance refer to our homebrew
    typing system similar to the style used in TypeScript, whereby dictionaries can be typed.
    Provides many kinds of feedback. TODO: Finish documenting.

Printing
--------

.. function:: ensure_prints(count: int) -> False or List[CaitNode]

    Determines whether the print function is called the given `count` times,
    providing appropriate feedback if it is not. Also determines if there is a print
    function being called from outside of the toplevel (e.g., in a loop or
    function). The function returns either `False` if any of the above is
    violated, or a list of the Print calls.

Plotting
--------

Helper functions for verifying information about plots made with MatPlotLib.

.. function:: prevent_incorrect_plt()

    Provides feedback if the user incorrectly imports MatPlotLib.
    We require them to use the `import matplotlib.pyplot as plt` style.
    TODO: improve documentation

.. function:: ensure_correct_plot(function_name: str)

    Checks that the plotting function with the given name is called correctly.
    You can pass in `"plot"`, `"hist"`, or `"scatter"`.

    .. TODO:: improve documentation

.. function:: ensure_show() -> bool:

    Checks that the `show` function was called, which is required to actually
    show the graph when it is ready.

    .. TODO:: improve documentation

.. function:: check_for_plot(plt_type: str, data: Any) -> bool

    Provides feedback on whether there is a graph with the given data and type.

    .. TODO:: improve documentation

Imports
-------

Checks various kinds of imports

.. function:: ensure_imports(*modules: str) -> bool

    Feedback functions for checking whether the modules with the given name
    have been imported using any of the valid styles.

    .. TODO:: improve documentation

