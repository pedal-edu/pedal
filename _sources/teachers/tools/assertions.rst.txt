Assertions
==========

There are two major kinds of assertions: static and runtime.



Static
------

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


Runtime
-------

All of the runtime assertion checks do a lot of work to try to provide really
nice feedback. They will try to provide a lot of information about what exactly
they did when running the student code, so that the error is clearly in the students'
code, and not the instructor code.

.. function:: assert_equal(left, right) -> Feedback
              assert_equal(left, right, exact_strings=False, delta=DELTA)

    The basic unit test, checks whether the left and right values are equal (uses ``==``,
    not ``is``).

    The ``exact_strings`` parameter is whether to require that strings be exactly the
    same, for each character. If ``False`` (the default), then strings will
    be normalized (lowercased, trailing decimals chopped, punctuation
    removed, lines are flattened, and all characters are sorted).

    The ``delta`` controls how float values are compared - how close the values must be.
    If delta is ``None``, then the default delta will be used (``.001``).

    ::

        # This passes
        assert_equal(5, 5)
        # This fails
        assert_equal("five", 5)
        # This passes
        assert_equal([1,2,3], [1,2] + [3])

        # Normally strings are matched imprecisely
        assert_equal("Hello, World!", "hello world")
        # Disable this for more precise matching
        assert_equal("Hello, World!", "hello world", exact_strings=True)

        # Floats are matched imprecisely
        assert_equal(1.0, 1.0001)
        # You might need a more precise delta
        assert_equal(1.0, 1.0001, delta=.0000001)

    Typically, you will use this in conjunction with :py:func:`call` to check students' functions.

    ::

        assert_equal(call("add", 2, 3), 5)

    You do not have to call the function first, and you can even call it on either
    side if you want to do more complicated comparisons.

    ::

        # This will work
        assert_equal(5, call("add", 2, 3))
        # And so will this
        assert_equal(call("add", 2, 3), call("add", 3, 2))

    In the case of more complicated calls, the feedback will be a little more complicated.

    .. code-block::

        Student code failed instructor test.
        I ran the code:
            add(2, 3)
            add(3, 2)
        The value of the first result was:
            -1
        The value of the second result was:
            1
        But I expected the first result to be equal to the second result

    Note that you can override the "I ran the code" part by providing a ``context`` parameter.
    You can also override the ``explanation`` and the ``assertion`` parts.

    .. feedback_function:: pedal.assertions.runtime.assert_equal

.. function:: assert_not_equal(left, right) -> Feedback
              assert_not_equal(left, right, exact_strings=False, delta=DELTA)

    Similar to :py:func:`assert_equal`, but checks that the left and right values are not equal (uses ``!=``,
    not ``is not``). See that function for more details.

    .. feedback_function:: pedal.assertions.runtime.assert_not_equal

.. function:: assert_less(left, right) -> Feedback

    Checks that the left value is less than the right value (uses ``<``).
    See :py:func:`assert_equal` for more details.

    .. feedback_function:: pedal.assertions.runtime.assert_less

.. function:: assert_less_equal(left, right) -> Feedback

    Checks that the left value is less than the right value (uses ``<``).
    See :py:func:`assert_equal` for more details.

    .. feedback_function:: pedal.assertions.runtime.assert_less_equal

.. function:: assert_greater(left, right) -> Feedback

    Checks that the left value is greater than the right value (uses ``>``).
    See :py:func:`assert_equal` for more details.

    .. feedback_function:: pedal.assertions.runtime.assert_greater

.. function:: assert_greater_equal(left, right) -> Feedback

    Checks that the left value is greater than or equal to the right value (uses ``>=``).
    See :py:func:`assert_equal` for more details.

    .. feedback_function:: pedal.assertions.runtime.assert_greater_equal

