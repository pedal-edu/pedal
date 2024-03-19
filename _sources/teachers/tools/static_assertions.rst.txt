Static Assertions
-----------------

.. function:: prevent_function_call(function_name: str, at_most=0, root=None) -> Feedback

    Confirms that the function is not called, generating Feedback if it is.
    This is a very simple check, simply looking for any ``function_name`` calls inside the
    code. It does not check if the function is actually called at runtime, or
    if that code is reachable!

    If ``at_most`` is provided, allows them to call the function at most that many times.
    If a ``root`` is provided, allows you to start the search from a specific node.

    ::

        # Student will not be able to call the function "hello_world"
        prevent_function_call("hello_world")
        # Students can't call "hello_world" more than twice
        prevent_function_call("hello_world", at_most=2)
        # Students can't call the function "add"
        prevent_function_call("add")

    .. feedback_function:: pedal.assertions.static.prevent_function_call

.. function:: ensure_function_call(function_name: str, at_least=0, root=None) -> Feedback

    Confirms that the function IS called, generating feedback if it is not.
    This is a very simple check, simply looking for any ``function_name`` calls inside the
    code. It does not check if the function is actually called at runtime, or
    if that code is reachable!

    If ``at_least`` is provided, requires they call the function at least that many times.
    If a ``root`` is provided, allows you to start the search from a specific node.

    ::

        # Student must call the function "hello_world"
        ensure_function_call("hello_world")
        # Students must call "hello_world" at least twice
        ensure_function_call("hello_world", at_least=2)
        # Students must call the function "add"
        ensure_function_call("add")

    .. feedback_function:: pedal.assertions.static.ensure_function_call

.. function:: prevent_operation(operation: str, at_most=0, root=None) -> Feedback
              prevent_operator(operation: str, at_most=0, root=None) -> Feedback

    Confirms that the operation is not in the code, generating Feedback if it is.
    This is a very simple check, simply looking for any ``operation`` calls inside the
    code. It does not check if the operation is actually called at runtime, or
    if that code is reachable!

    The ``operation`` should be provided as a string like ``"+"`` or `"<<"``. All
    comparison, boolean, binary, and unary operations are supported.

    If ``at_most`` is provided, allows them to use the operation at most that many times.
    If a ``root`` is provided, allows you to start the search from a specific node.

    ::

        # Student will not be able to use the addition operator
        prevent_operation("+")
        # Students can't use multiplication more than twice
        prevent_operation("*", at_most=2)
        # Students can't use the bitwise invert operator
        prevent_operation("~")

    .. feedback_function:: pedal.assertions.static.prevent_operation

.. function:: ensure_operation(operation: str, at_least=0, root=None) -> Feedback
              ensure_operator(operation: str, at_least=0, root=None) -> Feedback

    Confirms that the operation IS in the code, generating feedback if it is not.
    This is a very simple check, simply looking for any ``operation`` calls inside the
    code. It does not check if the operation is actually called at runtime, or
    if that code is reachable!

    The ``operation`` should be provided as a string like ``"+"`` or `"<<"``. All
    comparison, boolean, binary, and unary operations are supported.

    If ``at_least`` is provided, requires they use the operation at least that many times.
    If a ``root`` is provided, allows you to start the search from a specific node.

    ::

        # Student must use the addition operator
        ensure_operation("+")
        # Students must use multiplication at least twice
        ensure_operation("*", at_least=2)
        # Students must use the bitwise invert operator
        ensure_operation("~")

    .. feedback_function:: pedal.assertions.static.ensure_operation

.. function:: prevent_literal(literal: Any, at_most=0, root=None) -> Feedback

    Confirms that the literal is not in the code, generating Feedback if it is.
    You can use literal any values including strings, integers, floats, booleans,
    lists, sets, tuples, dictionaries, and None.

    If ``at_most`` is provided, allows them to use the literal at most that many times.
    If a ``root`` is provided, allows you to start the search from a specific node.

    ::

        # Student will not be able to embed the literal 5
        prevent_literal(5)
        # Students can't use 5 more than twice
        prevent_literal(5, at_most=2)
        # Students can't use the string "hello"
        prevent_literal("hello")

    .. feedback_function:: pedal.assertions.static.prevent_literal

