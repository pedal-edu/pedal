.. _teachers_ffs:

Feedback Functions
------------------

A major concept in Pedal is a :term:`Feedback Function`, which encapsulate the idea of a :term:`Feedback Condition` and
a :term:`Feedback Response` pair. Pedal provides a large number of Feedback Functions and mechanisms to create new ones.
As instructors, you have can control and override the default behavior of these feedback functions in various ways.

Some Composite Feedback Functions do not have keyword parameters, because of their complexity. However, we strive to
universally provide these parameters!

This documentation describes Feedback Functions from the perspective of *teachers* who are interested in writing
autograding scripts. If you are interested in extending Pedal, you might want to consult the :ref:`developers_ffs`
documentation page.



.. py:attribute:: title
    :type: str

    The descriptive name for this Feedback Function that will be shown to students as a "header" of
    sorts.

.. py:attribute:: message
    :type: str

    The actual text of the feedback that will be shown to the student. Depending on the current Formatter
    and Environment, may support HTML or Markdown. Will override the :py:attr:`message_template` if provided.

.. py:attribute:: message_template
    :type: str

    The string template used to generate the text to show the student if the :py:attr:`message` is not provided.
    Any field names wrapped in curly braces will be interpolated when the Feedback Function meets its condition.
    These fields can be further manipulated by incorporating the :ref:`teacher_formatter`'s supported conversion flags:

    .. code-block::

        # A message_template can have fields and conversion flags:
        "Your code returned {student_answer!python_value}"

        # Which will generate the HTML output:
        "Your code returned <code>5</code>"

        # Or the plain-text output:
        "Your code returned 5"

    Usually, you will override the :py:attr:`message` instead of the template, to set a specific message instead.

.. py:attribute:: else_message
    :type: str

    A string to render as the :py:attr:`message` if the Feedback Function's condition is NOT met.
    Except for Feedback Functions that have a positive valence - then this message is shown when the
    FF's condition IS met.
    Otherwise follows the same rules as the message field.
    The typical use case for this parameter is to display a positive message if the students happen to complete
    a specific subtask or task and a Resolver is chosen that will show multiple kinds of feedback.
    Note that because A) the default Resolver only shows one piece of feedback, B) that resolver prioritizes errors,
    and C) that resolve prioritizes the final Success over lesser successes, you are unlikely to see these messages
    in most cases as the actual feedback. However, the message will be provided as a Positive feedback, for environments
    that choose to render such things.

.. py:attribute:: else_message_template
    :type: str

    The corresponding string template parameter for the :py:attr:`else_message` parameter. Works the same as its
    corresponding :py:attr:`message_template` field, just for providing text to the student in the case of no
    ``else_message`` being provided. Usually not used.

.. py:attribute:: category
    :type: pedal.core.feedback_category.FeedbackCategory

    An internal name categorizing the feedback condition, such as ``"syntax"`` or ``"runtime"``.
    Usually you don't want to change this.

.. py:attribute:: kind
    :type: pedal.core.feedback_category.FeedbackKind

    An internal name categorizing the feedback response, such as ``"hint"`` or ``"mistake"``.
    Usually you don't want to change this.

.. py:attribute:: fields
    :type: dict[str, typing.Any]

    Internal data for the Feedback Function used in constructing its message and justification.

.. py:attribute:: field_names
    :type: list[str]

    An explicit list of the field names for this Feedback Function. If not provided, then it will
    be inferred from the :py:attr:`fields`. Usually you won't need to do anything with this.


.. py:attribute:: tool
    :type: str

    What Tool was responsible for creating this feedback function. Usually you don't want to change this.

.. py:attribute:: label
    :type: str

    A unique name for this general class of feedback. You might override this to give a more specific
    identifier to the feedback for future analysis purposes.

.. py:attribute:: justification
    :type: str | tuple[str, str]

    An internal explanation for why this feedback was chosen (and/or not chosen), which can be shown
    to the instructor (but not the student). Usually you don't want to change this.


.. py:attribute:: priority
    :type: str

    Controls the ordering of this feedback relative to others. Higher priority feedback is shown first.
    Common values: ``"syntax"`` (highest), ``"runtime"``, ``"algorithmic"``, ``"style"`` (lowest).
    You can also use custom priority strings.

.. py:attribute:: score
    :type: float | str

    The score to award (or deduct) when this feedback is triggered. Can be a number (e.g., ``5.0``)
    or a percentage string (e.g., ``"10%"``). Negative values deduct points.