.. function:: assert_in(item, container) -> Feedback

    Checks that the ``item`` is in the ``container`` (uses ``in``/``not in``).
    See :py:func:`assert_equal` for more details.

    Correctly handles asymmetry of function calls to give proper messages.

    ::

        # "I expected the result to be in the: [1, 2, 3]"
        assert_in(call('guess_number'), [1, 2, 3])

        # "I expected the result to contain: 7"
        assert_in(7, call('provide_options'))

    .. feedback_function:: pedal.assertions.runtime.assert_in

.. function:: assert_not_in(item, container) -> Feedback

    Checks that the ``item`` is not in the ``container`` (uses ``in``/``not in``).

    See :py:func:`assert_not_in` for more details.

.. function:: assert_contains_subset(needles, haystack) -> Feedback

    Checks that the ``needles`` are *all* in the ``haystacks`` (uses ``in``/``not in``).
    This is a little different from :py:func:`assert_in` because it will check
    that all of the needles are in the haystacks, not just one.

    ::

        # "I expected the result to contain: [1, 2, 3]"
        assert_contains_subset([1, 2, 3], call('provide_options'))

        # "I expected the result to be in: [4, 5, 6]"
        assert_contains_subset(call('guess_numbers'), [4, 5, 6])

    .. feedback_function:: pedal.assertions.runtime.assert_contains_subset

.. function:: assert_not_contains_subset(needles, haystack) -> Feedback

    Checks that the ``needles`` are *not* all in the ``haystacks`` (uses ``in``/``not in``).
    See :py:func:`assert_contains_subset` for more details.

    .. feedback_function:: pedal.assertions.runtime.assert_not_contains_subset

.. function:: assert_is(left, right) -> Feedback

    Checks that the left value is the same as the right value (uses ``is``).
    In other words, the two objects MUST be strictly equal, the actaul identical object
    and not just the same contents. This is actually unlikely to occur in most situations,
    given the way that Pedal executes student code in its own context, but is still
    sometimes necessary.
    See :py:func:`assert_equal` for more details.

    .. feedback_function:: pedal.assertions.runtime.assert_is

.. function:: assert_is_not(left, right) -> Feedback

    Checks that the left value is not the same as the right value (uses ``is not``).
    See :py:func:`assert_is` for more details.

    .. feedback_function:: pedal.assertions.runtime.assert_is_not

.. function:: assert_is_none(value) -> Feedback

    Checks that the value is ``None`` (uses ``is None``).
    See :py:func:`assert_equal` for more details.

    .. feedback_function:: pedal.assertions.runtime.assert_is_none

.. function:: assert_is_not_none(value) -> Feedback

    Checks that the value is not ``None`` (uses ``is not None``).
    See :py:func:`assert_equal` for more details.

    .. feedback_function:: pedal.assertions.runtime.assert_is_not_none

.. function:: assert_is_dataclass(value) -> Feedback

    Checks that the value is a dataclass. Note that this is not a type check, but
    actually checking if the given object has the special ``__dataclass_fields__``
    attribute. This is a little bit of a hack, but it is the best way to check
    if a value is actually a dataclass (or at least, it's currently how ``is_dataclass``
    itself checks).
    See :py:func:`assert_equal` for more details.

    .. feedback_function:: pedal.assertions.runtime.assert_is_dataclass

.. function:: assert_is_not_dataclass(value) -> Feedback

    Checks that the value is not a dataclass. Note that this is not a type check, but
    actually checking if the given object has the special ``__dataclass_fields__``
    attribute. This is a little bit of a hack, but it is the best way to check
    if a value is actually a dataclass (or at least, it's currently how ``is_dataclass``
    itself checks).
    See :py:func:`assert_equal` for more details.

    .. feedback_function:: pedal.assertions.runtime.assert_is_not_dataclass