.. function:: ensure_literal(literal: Any) -> Feedback

    Confirms that the literal IS in the code, generating feedback if it is.
    You can use literal any values including strings, integers, floats, booleans,
    lists, sets, tuples, dictionaries, and None.

    If ``at_least`` is provided, requires they use the literal at least that many times.
    If a ``root`` is provided, allows you to start the search from a specific node.

    ::

        # Student must use the literal 5
        ensure_literal(5)
        # Students must use 5 at least twice
        ensure_literal(5, at_least=2)
        # Students must use the string "hello"
        ensure_literal("hello")

    .. feedback_function:: pedal.assertions.static.ensure_literal

.. function:: prevent_literal_type(literal_type: type, at_most=0, root=None) -> Feedback

    Confirms that the literal type is not in the code, generating Feedback if it is.
    You can use the following literal types: ``int``, ``float``, ``str``, ``bool``,
    ``list``, ``set``, ``tuple``, ``dict``, and ``None``.
    Note that generics are not currently recognized!

    If ``at_most`` is provided, allows them to use the literal at most that many times.
    If a ``root`` is provided, allows you to start the search from a specific node.

    ::

        # Student will not be able to write any integer literals
        prevent_literal_type(int)
        # Students can't use integers more than twice
        prevent_literal_type(int, at_most=2)
        # Students can't use any strings
        prevent_literal_type(str)

    .. feedback_function:: pedal.assertions.static.prevent_literal_type

.. function:: ensure_literal_type(literal_type: type, at_least=0, root=None) -> Feedback

    Confirms that the literal type IS in the code, generating feedback if it is.
    You can use the following literal types: ``int``, ``float``, ``str``, ``bool``,
    ``list``, ``set``, ``tuple``, ``dict``, and ``None``.
    Note that generics are not currently recognized!

    If ``at_least`` is provided, requires they use the literal at least that many times.
    If a ``root`` is provided, allows you to start the search from a specific node.

    ::

        # Student must use at least one integer literal
        ensure_literal_type(int)
        # Students must use integers at least twice
        ensure_literal_type(int, at_least=2)
        # Students must use at least one string
        ensure_literal_type(str)

    .. feedback_function:: pedal.assertions.static.ensure_literal_type

.. function:: prevent_ast(ast_name: str, at_most=0, root=None) -> Feedback

    Confirms that the AST type is not in the code, generating Feedback if it is.
    You should use the type of AST element you are looking for, provided as a string.
    Refer to the AST documentation for more information, or to
    `GreenTreeSnakes <https://greentreesnakes.readthedocs.io/en/latest/>`_.

    If ``at_most`` is provided, allows them to use the literal at most that many times.
    If a ``root`` is provided, allows you to start the search from a specific node.

    ::

        # Student will not be able to write any integer literals
        prevent_ast("Num")
        # Students can't for loops more than twice
        prevent_ast("For", at_most=2)
        # Students can't use any function calls
        prevent_ast("Call")
        # Students can't use subscripts
        prevent_ast("Subscript")

    .. feedback_function:: pedal.assertions.static.prevent_ast

.. function:: ensure_ast(ast_name: str, at_least=0, root=None) -> Feedback

        Confirms that the AST type IS in the code, generating feedback if it is.
        You should use the type of AST element you are looking for, provided as a string.
        Refer to the AST documentation for more information, or to
        `GreenTreeSnakes <https://greentreesnakes.readthedocs.io/en/latest/>`_.

        If ``at_least`` is provided, requires they use the literal at least that many times.
        If a ``root`` is provided, allows you to start the search from a specific node.

        ::

            # Student must use at least one integer literal
            ensure_ast("Num")
            # Students must use for loops at least twice
            ensure_ast("For", at_least=2)
            # Students must use at least one function call
            ensure_ast("Call")
            # Students must use subscripts
            ensure_ast("Subscript")

        .. feedback_function:: pedal.assertions.static.ensure_ast

