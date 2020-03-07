Teacher Quick Start Guide
=========================

Pedal is composed of `Tools` that write `Feedback` to a centralized `Report`
by detecting `Conditions` in your learners' `Submission` and providing an appropriate `Response`.
As a grader, you just have to write the Instructor Control Script (or "Grading Script").
In this Quick Start Guide, we'll show you how you can make this happen in just a few lines of code.
Once you've got the basics, you can check out the :doc:`tutorial` for a more in-depth coverage.

Command Line Usage
^^^^^^^^^^^^^^^^^^

Pedal is meant to be integrated into existing autograders (see integrations), but works perfectly fine
on its own through the command line. For example, after you create a grading script named
`grade_assignment.py`, you can run a single student submission through it to get the recommended feedback:

.. code:: console

    $> pedal feedback grade_assignment.py student_submission.py
    You created a variable on line 3 named `sum`, but never ended up using it.

Or you could regrade a folder of student submissions:

.. code:: console

    $> ls submissions/
    Ada Bart.py
    Babbage Bart.py
    Reese Trexler.py

    $> pedal score grade_assignment.py submissions/
    Ada Bart, 100
    Babbage Bart, 0
    Reese Trexler, 63

There are many settings for the command line version. Check the Integrations for more info.

Let's turn to look at what you might put inside that `grade_assignment.py` script.

Standard Environment
^^^^^^^^^^^^^^^^^^^^

Although Pedal can be configured in a lot of ways, you may want to begin by using our default
"Standard Environment", which immediately sets up some of core Tools for a submission of learners' code.

.. code:: python

    from pedal.environments import setup_pedal
    student_code = "print('Hello world!')"
    ast, student, resolve = setup_pedal(student_code)

    # ... More instructor logic can go here ...

    resolve()

After just the lines above, the learners' submission will have been:

* Checked for `Source` code errors that prevent parsing, with relevant syntax error messages generated.
* Parsed into a traversable AST by `CAIT`, to enable structural checks.
* Executed in our `Sandbox` (relatively safely), with relevant runtime error messages generated.
* Reviewed by `TIFA`, which detects and provides feedback on common algorithmic errors (e.g., unused variables).
* A default `Resolver` is provided to be called at the end of your script.

We'll talk about what you get from the features above, but first, let's talk about how you provide
custom feedback.

Core Feedback Functions
^^^^^^^^^^^^^^^^^^^^^^^

There are a few core feedback commands that provide simple Responses to students.
Most likely, these will be called within the body of `if` statements throughout your instructor control script.

.. code:: python

    from pedal import gently, set_success, give_partial, compliment

The first is `gently`, which allows you to present the learner with a simple textual message.
This might be a hint, or a description of the mistake they made, or something else.
However, it should be used to deliver negative feedback.
There are other Feedback Functions to deliver negative feedback; the name `gently` refers to the
fact that most Resolvers will prioritize this feedback lower than runtime errors, syntax errors, etc.

Notice that we provide a label as a second argument.
Although optional, we encourage you to label feedback to enhance your subsequent analysis.

.. code:: python

    gently("You failed to solve the question correctly!", "incorrect_answer")

The next is `set_success`, which allows you to establish that the learner has completed the problem
successfully. The default resolver will prioritize this feedback above all others.

.. code:: python

    set_success()

Along the way, you can give students partial credit with `give_partial`. You'll need to check whether
your autograder expects the sum to be 1 or 100.

.. code:: python

    give_partial(45)

Finally, you can give the student compliments on things that are going well.

.. code:: python

    compliment("You've almost got it!")

There are several other core commands, so check out the :doc:`reference` for more.

Finding AST Elements
^^^^^^^^^^^^^^^^^^^^

`CAIT` is a "Capturer for AST Inclusion Trees", a fancy way of saying it can be used to access the
AST of the learners' code. If the code failed to parse, `CAIT` functions are still safe to run - they
will not cause exceptions, just return no results. `CAIT` has almost no `Feedback Functions`; instead, it
supports `Feedback Condition` authoring through two mechanisms.

The first major feature is `find_all`:

.. code:: python

    if ast.find_all("For"):
        gently("It looks like your code is using a `for` loop; don't do that!", "used_for_loop")

The `find_all` function returns a list of `CaitNodes`, which represent elements of the AST.
You can access attributes of these nodes; we recommend you refer to the
`GreenTreeSnakes <https://greentreesnakes.readthedocs.io/en/latest/nodes.html>`_ documentation
for more information about what is available.

.. code:: python

    loops = ast.find_all("For")
    for loop in loops:
        if loop.target.name == "Tuple":
            gently("You have a `for` loop with multiple targets, don't do that!", "for_loop_multiple_targets")

Finding AST Patterns
^^^^^^^^^^^^^^^^^^^^

CAIT can also be used to declaratively identify regions of source using a Regular-expression style
function named `find_matches` (or `find_match` to get the first result):

.. code:: python

    matches = ast.find_matches("answer = 5")
    if matches:
        gently("The variable `answer` should not be assigned the value `5`.", "assigned_literal_value_to_answer")

The `find_matches` function supports several kinds of wildcards, and gives you access to
identifiers in the learners' code.

**Wild Card Match**:  The triple underscore is used as a wild match card.
It will match to any node or subtree.
If you wish to access such data, you should use expressions instead.