.. function:: assert_true(value) -> Feedback

    Checks that the value is (truthy) ``True``. In other words, the result is
    converted to a boolean using ``bool`, and then checked to see if it is
    ``True``.
    See :py:func:`assert_equal` for more details.

    .. feedback_function:: pedal.assertions.runtime.assert_true

.. function:: assert_false(value) -> Feedback

    Checks that the value is (falsey) ``False``. In other words, the result is
    converted to a boolean using ``bool``, and then checked to see if it is
    ``False``.
    See :py:func:`assert_equal` for more details.

    .. feedback_function:: pedal.assertions.runtime.assert_false

.. function:: assert_length_equal(sequence, length) -> Feedback

    Checks that the length of the sequence is equal to the given length.
    This function exists because the built-in ``len`` actually CANNOT be used
    in conjunction with ``call``. The ``len`` function in CPython **must** return
    an integer, or it will segfault. So to get around this, we have provided our
    version of ``len`` that will avoid this problem. Most of the time you won't even
    notice that you are using our version of ``len``, but if you do, then you can
    use this ``assert_length_equal`` function and ``call`` to check the length of its
    result more directly.

    See :py:func:`assert_equal` for more details on assertions, or
    `This Post <https://stackoverflow.com/questions/42521449/how-does-python-ensure-the-return-value-of-len-is-an-integer-when-len-is-cal>`_
    for more information about the ``len`` problem.

    .. feedback_function:: pedal.assertions.runtime.assert_length_equal

.. function:: assert_length_not_equal(sequence, length) -> Feedback

    Checks that the length of the sequence is not equal to the given length.
    Basically equivalent to ``assert_not_equal(len(sequence), length)``, but
    will correctly provide context since ``len`` cannot be used with ``call``.
    See :py:func:`assert_length_equal` for more details.

    .. feedback_function:: pedal.assertions.runtime.assert_length_not_equal

.. function:: assert_length_less(sequence, length) -> Feedback

    Checks that the length of the sequence is less than the given length.
    Basically equivalent to ``assert_less(len(sequence), length)``, but
    will correctly provide context since ``len`` cannot be used with ``call``.
    See :py:func:`assert_length_equal` for more details.

    .. feedback_function:: pedal.assertions.runtime.assert_length_less

.. function:: assert_length_less_equal(sequence, length) -> Feedback

    Checks that the length of the sequence is less than or equal to the given length.
    Basically equivalent to ``assert_less_equal(len(sequence), length)``, but
    will correctly provide context since ``len`` cannot be used with ``call``.
    See :py:func:`assert_length_equal` for more details.

    .. feedback_function:: pedal.assertions.runtime.assert_length_less_equal

.. function:: assert_length_greater(sequence, length) -> Feedback

    Checks that the length of the sequence is greater than the given length.
    Basically equivalent to ``assert_greater(len(sequence), length)``, but
    will correctly provide context since ``len`` cannot be used with ``call``.
    See :py:func:`assert_length_equal` for more details.

    .. feedback_function:: pedal.assertions.runtime.assert_length_greater

.. function:: assert_length_greater_equal(sequence, length) -> Feedback

    Checks that the length of the sequence is greater than or equal to the given length.
    Basically equivalent to ``assert_greater_equal(len(sequence), length)``, but
    will correctly provide context since ``len`` cannot be used with ``call``.
    See :py:func:`assert_length_equal` for more details.

    .. feedback_function:: pedal.assertions.runtime.assert_length_greater_equal

.. function:: assert_is_instance(obj, cls) -> Feedback

    Checks that the object is an instance of the given class using ``isinstance``.
    If either ``int`` or ``float`` is provided, then they will allow the other
    to be used. To avoid this behavior, simply wrap the type in a tuple or list.
    Note that this function does not support generics.
    See :py:func:`assert_equal` for more details.

    ::

        # This will pass
        assert_is_instance(5, int)
        # This will pass
        assert_is_instance(5, float)
        # This will fail
        assert_is_instance(5, [float])

    .. feedback_function:: pedal.assertions.runtime.assert_is_instance