.. function:: function_prints(function_name: str) -> Feedback

    Confirms that the function prints something, generating feedback if it does not.
    This is a very simple check, simply looking for any ``print`` calls inside the
    function. It does not check if the function is actually called at runtime, or
    if that code is reachable!

    This is just a wrapper around :py:func:`ensure_function_call`.

    ::

        # Student must have a function named "hello_world" with a print statement.
        function_prints("hello_world")

    .. feedback_function:: pedal.assertions.static.ensure_function_call

.. function:: ensure_import(module_name: str, root=None) -> Feedback

    Confirms that the module is imported, generating feedback if it is not.
    This is a very simple check, simply looking for any ``import`` or ``from``
    statements inside the code. It does not check if the module is actually used
    at runtime, or if that code is reachable! There is no ``at_least`` parameter
    because it is assumed that the student will need to import the module at least once.

    ::

        # Student must import the "math" module
        ensure_import("math")

    .. feedback_function:: pedal.assertions.static.ensure_import

.. function:: prevent_import(module_name: str, root=None) -> Feedback

    Confirms that the module is not imported, generating feedback if it is.
    This is a very simple check, simply looking for any ``import`` or ``from``
    statements inside the code. It does not check if the module is actually used
    at runtime, or if that code is reachable!

    If a ``root`` is provided, allows you to start the search from a specific node.

    ::

        # Student must not import the "math" module
        prevent_import("math")

    .. feedback_function:: pedal.assertions.static.prevent_import

.. function:: ensure_documented_functions(root=None) -> Feedback

    Confirms that all functions are documented, generating feedback if they are not.
    Only proper docstrings are accepted, not comments. The docstring must be the
    first thing in the function, and must be a string literal. Students will be
    given a list of names of the functions that are not documented.

    If a ``root`` is provided, allows you to start the search from a specific node.

    ::

        ensure_documented_functions()

    .. feedback_function:: pedal.assertions.static.ensure_documented_functions

.. function:: ensure_function(name: str, arity: int = None, parameters = None, returns=None, root=None, compliment=False) -> Feedback

    Confirms that the function is defined, generating feedback if it is not.
    This checks a number of things about the function:

    1. Whether or not the function exists, and whether it has been defined multiple times.
    2. If found, then the function will move on to check the ``arity`` (number of parameters) if
       that was provided.
    3. If ``parameters`` is provided, then it will check that the parameters are of the correct types.
       The parameters should be a list of types, and can be given as strings or integers (generics are respected).
    4. If ``returns`` is provided, then it will check that the return type is correct. The return type
       should be a type, and can be given as a string or integer (generics are respected).

    If ``compliment`` is a string, then it will use that to generate a :py:func:`compliment`
    feedback if the function is found. If ``compliment`` is ``True``, then it will
    generate a default compliment.

    If ``score`` is provided, then it will use :py:func:`give_partial` to give partial
    credit.

    ::

        ensure_function('add', 2, [int, int], returns=int)
        ensure_function('double', parameters=[int])
        ensure_function('clean_data', compliment="You defined the clean_data function!")
        ensure_function('move_forward', parameters=['Sprite', int], returns='Sprite')

    - .. feedback_function:: pedal.assertions.functions.missing_function
    - .. feedback_function:: pedal.assertions.functions.duplicate_function_definition
    - .. feedback_function:: pedal.assertions.functions.too_few_parameters
    - .. feedback_function:: pedal.assertions.functions.too_many_parameters
    - .. feedback_function:: pedal.assertions.functions.missing_parameter_type
    - .. feedback_function:: pedal.assertions.functions.invalid_parameter_type
    - .. feedback_function:: pedal.assertions.functions.wrong_parameter_type
    - .. feedback_function:: pedal.assertions.functions.wrong_return_type
    - .. feedback_function:: pedal.assertions.functions.missing_return_type