.. py:attribute:: correct
    :type: bool

    Whether this feedback indicates correct behavior (``True``) or incorrect behavior (``False``).
    Affects how resolvers prioritize and display the feedback.

.. py:attribute:: muted
    :type: bool

    If ``True``, this feedback will not be shown to students but will still affect scoring.
    Useful for instructor-only feedback or internal tracking.

.. py:attribute:: unscored
    :type: bool  

    If ``True``, this feedback will not affect the student's score, only provide informational messages.

.. py:attribute:: activate
    :type: bool

    Whether this feedback should be activated immediately when created. Usually ``True`` by default.

Common Feedback Functions
-------------------------

Pedal provides many built-in feedback functions. Here are some commonly used ones with practical examples:

**Assertion-Based Functions:**

.. code-block:: python

    from pedal import *
    
    # Test function calls with custom messages
    assert_equal(call("add", 1, 2), 3, 
                message="Your add function should return 3 when called with 1 and 2")
    
    # Test output with score attribution
    assert_output(student, "Hello World", 
                 message="Your program should print 'Hello World'",
                 score=25)
    
    # Test with else_message for positive feedback
    assert_equal(call("multiply", 3, 4), 12,
                message="Multiplication is incorrect: expected 12, got {student_answer}",
                else_message="Excellent! Your multiplication function works perfectly!",
                score=10)

**Code Structure Functions:**

.. code-block:: python

    from pedal import *
    
    # Ensure specific patterns exist
    ensure_function_call('print', 
                        message="You must use the print function to display output",
                        score=5)
    
    ensure_literal(42, 
                  message="Your solution must include the number 42",
                  else_message="Good! You used the required number 42")
    
    # Prevent problematic patterns
    prevent_function_call('eval',
                         message="Do not use the eval() function - it's dangerous!",
                         score=-10)
    
    prevent_literal("hardcoded answer",
                   message="Don't hardcode the entire answer as a string",
                   priority="style")

**Style and Quality Functions:**

.. code-block:: python

    from pedal import *
    
    # Check code quality
    def check_code_style():
        if line_count() > 50:
            explain("Your code is quite long. Consider breaking it into smaller functions.",
                   category="style", score=-2)
        
        if function_count() == 0:
            explain("Consider organizing your code into functions for better readability.",
                   category="style", score=-1)
        
        if comment_count() == 0:
            explain("Adding comments would make your code more readable.",
                   category="style", unscored=True)

**Custom Feedback Functions:**

.. code-block:: python

    from pedal import *
    
    def check_algorithm_efficiency():
        """Custom feedback function to check algorithm efficiency."""
        code = get_program()
        
        if "for" in code and "for" in code[code.index("for")+1:]:
            explain("You're using nested loops. Can you solve this more efficiently?",
                   title="Algorithm Efficiency",
                   category="algorithmic",
                   label="nested_loops_warning",
                   score=-5)
        
        if code.count("if") > 5:
            explain("You have many if statements. Consider using elif or other structures.",
                   title="Code Structure",
                   category="style", 
                   priority="style")

**Contextual Feedback Functions:**

.. code-block:: python

    from pedal import *
    
    def provide_contextual_help():
        """Provide different feedback based on what the student attempted."""
        
        if function_exists("calculate_area"):
            result = call("calculate_area", 5)
            if result is None:
                explain("Your calculate_area function exists but doesn't return anything. "
                       "Add a 'return' statement.",
                       title="Missing Return Statement",
                       score=5)  # Partial credit for attempting
            elif result != 25:
                explain(f"calculate_area(5) returned {result}, but should return 25. "
                       f"Remember: area of a square = side × side",
                       title="Calculation Error", 
                       score=8)  # More credit for having return statement
            else:
                explain("Perfect! Your calculate_area function works correctly.",
                       title="Function Success",
                       score=15,
                       correct=True)
        else:
            explain("You need to define a function named 'calculate_area'. "
                   "Start with: def calculate_area(side):",
                   title="Missing Function Definition",
                   score=0)

**Deduction-Based Feedback Functions:**