.. function:: assert_is_not_instance(obj, cls) -> Feedback

    Checks that the object is not an instance of the given class using ``isinstance``.
    If either ``int`` or ``float`` is provided, then they will allow the other
    to be used. To avoid this behavior, simply wrap the type in a tuple or list.
    Note that this function does not support generics.
    See :py:func:`assert_equal` for more details.

    ::

        # This will fail
        assert_is_not_instance(5, int)
        # This will fail
        assert_is_not_instance(5, float)
        # This will pass
        assert_is_not_instance(5, [float])

    .. feedback_function:: pedal.assertions.runtime.assert_not_is_instance

.. function:: assert_type(value, expected_type) -> Feedback

    Checks that the value is of the given type, more flexibly than ``isinstance``.
    Basically, this uses Pedal's type system, which allows for types to be provided
    as type objects (e.g., ``int``, ``str``), with generics (``list[int]``), as strings
    (``"int"``, ``"str"``, ``"list[int]"``), and a few other ways.
    For more information about Pedal's type system, see :ref:`pedal_types`.
    For more about assertions, see :py:func:`assert_equal` for more details.

    ::

        # This will pass
        assert_type(5, int)
        # This will pass
        assert_type(["Hello", "World"], list[str])
        # This will fail
        assert_type([1, 2], list[str])
        # This will pass
        assert_type([1, 2], "list[int]")

    .. feedback_function:: pedal.assertions.runtime.assert_type

.. function:: assert_not_type(value, expected_type) -> Feedback

    Checks that the value is not of the given type, more flexibly than ``isinstance``.
    See :py:func:`assert_type` for more details.

    ::

        # This will fail
        assert_not_type(5, int)
        # This will fail
        assert_not_type(["Hello", "World"], list[str])
        # This will pass
        assert_not_type([1, 2], list[str])
        # This will fail
        assert_not_type([1, 2], "list[int]")

    .. feedback_function:: pedal.assertions.runtime.assert_not_type

.. function:: assert_regex(pattern, text) -> Feedback

    Checks that the regex matches the string, checking that ``re.search`` is not None.
    See :py:func:`assert_equal` for more details.

    .. feedback_function:: pedal.assertions.runtime.assert_regex

.. function:: assert_not_regex(pattern, text) -> Feedback

    Checks that the regex does not match the string, checking that ``re.search`` is None.
    See :py:func:`assert_equal` for more details.

    .. feedback_function:: pedal.assertions.runtime.assert_not_regex

.. function:: assert_output(execution, text) -> Feedback
              assert_output(execution, text, exact_strings=False) -> Feedback

    Determine if the ``execution`` outputs ``text``. Uses the ``==`` operator to do the final comparison.
    In this case, you can think of the output as a single string with newlines, as opposed to a list
    of strings (i.e., it is retrieved with :py:func:`~get_raw_output`).
    See :py:func:`assert_equal` for more details.

    You can use the :py:data:`~student` variable from the Sandbox to get all of the
    output.

    ::

        # Accepts "Hello world"
        assert_output(student, "Hello, World!")
        # Only accepts "Hello, World!"
        assert_output(student, "Hello, World!", exact_strings=True)


    Otherwise, the first argument can be a :py:func:`~call`
    or :py:func:`~run` result. This correctly checks that the desired text is in the
    output as a result of the given function call (and not for some other reason).

    ::

        assert_output(call('main'), "Hello world!")

    If the `exact_strings` parameter is set to be `False`, then output is first normalized following
    this strategy:

    * Make strings lowercase
    * Remove all punctuation characters
    * Split the string by newlines into a list
    * Split each individual line by spaces (aka into words)
    * Remove all empty lines
    * Sorts the lines by default order

    So the default check will be fairly generous about checking output; as long as all the lines are
    there (in whatever order), ignoring punctuation and case, the text will be found.

    .. feedback_function:: pedal.assertions.runtime.assert_output

.. function:: assert_not_output(execution, text) -> Feedback
              assert_not_output(execution, text, exact_strings=False) -> Feedback

    Determine if the ``execution`` does not output ``text``.
    See :py:func:`assert_output` for more details.

    .. feedback_function:: pedal.assertions.runtime.assert_not_output

