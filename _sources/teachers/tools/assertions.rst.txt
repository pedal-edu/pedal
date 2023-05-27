Assertions
==========

There are two major kinds of assertions: static and runtime.



Static
------

.. function:: prevent_literal(*literals: Any) -> Feedback

    Confirms that the literal is not in the code, returning False if it is not.
    You can use literal strings, integers, floats, booleans, and None.

    .. feedback_function:: pedal.assertions.static.prevent_literal

.. function:: ensure_literal(*literals: Any) -> Feedback

    Confirms that the literal IS in the code, returning False if it is not.
    You can use literal strings, integers, floats, booleans, and None.

    .. feedback_function:: pedal.assertions.static.ensure_literal

TODO: Handle all the others

prevent_function_call()
ensure_function_call()
prevent_operation()
ensure_operation()
ensure_operator
prevent_operator
prevent_literal
ensure_literal
prevent_literal_type
ensure_literal_type
prevent_ast
ensure_ast
function_prints
has_import
ensure_import
prevent_import
ensure_documented_functions
ensure_function
ensure_dataclass
ensure_prints_exactly
ensure_starting_code
prevent_embedded_answer

Runtime
-------

.. function:: assert_equal(left, right) -> Feedback

    Tests if the left and right values are equal.

    .. feedback_function:: pedal.assertions.runtime.assert_equal

TODO: Handle all the others