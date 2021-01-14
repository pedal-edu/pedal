Teacher Quick Start Guide
=========================

Pedal is composed of `Tools` that write `Feedback` to a centralized `Report`
by detecting `Conditions` in your learners' `Submission` and providing an
appropriate `Response`. As a grader, you just have to write the Instructor
Control Script (or "Grading Script"). In this Quick Start Guide, we'll show you
how you can make this happen in just a few lines of code. Once you've got the
basics, you can check out the :doc:`examples` for a more detailed examples.

Command Line Usage
^^^^^^^^^^^^^^^^^^

Pedal is meant to be integrated into existing autograders (see :ref:`integrations`),
but works perfectly fine on its own through the command line. For example,
after you create a grading script named `grade_assignment.py`, you can run a
single student submission through it to get the recommended feedback:

.. code-block:: console

    $> pedal feedback grade_assignment.py student_submission.py
    You created a variable on line 3 named `sum`, but never ended up using it.

Or you could regrade a folder of student submissions:

.. code-block:: console

    $> ls submissions/
    Ada Bart.py
    Babbage Bart.py
    Reese Trexler.py

    $> pedal grade grade_assignment.py submissions/
    grade_assignment.py, submissions/Ada Bart.py, 100
    grade_assignment.py, submissions/Babbage Bart.py, 0
    grade_assignment.py, submissions/Reese Trexler.py, 63

There are many settings for the command line version. Check the Integrations for
more info.

Instructor Control Scripts
^^^^^^^^^^^^^^^^^^^^^^^^^^

Let's turn to look at what you might put inside that `grade_assignment.py`
script. This is our Instructor Control Script (or a "grading script", if you
prefer). If you're not using a custom environment, then you will probably
want to run the following at the minimum:

.. code-block:: python
    :caption: grade_assignment.py

    # Always start by importing Pedal
    from pedal import *

    # Load the students' code
    student_code = "print('Hello world!')"
    contextualize_report(student_code)

    # Check their source code for syntax errors
    verify()
    # Run their code
    student = run(student_code)

    # ... More instructor logic can go here ...

    # Resolve output and print
    from pedal.resolvers import print_resolve
    print_resolve()

Custom Environments
^^^^^^^^^^^^^^^^^^^

Always needing to setup and run the students' code is tedious. If you write that
code a hundred times, you're likely to make a mistake. Pedal supports the idea
of Environment's to handle the common boilerplate. These can be passed in as
command line arguments, or an autograding platform can provide them automatically.

For example, let's say we ran the following on the command line to emulate the
BlockPy environment:

.. code-block:: console

    $> pedal feedback grade_assignment.py student_submission.py --environment blockpy

Now that same instructor script from before can literally just be:

.. code-block:: python
    :caption: grade_assignment.py

    # Always start by importing Pedal
    from pedal import *

    # ... More instructor logic can go here ...

After just the lines above, the learners' submission will have been:

* Checked for `Source` code errors that prevent parsing, with relevant syntax error messages generated.
* Executed in our `Sandbox` (relatively safely), with relevant runtime error messages generated and student data stored in a `student` variable.
* Reviewed by `TIFA`, which detects and provides feedback on common algorithmic errors (e.g., unused variables).
* A default `Resolver` is called at the end of your script.

We'll talk about what you get from the features above, but first, let's talk about how you provide
custom feedback.

Core Feedback Functions
^^^^^^^^^^^^^^^^^^^^^^^

There are a few core feedback commands that provide simple Responses to students.
Most likely, these will be called within the body of `if` statements throughout
your instructor control script.

**Gently**: The first is :func:`~pedal.core.commands.gently`, which allows you
to present the learner with a simple textual message. This might be a hint, or
a description of the mistake they made, or something else. However, it should
be used to deliver negative feedback. There are other Feedback Functions to
deliver negative feedback; the name `gently` refers to the fact that most
Resolvers will prioritize this feedback lower than runtime errors, syntax
errors, etc. Its high-priority complement is `explain` which will totally
supplant most other kinds of errors.

.. code-block:: python
    :caption: grade_assignment.py

    gently("You failed to solve the question correctly!",
           label="incorrect_answer", title="Wrong!")

Notice that we provide a `label` and `title` (both optional).
We encourage you to label feedback to enhance your subsequent analysis.
Any Feedback Function can take in `label`, `title`, and many other useful
settings.

**Compliment**: You can give the student compliments on things that are going well.

.. code-block:: python
    :caption: grade_assignment.py

    compliment("Good use of a `for` loop!", score="+10%")

In this example, we have also included some partial credit using the optional `score`
parameter.


There are many other core commands, and many other optional parameters to enhance them.
Check out the :doc:`reference` for more.

Finding AST Patterns
^^^^^^^^^^^^^^^^^^^^

CAIT can also be used to declaratively identify regions of source using a Regular-expression style
function named `find_matches` (or `find_match` to get the first result):

.. code-block:: python
    :caption: grade_assignment.py

    matches = find_matches("answer = 5")
    if matches:
        gently("The variable `answer` should not be assigned the value `5`.", "assigned_literal_value_to_answer")

The `find_matches` function supports several kinds of wildcards, and gives you access to
identifiers in the learners' code.

**Wild Card Match**:  The triple underscore is used as a wild match card.
It will match to any node or subtree.
If you wish to access such data, you should use expressions instead.

.. code-block:: python
    :caption: grade_assignment.py

    if find_matches("answer = ___"):
        gently("You assigned something to the variable `answer`", "assigned_to_answer")