.. code-block:: python

    from pedal import *
    
    def apply_deductions():
        """Apply point deductions for poor practices."""
        
        set_maximum_score(100)
        give_partial(100)  # Start with full credit
        
        # Deduct for bad practices
        if "global" in get_program():
            explain("Avoid using global variables in this assignment.",
                   score=-10, 
                   category="style",
                   muted=False)  # Show to student
        
        if "import os" in get_program():
            explain("OS imports detected - instructor review required.",
                   score=-5,
                   category="security", 
                   muted=True)  # Hidden from student, instructor only
        
        # Award bonus for good practices
        if comment_ratio() > 0.1:  # More than 10% comments
            explain("Excellent commenting! Bonus points awarded.",
                   score=5,
                   category="style",
                   correct=True)

**Progressive Feedback Functions:**

.. code-block:: python

    from pedal import *
    
    def progressive_testing():
        """Provide increasingly specific feedback."""
        
        # Level 1: Basic existence check
        if not function_exists("process_data"):
            explain("Define a function called 'process_data'", 
                   label="missing_function")
            return  # Don't continue if basic requirement isn't met
        
        # Level 2: Basic functionality
        try:
            result = call("process_data", [1, 2, 3])
        except:
            explain("Your process_data function has an error when called with [1, 2, 3]",
                   label="function_error")
            return
        
        # Level 3: Correct output type
        if not isinstance(result, list):
            explain("process_data should return a list, not {type}".format(type=type(result).__name__),
                   label="wrong_return_type")
            return
        
        # Level 4: Correct output values
        if result != [2, 4, 6]:
            explain("process_data([1, 2, 3]) should return [2, 4, 6], got {result}".format(result=result),
                   label="wrong_return_value")
            return
        
        # Level 5: Success!
        explain("Excellent! Your process_data function works perfectly!",
               correct=True,
               score=20)

Advanced Feedback Function Techniques
------------------------------------

**Conditional Feedback Based on Environment:**

.. code-block:: python

    from pedal import *
    
    def environment_specific_feedback():
        """Provide different feedback based on the environment."""
        env = get_environment()
        
        if env.name == "gradescope":
            # More detailed feedback for gradescope
            assert_equal(call("func", 1), 2, 
                        message="Detailed explanation: func(1) should return 2 because...")
        else:
            # Simpler feedback for other environments  
            assert_equal(call("func", 1), 2, 
                        message="func(1) should return 2")

**Feedback with Rich Formatting:**

.. code-block:: python

    from pedal import *
    
    def rich_feedback_example():
        """Use rich formatting in feedback messages."""
        
        result = call("calculate", 5, 3)
        expected = 8
        
        if result != expected:
            explain("""
Your calculate function returned {student_answer!python_value} but should return {expected!python_value}.

**Debugging steps:**
1. Check your addition logic
2. Verify parameter order
3. Test with simple values

**Example:**
```python
def calculate(a, b):
    return a + b  # Make sure you're adding, not subtracting!
```
""".format(student_answer=result, expected=expected),
                   title="Calculation Error",
                   message_template="Custom formatted error message")

**Feedback Function Composition:**

.. code-block:: python

    from pedal import *
    
    def comprehensive_function_test(func_name, test_cases, points_per_test=5):
        """Test a function comprehensively with multiple test cases."""
        
        if not function_exists(func_name):
            explain(f"Function '{func_name}' is not defined", score=0)
            return False
        
        passed_tests = 0
        total_tests = len(test_cases)
        
        for i, (inputs, expected) in enumerate(test_cases):
            try:
                result = call(func_name, *inputs)
                if result == expected:
                    passed_tests += 1
                    # Give partial credit
                    give_partial(points_per_test, 
                               f"Test case {i+1} passed", 
                               muted=True)
                else:
                    explain(f"Test case {i+1}: {func_name}({', '.join(map(str, inputs))}) "
                           f"returned {result}, expected {expected}",
                           score=0)
            except Exception as e:
                explain(f"Test case {i+1}: {func_name}({', '.join(map(str, inputs))}) "
                       f"raised an error: {e}",
                       score=0)
        
        # Summary feedback
        if passed_tests == total_tests:
            explain(f"Excellent! All {total_tests} test cases passed!", 
                   correct=True)
            return True
        else:
            explain(f"Passed {passed_tests}/{total_tests} test cases", 
                   score=passed_tests * points_per_test)
            return False

    # Usage:
    test_cases = [
        ([1, 2], 3),
        ([0, 5], 5), 
        ([-1, 1], 0),
        ([10, -5], 5)
    ]
    comprehensive_function_test("add_numbers", test_cases, points_per_test=10)
