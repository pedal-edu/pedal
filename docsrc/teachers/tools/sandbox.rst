Sandbox
=======

The primary goal of this module is to rerun the students code under other circumstances.

Typically, your environment will handle running the Sandbox for you. Sometimes, it will avoid running
the students' code using Pedal in favor of its own execution environment. However, they evaluate the students'
code, most environments will provide a `student` variable that holds information about the executed code.

.. code-block:: python

    from pedal.sandbox import run

    student = run()

.. function:: call(function: str, *arguments: Any, inputs: list[str]= None, target: str="_") -> Result

    Calls the given `function` that the student has defined, using all the given `arguments`.
    You can pass in `inputs` to mock any builtin `input` calls. You can also choose the variable within the students'
    code namespace that the result will be assigned to.

    Note that this function returns a Sandbox Result Proxy. This is an extremely
    sophisticated type that attempts to perfectly imitate built-in values as
    much as possible. If a students' code returns an integer, you can treat the
    returned value as if it were an integer (adding, subtracting, even using
    things like `isinstance`). However, extra meta information is sneakily
    included in the result, which allows more sophisticated output that
    includes the context of the call.

.. function:: run(code: str, inputs: list[str] = None) -> student

    Runs the given arbitrary code, as you might expect from calling `exec`.
    However, handles a lot of common sandboxing issues. For example, the
    students' code is in a seperate thread and shouldn't be able to modify
    anything about the Report object or access files on disk (unless you
    explicitly allow them). Code with errors will have their errors adjusted
    to better provide the context of what went wrong and ensure that students
    understand why their code is wrong and not the instructors.

.. data:: student.data: dict[str, Any]

    All of the students' created variables and functions will be stored in
    a dictionary attached to the `data` field. You can access it like so:

    .. code-block:: python

        from pedal.sandbox import run
        student = run('alpha = 7')
        student.data['alpha']

.. function:: set_input(*inputs: str)

    Sets the given `inputs` strings to be the value that `input` will return.
    This allows you to test students' code that involves the builtin `input`
    function, mocking whatever needs to be typed in.

TODO: Add in other pedal.sandbox.commands!