.. code:: python

    if ast.find_matches("answer = ___"):
        gently("You assigned something to the variable `answer`", "assigned_to_answer")

**Variable Name Match**: A place holder for variables, denoted by single underscores on both sides.
Many instructor variables are allowed to map to one variable in student code,
but each variable in student code can only map to one instructor variable.
You can get a variable's name via its `id` attribute.

.. code:: python

    match = ast.find_match("_accumulator_ = 0")
    if match["_accumulator_"].id == "sum":
        gently("Do not name your accumulating variable `sum`, since that is a reserved word.", "shadowed_builtin")

**Subtree Expressions Match**: A place holder for subtree expressions.
An expression is denoted by a double underscore before and after the name of the expression.
You can get the expression's AST node name via the `name` attribute.

.. code:: python

    match = ast.find_match("_accumulator_ = __initial__")
    if match["__initial__"].name == "List":
        gently("You initialized your accumulator as a list literal.", "initialized_accumulator")

Checking Execution Results
^^^^^^^^^^^^^^^^^^^^^^^^^^

The `Sandbox` module is responsible for running student code as safely as possible,
preventing access to the instructor control script and the grading functionality.
Once run, you can get access to students' final variables' values via the `data` attribute:

.. code:: python

    if 'sum' in student.data and student.data['sum'] == 47:
        set_success()

You can also check for variable's in a few other ways:

.. code:: python

    integer_variables = student.get_variables_by_type(int)
    for name, value in integer_variables:
        if value == 47:
            gently("You should not have assigned the value 47 to the variable "+name)

However, you should be aware that true sandboxing is impossible in a dynamic language like Python
We recommend setting course policies that disincentivize cheating and ensuring your autograding environment
has multiple lines of defense, such as proper file system permissions.

Checking Execution Output
^^^^^^^^^^^^^^^^^^^^^^^^^

The `output` attribute provides a list of strings representation of all the lines printed by the students'
code, minus the trailing newlines.

.. code:: python

    if "Hello world!" not in student.output:
        gently("You need to print the string 'Hello world!'")

There is also `raw_output` to get a single string, including newline characters.

.. code:: python

    if "Complex\nText" in student.raw_output:
        gently("You should have the precise text we gave you in there.")

Calling Students' Functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can call students' functions and pass in arguments.

.. code:: python

    result = student.call("add_numbers", 5, 7)
    if result == 13:
        set_success()

If you inspect the result of calling a student function, it will appear to be a simple Python
value - in the case above, if the students' code returned an integer, you could add or divide
the result normally. However, it's secretly a heavily-proxied wrapper object that pretends to be
the value - the payoff of that complexity is additional metadata for how that value is produced,
which you can see in the Assertions.

Simple Assertions
^^^^^^^^^^^^^^^^^

Most instructors will already be comfortable with writing assertions, as they would with a
unit testing framework.

.. code:: python

    from pedal.assertions import *

    assert_equal(student.call('add', 5, 7), 13)

The `assert_*` functions have a large amount of extra machinery to produce vastly improved error messages.
When a students' code causes an error, the traceback will not show any instructor lines.

.. todo:: produce an example feedback message.

There are also some more advanced assertions:

.. code:: python

    assert_prints(student.call("print_values", [1,2,3]), ["1", "2", "3"])

Simple Unit Testing
^^^^^^^^^^^^^^^^^^^

Assertions are a convenient way to check an individual aspect of code, but sometimes you want to
bundle up a series of input/output tests (whether that means stdin/stdout or arguments/return values).
The `Toolkit` module is a collection of useful functions, including `unit_test` and `output_test`.

.. code:: python

    from pedal.toolkit.functions import unit_test, output_test

    if unit_test('add', [ (3, 4, 7), (5, 5, 10), (-3, -3, -6) ]):
        set_success()

These Feedback Functions return True if all unit tests pass, but generate Responses depending on how
they failed. The results of failed tests are placed into an HTML table.

Other Toolkit Tools
^^^^^^^^^^^^^^^^^^^

There are a large number of other tools in the toolkit. For example, you can quickly perform
a check of the source code that a function has the appropriate signature:

.. code:: python

    from pedal.toolkit.functions import match_signature

    if not match_signature('add', 2):
        gently("The `add` function should have 2 parameters.")

Or assert that all functions must have a docstring:

.. code:: python

    from pedal.toolkit.functions import all_documented

    all_documented()

Worried that students are printing out a literal value instead of relying on variables?

.. code:: python

    from pedal.toolkit.utilities import only_printing_variables

    if not only_printing_variables():
        gently("You should only be printing variables' values, not literal values.")

Are they not allowed to use certain operators for this question?

.. code:: python

    from pedal.toolkit.utilities import prevent_operation

    prevent_operation("/")
    prevent_operation("*")

The toolkit is rich and extensive, although somewhat situational. Refer to the complete
:doc:`reference` for more information.

Resolver the Feedback
^^^^^^^^^^^^^^^^^^^^^

Ultimately, when you're done detecting conditions and generating responses, you need to
resolve the feedback into some output. The Simple Environment provides access to the
Simple Resolver, which has a prioritization scheme to choose a single, most important piece of feedback.

.. code:: python

    resolve()
