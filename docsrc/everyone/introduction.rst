Introduction
============

.. image:: ../_static/pedal-overview.png

We believe that autograding feedback should be *more* than just unit tests.
Program analysis can give us deep insight into students' problems - if they declare a variable and
its never used it, shouldn't we address that with feedback? Research has shown that many existing
error messages are unhelpful - can't we provide more context, details, and pedagogically-friendly
language when students get a TypeError because they added a string and a number? Our goal is to make
it easier for instructors to leverage these tools and start making measurable progress towards helping learners.

.. code-block:: python
    :caption: student.py

    def add_prices(books):
        for book in books:
            total = book + books
            return total

The student's code above has a number of errors - they failed to initialize a variable, they
used the list instead of the iteration target, they returned inside of a loop, etc. Pedal could
detect many of these scenarios and provide different kinds of feedback.

.. code-block:: python
    :caption: instructor.py

    from pedal import verify
    verify()

    # Generic, friendly feedback on undeclared variables, among others
    from pedal.tifa import tifa_analysis
    tifa_analysis()

    # Partial credit for good progress
    from pedal import give_partial
    from pedal.cait import parse_program
    ast = parse_program()
    if ast.find("For"):
        give_partial(1/10, "Right, you need a `for` loop!")

    # Give feedback by finding a common problem-specific mistake
    from pedal import explain
    from pedal.cait import find_matches
    matches = find_matches("for _expr_ in _list_:\n ___ = ____ + _list_")
    if matches:
        explain("list_inside_loop", "You shouldn't use the list inside the for loop.")

    # Unit test, with enhanced tracebacks and safe execution!
    from pedal.sandbox import run
    from pedal.assertions import assert_equal, assert_has_function
    student = run()
    assert_has_function(student, 'add_prices', list)
    assert_equal(student.add_prices([1,2,3]), 6)

This only briefly summarizes some of our features, read some of the sections below to find out more!