.. function:: assert_output_contains(execution, text) -> Feedback
              assert_output_contains(execution, text, exact_strings=False) -> Feedback

    Determine if the ``execution`` outputs ``text``.
    Uses the ``in`` operator to do the final comparison.
    The normalization for ``exact_strings`` is more basic than for :py:func:`assert_output`,
    since it will only do the lowercase conversion (punctuation is not removed).

    See :py:func:`assert_output` for more details.

    .. feedback_function:: pedal.assertions.runtime.assert_output_contains

.. function:: assert_not_output_contains(execution, text) -> Feedback
              assert_not_output_contains(execution, text, exact_strings=False) -> Feedback

    Determine if the ``execution`` does not output ``text``.
    See :py:func:`assert_output_contains` for more details.

    .. feedback_function:: pedal.assertions.runtime.assert_not_output_contains

.. function:: assert_has_attr(obj, attr) -> Feedback

    Determine if the ``obj`` has the attribute ``attr`` using the ``hasattr`` function.
    See :py:func:`assert_equal` for more details.

    .. feedback_function:: pedal.assertions.runtime.assert_has_attr

.. function:: assert_has_variable(sandbox, variable_name) -> Feedback

    Determine if the ``sandbox`` has the variable ``variable_name``.
    This actually does check that the variable is defined at runtime, and not just
    that it is defined in the code.
    If you wish to check the top-level module of the student's code, then you
    can use the :py:data:`~student` variable from the Sandbox.

    ::

        assert_has_variable(student, "x")

    .. feedback_function:: pedal.assertions.runtime.assert_has_variable

.. function:: assert_has_function(sandbox, function_name) -> Feedback

    Determine if the ``sandbox`` has the function ``function_name``, and that
    the function is ``callable``.
    If you wish to check the top-level module of the student's code, then you
    can use the :py:data:`~student` variable from the Sandbox.

    ::

        assert_has_function(student, "add")

    .. feedback_function:: pedal.assertions.runtime.assert_has_function

.. function:: ensure_coverage() -> Feedback
              ensure_coverage(at_least=.5) -> Feedback

    Verifies that the most recent executed and traced student code has at least
    the given percentage of coverage (defaulting to half of the code covered).
    The ratio is calculated by dividing the number of lines executed by the total
    number of non-blank, executable lines. The coverage checker does not take into
    account certain line such as docstrings or comments.

    ::

        # 50% coverage
        ensure_coverage()
        # 90% coverage
        ensure_coverage(.9)
        # 100% coverage
        ensure_coverage(1)

    .. feedback_function:: pedal.assertions.runtime.ensure_coverage


.. function:: ensure_called_uniquely(function_name) -> Feedback
              ensure_called_uniquely(function_name, at_least=1) -> Feedback
              ensure_called_uniquely(function_name, ignore=None, why_ignored="") -> Feedback

    Verifies that the most recent executed and traced student code has
    ``at_least`` called the given function uniquely that number of times.
    In other words, it prevents students from calling the same function repeatedly
    WITHOUT changing the arguments. Students often try to bypass simpler checks
    (e.g., call ``assert_equal`` three times) by calling the same function multiple
    times with the same arguments. This at least prevents the most obvious cheating,
    although you should still think about additional ways to check their tests.

    The ``ignore`` (``set[tuple])``) and ``why_ignored`` (``str``) parameters
    are used to ignore certain sets of arguments (the ``tuple`` are the arguments).
    This is useful if you have provided them with some tests, and you do not want
    those tests to count towards their total. The ``why_ignored`` is used to provide
    feedback to the student about why their test was ignored. For example, to say
    something like ````

    ::

        # Student must call the "add" function at least once
        ensure_called_uniquely("add")

        # Student must call the "add" function at least three times
        ensure_called_uniquely("add", 3)

        # We provide them with a few example tests
        ensure_called_uniquely("add", ignore={(1, 2), (2, 3)},
                               why_ignored=" because it was provided to you as an example.")

    .. feedback_function:: pedal.assertions.runtime.ensure_called_uniquely