.. function:: ensure_dataclass(example: dataclass, root=None, compliment=False) -> Feedback
              ensure_dataclass(name: str, fields: dict[str, Any], root=None, compliment=False) -> Feedback

    Confirms that the dataclass is defined, generating feedback if it is not.
    This checks a number of things about the dataclass:

    1. Whether or not the dataclass exists, and whether it has been defined multiple times.
    2. If found, then the dataclass will move on to check the ``fields`` (names and types) if
       that was provided. The fields should be a dictionary of names to types, and can be given as strings or integers (generics are respected).
       Alternatively, you can provide the instructor version of the dataclass, and it will check
       that the student version has the same fields.

    If ``compliment`` is a string, then it will use that to generate a :py:func:`compliment`
    feedback if the dataclass is found. If ``compliment`` is ``True``, then it will
    generate a default compliment.

    If ``score`` is provided, then it will use :py:func:`give_partial` to give partial
    credit.

    ::

        ensure_dataclass('Person', {'name': str, 'age': int})
        ensure_dataclass('Sprite', {'x': int, 'y': int}, compliment="You defined the Sprite dataclass!")

        @dataclass
        class Person:
            name: str
            age: int
        ensure_dataclass(Person)

    - .. feedback_function:: pedal.assertions.classes.missing_dataclass
    - .. feedback_function:: pedal.assertions.classes.duplicate_dataclass_definition
    - .. feedback_function:: pedal.assertions.classes.too_few_fields
    - .. feedback_function:: pedal.assertions.classes.too_many_fields
    - .. feedback_function:: pedal.assertions.classes.invalid_field_type
    - .. feedback_function:: pedal.assertions.classes.unknown_field
    - .. feedback_function:: pedal.assertions.classes.missing_field_type
    - .. feedback_function:: pedal.assertions.classes.wrong_fields_type
    - .. feedback_function:: pedal.assertions.classes.name_is_not_a_dataclass
    - .. feedback_function:: pedal.assertions.classes.dataclass_not_available
    - .. feedback_function:: pedal.assertions.classes.missing_dataclass_annotation


.. function:: ensure_prints_exactly(count: int) -> Feedback

    Confirms that the student prints exactly the given number of times, generating feedback if they do not.
    This is just a wrapper around :py:func:`ensure_function_call` and :py:func:`prevent_function_call`.

    ::

        ensure_prints_exactly(3)


.. function:: ensure_starting_code(code: str) -> Feedback

    Confirms that the student's code has the given code, generating feedback if it does not.
    This is most useful for providing some starting code that students are instructed to not
    mess with.

    The given string of code will be parsed and checked with CAIT, so you can be a little flexible.
    It will not be a problem if the student introduces whitespace or comments, but changing
    variable names or something else will be detected.

    ::

        ensure_starting_code("import math")
        ensure_starting_code("def hello():\n    print('hello')")

    .. feedback_function:: pedal.assertions.static.ensure_starting_code

.. function:: prevent_embedded_answer(code: str) -> Feedback

    Confirms that the student's code does not have the given code, generating feedback if it does.
    This is most useful for checking to make sure that the student did not embed some exact literal solution.

    The given string of code will be parsed and checked with CAIT, so you can be a little flexible.
    It will not be a problem if the student introduces whitespace or comments, but changing
    variable names or something else will be sufficient to beat this check.

    ::

        prevent_embedded_answer("print(3)")
        prevent_embedded_answer("def hello():\n    print('hello')")

    .. feedback_function:: pedal.assertions.static.prevent_embedded_answer

