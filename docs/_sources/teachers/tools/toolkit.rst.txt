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

    from pedal.toolkit.utility import *

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