**Variable Name Match**: A place holder for variables, denoted by single underscores on both sides.
Many instructor variables are allowed to map to one variable in student code,
but each variable in student code can only map to one instructor variable.
You can get a variable's name via its `id` attribute.

.. code-block:: python
    :caption: grade_assignment.py

    match = find_match("_accumulator_ = 0")
    if match["_accumulator_"].id == "sum":
        gently("Do not name your accumulating variable `sum`, since that is a reserved word.", "shadowed_builtin")

**Subtree Expressions Match**: A place holder for subtree expressions.
An expression is denoted by a double underscore before and after the name of the expression.
You can get the expression's AST node name via the `name` attribute.

.. code-block:: python
    :caption: grade_assignment.py

    match = find_match("_accumulator_ = __initial__")
    if match["__initial__"].name == "List":
        gently("You initialized your accumulator as a list literal.", "initialized_accumulator")

Checking Execution Results
^^^^^^^^^^^^^^^^^^^^^^^^^^

The `Sandbox` module is responsible for running student code as safely as possible,
preventing access to the instructor control script and the grading functionality.
Once run, you can get access to students' final variables' values via the `data` attribute:

.. code-block:: python
    :caption: grade_assignment.py

    if 'sum' in student.data and student.data['sum'] == 47:
        compliment("You have summed correctly!")

Calling Students' Functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can call students' functions and pass in arguments.

.. code-block::
    :caption: grade_assignment.py

    result = call("add_numbers", 5, 7)
    if result == 35:
        gently("You are multiplying instead of adding.")

If you inspect the result of calling a student function, it will appear to be a simple Python
value - in the case above, if the students' code returned an integer, you could add or divide
the result normally. However, it's secretly a heavily-proxied wrapper object that pretends to be
the value - the payoff of that complexity is additional metadata for how that value is produced,
which you can see in the Assertions.

Simple Assertions
^^^^^^^^^^^^^^^^^

Most instructors will already be comfortable with writing assertions, as they would with a
unit testing framework.

.. code-block:: python
    :caption: grade_assignment.py

    from pedal.assertions import *

    assert_equal(call('add', 5, 7), 13)

The `assert_*` functions have a large amount of extra machinery to produce vastly improved error messages.
When a students' code causes an error, the traceback will not show any instructor lines.

.. warning::

    .. raw:: html

        <strong>Failed Instructor Test</strong>
        <pre>Student code failed instructor test.
        I ran the code:
            add(1, 2)
        The value of the result was:
            -1
        But I expected the result to be equal to:
            3</pre>

There are also some more advanced assertions:

.. code-block:: python
    :caption: grade_assignment.py

    assert_output(call("print_values", [1,2,3]), "1\n2\n3")

Simple Unit Testing
^^^^^^^^^^^^^^^^^^^

Assertions are a convenient way to check an individual aspect of code, but sometimes you want to
bundle up a series of arguments/return values.

.. code-block:: python
    :caption: grade_assignment.py

    unit_test('add', [
        ((3, 4), 7),
        ((5, 5), 10),
        ((-3, -3), -6)
    ])

The results of failed tests are placed into an HTML table.

Other Assertions
^^^^^^^^^^^^^^^^

There are many other kinds of assertions:

.. code-block:: python
    :caption: grade_assignment.py

    # Ensure the function has two parameters
    ensure_function('add', arity=2)
    # Ensure the functions' parameters are typed
    ensure_function('add', parameters=[str, int], returns=bool)
    # Make sure all functions are documented
    ensure_documented_functions()



Are they not allowed to use certain operators, literals, or functions for
this question?

.. code-block:: python
    :caption: grade_assignment.py

    # Give operations as strings
    prevent_operation("/")
    ensure_operation("*")
    # You can limit the quantity
    ensure_function_call("print", at_least=2)
    prevent_function_call("print", at_most=4)
    # You can check literal values
    ensure_literal(27)
    prevent_literal(29)
    ensure_literal_type(int)
    prevent_literal_type(str)
    # Or check AST nodes
    ensure_ast("For")
    prevent_ast("While")
    # You can statically check modules
    ensure_import('math')
    prevent_import('statistics')


The toolkit is rich and extensive, although somewhat situational. Refer to the complete
:doc:`reference` for more information.


Resolver Feedback
^^^^^^^^^^^^^^^^^

Ultimately, when you're done detecting conditions and generating responses, you need to
resolve the feedback into some output. Most environments automatically call
the resolver, so it is not necessary to call this yourself. However, the default
environment does not, so you would need to use the following:

.. code-block:: python
    :caption: grade_assignment.py

    from pedal.resolvers.simple import resolve
    resolve()

There are many ways that a resolver could choose among pieces of collected feedback.
The default resolver prioritizes things as follows:

* Highest priority is any feedback given the `'highest'` priority explicitly
* Next up are syntax errors
* Then any custom Instructor feedback (e.g., forbidding `for` loops)
* Then TIFA's algorithmic feedback (e.g., unused variables, incompatible type operations)
* Any Runtime errors
* Any feedback that is given through `gently`
* Finally, any feedback given the `'lowest'` priority explicitly

If no issues are detected, then by default the resolver will mark the submission as correct.
Other custom resolvers can behave differently, and ultimately might want to show more than one
piece of feedback, or not default to marking the submission as correct. However, we have found
this default resolver to be largely effective (anecdotally).