.. function:: prevent_printing_functions(exception: str) -> Feedback
              prevent_printing_functions(exceptions: list[str]) -> Feedback
              prevent_printing_functions() -> Feedback

    Confirms that the student's code does not have any print statements in functions, generating feedback if it does.
    This is a common enough problem that it is worth checking for. You can provide a list of function names
    that are allowed to print (e.g., ``main``). You can also provide a single string.

    This does not actually check that ``print`` is called at runtime, and will not allow mundane
    uses of print (e.g., print-statement-debugging). It can also be defeated
    by things like ``sys.stdout.write``.

    ::

        prevent_printing_functions()
        prevent_printing_functions('main')
        prevent_printing_functions(['main', 'log'])

    .. feedback_function:: pedal.assertions.static.prevent_printing_functions

.. function:: ensure_functions_return() -> Feedback
              ensure_functions_return(exception: str) -> Feedback
              ensure_functions_return(exceptions: list[str]) -> Feedback

    Confirms that the student's functions return something, generating feedback if they do not.
    This is a common enough problem that it is worth checking for. You can provide a list of function names
    that do not have to return (e.g., ``main``). You can also provide a single string.

    This does not actually check that the function returns at runtime along every
    branch, and that the ``return`` statement is even reachable.

    ::

        ensure_functions_return()
        ensure_functions_return('main')
        ensure_functions_return(['main', 'save_to_file'])

    .. feedback_function:: pedal.assertions.static.ensure_functions_return


.. function:: only_printing_variables()

    Confirms that the student's code only prints variables, generating feedback if it does not.
    This is a narrow use case, to be sure.
    ::

        only_printing_variables()

    .. feedback_function:: pedal.assertions.static.only_printing_variables

.. function:: prevent_advanced_iteration(allow_while=False, allow_for=False, allow_function=None)

    Confirms that the student's code does not use any iteration, generating feedback if it does.
    By default, all forms of iteration that can be detected easily are blocked
    (``while`` loops, ``for`` loops). You can allow specific forms of iteration
    via the boolean flag parameters.

    By default, most built-in looping functions are blocked.
    You can override this list by providing a list of function names to allow.
    Otherwise, the following functions are blocked: ``sum``, ``map``, ``filter``,
    ``any``, ``all``, ``reduce``, ``sorted``, ``reduce``, ``len``, ``max``, ``min``,
    ``getattr``, ``setattr``, ``eval``, ``exec``, ``iter``, ``next``.

    Surprisingly, does not block comprehensions of any kind. Unsurprisingly, does
    not block recursion.

    Technically, this is just a wrapper around :py:func:`prevent_function_call`
    and :py:func:`prevent_ast`.

    ::

        prevent_advanced_iteration()
        prevent_advanced_iteration(allow_while=True)
        prevent_advanced_iteration(allow_for=True)
        prevent_advanced_iteration(allow_function=['len', 'sum'])
        prevent_advanced_iteration(allow_function='sorted')


.. function:: files_not_handled_correctly(*filenames: str)
              files_not_handled_correctly(number_of_filenames: int)

    Statically detects whether the files have all been opened and closed correctly.
    This is a very simple check, simply looking for corresponding ``open`` function
    calls and ``close`` method calls, or if ``with`` was used (which counts as an
    implicit ``close``). It does not check if the file is actually used, and that the
    files were opened and closed in the correct order or actually closed at runtime!

    If a ``number_of_filenames`` is provided, then it will check for that many files.
    If a list of strings is proivded, then it will check for those specific files.

    This function will also check if the student incorrectly uses ``close`` as a function
    or ``open`` as a method, providing cutom feedback.

    ::

        # Student must open and close exactly one file
        files_not_handled_correctly(1)
        # Student must open and close exactly two files
        files_not_handled_correctly(2)
        # Student must open and close the files "data.txt" and "output.txt"
        files_not_handled_correctly("data.txt", "output.txt")

    .. feedback_function:: pedal.assertions.static.open_without_arguments