.. function:: ensure_function_callable(name) -> Feedback

    Verifies that the most recent executed and traced student code has
    a function with the given name that is callable. This is often a little
    more intuitive to use than :py:func:`assert_has_function`.

    ::

        # Student must define a function called "add"
        ensure_function_callable("add")

    - .. feedback_function:: pedal.assertions.runtime.function_not_available
    - .. feedback_function:: pedal.assertions.runtime.name_is_not_a_function

Equivalent Names
****************

Despite the fact that PEP8 is pretty clear you should use snake_case instead
of camelCase, some folks are still just more comfortable with writing ``assertEqual``.
Therefore, we provide aliases of all the functions:

+-----------------------------+--------------------------+
| Original                    | Alias                    |
+-----------------------------+--------------------------+
| assert_equal                | assertEqual              |
+-----------------------------+--------------------------+
| assert_not_equal            | assertNotEqual           |
+-----------------------------+--------------------------+
| assert_less                 | assertLess               |
+-----------------------------+--------------------------+
| assert_less_equal           | assertLessEqual          |
+-----------------------------+--------------------------+
| assert_greater              | assertGreater            |
+-----------------------------+--------------------------+
| assert_greater_equal        | assertGreaterEqual       |
+-----------------------------+--------------------------+
| assert_length_equal         | assertLengthEqual        |
+-----------------------------+--------------------------+
| assert_length_not_equal     | assertLengthNotEqual     |
+-----------------------------+--------------------------+
| assert_length_less          | assertLengthLess         |
+-----------------------------+--------------------------+
| assert_length_less_equal    | assertLengthLessEqual    |
+-----------------------------+--------------------------+
| assert_length_greater       | assertLengthGreater      |
+-----------------------------+--------------------------+
| assert_length_greater_equal | assertLengthGreaterEqual |
+-----------------------------+--------------------------+
| assert_in                   | assertIn                 |
+-----------------------------+--------------------------+
| assert_not_in               | assertNotIn              |
+-----------------------------+--------------------------+
| assert_is                   | assertIs                 |
+-----------------------------+--------------------------+
| assert_is_not               | assertIsNot              |
+-----------------------------+--------------------------+
| assert_is_none              | assertIsNone             |
+-----------------------------+--------------------------+
| assert_is_not_none          | assertIsNotNone          |
+-----------------------------+--------------------------+
| assert_true                 | assertTrue               |
+-----------------------------+--------------------------+
| assert_false                | assertFalse              |
+-----------------------------+--------------------------+
| assert_is_instance          | assertIsInstance         |
+-----------------------------+--------------------------+
| assert_not_is_instance      | assertIsNotInstance      |
+-----------------------------+--------------------------+
| assert_equal                | assertAlmostEqual        |
+-----------------------------+--------------------------+
| assert_not_equal            | assertNotAlmostEqual     |
+-----------------------------+--------------------------+
| assert_regex                | assertRegex              |
+-----------------------------+--------------------------+
| assert_not_regex            | assertNotRegex           |
+-----------------------------+--------------------------+
| assert_prints               | assertPrints             |
+-----------------------------+--------------------------+
| assert_output               | assertOutput             |
+-----------------------------+--------------------------+
| assert_not_output           | assertNotOutput          |
+-----------------------------+--------------------------+
| assert_output_contains      | assertOutputContains     |
+-----------------------------+--------------------------+
| assert_not_output_contains  | assertNotOutputContains  |
+-----------------------------+--------------------------+
| assert_has_attr             | assertHasAttr            |
+-----------------------------+--------------------------+
| assert_has_function         | assertHasFunction        |
+-----------------------------+--------------------------+
| assert_has_variable         | assertHasVariable        |
+-----------------------------+--------------------------+
| assert_type                 | assertType               |
+-----------------------------+--------------------------+
| assert_not_type             | assertNotType            |
+-----------------------------+--------------------------+