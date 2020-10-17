Assertions
==========

There are two major kinds of assertions: static and runtime.


Static
------

.. function:: prevent_literal(*literals: Any, muted=False) -> False or Any

    Confirms that the literal is not in the code, returning False if it is not.
    You can use literal strings, integers, floats, booleans, and None.

    .. feedback_function:: pedal.assertions.static.prevent_literal

.. function:: ensure_literal(*literals: Any, muted=False) -> False or Any

    Confirms that the literal IS in the code, returning False if it is not.
    You can use literal strings, integers, floats, booleans, and None.

    .. feedback_function:: pedal.assertions.static.ensure_literal

TODO: Handle all the others

Runtime
-------

.. function:: assert_equal(left, right) -> Feedback

    Tests if the left and right values are equal.

    .. feedback_function:: pedal.assertions.runtime.assert_equal

TODO: Handle all the others