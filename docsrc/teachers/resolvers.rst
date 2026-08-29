.. _teachers_resolvers:

Resolvers
=========

Resolvers determine how feedback is processed and presented to students. Different resolvers provide different strategies for handling multiple pieces of feedback, scoring, and output formatting.

Understanding Resolvers
-----------------------

When your instructor control script runs, it may generate multiple pieces of feedback (errors, successes, warnings, etc.). A resolver decides which feedback to show, how to combine scores, and how to format the final output.

**Key Concepts:**

* **Simple Resolver**: Shows only the first/highest priority feedback
* **Full Resolver**: Shows all generated feedback  
* **Sectional Resolver**: Organizes feedback by sections/parts
* **Custom Resolvers**: You can create your own resolution logic

Simple Resolver (Default)
-------------------------

The simple resolver shows only the most important piece of feedback, following priority rules:

.. code-block:: python

    from pedal import *
    # Simple resolver is used by default
    
    assert_equal(call("add", 1, 2), 3)  # If this fails, student sees this error
    assert_equal(call("multiply", 3, 4), 12)  # This won't be shown if first fails
    set_success("Great work!")  # Only shown if all tests pass
    
    resolve()  # Uses simple resolver by default

**Priority Order (highest to lowest):**
1. Syntax/Runtime errors
2. Instructor assertion failures  
3. Static analysis warnings
4. Success messages

**When to use:** Simple assignments where you want students to fix one issue at a time.

Full Resolver
------------

The full resolver shows all feedback that was generated:

.. code-block:: python

    from pedal import *
    from pedal.resolvers.full import resolve
    
    # All of these will be shown to the student
    assert_equal(call("add", 1, 2), 3, message="Addition test failed")
    assert_equal(call("multiply", 3, 4), 12, message="Multiplication test failed") 
    ensure_function_call('print', message="Must use print function")
    prevent_literal(42, message="Do not hardcode the answer")
    
    # Shows ALL feedback
    resolve()

**Features:**
* Combines all feedback into a comprehensive report
* Adds up partial scores from all sources
* Shows both successes and failures
* Useful for detailed rubric-based grading

**When to use:** When you want students to see all issues at once, or for comprehensive rubric-based grading.

Sectional Resolver  
-----------------

The sectional resolver organizes feedback by assignment sections or parts:

.. code-block:: python

    from pedal import *
    from pedal.resolvers.sectional import resolve
    
    # Part 1 feedback
    with section("Part 1: Basic Functions"):
        set_section_score(40)  # This part worth 40 points
        assert_equal(call("add", 1, 2), 3)
        assert_equal(call("subtract", 5, 3), 2)
        
    # Part 2 feedback  
    with section("Part 2: Error Handling"):
        set_section_score(30)  # This part worth 30 points
        assert_equal(call("divide", 10, 0), "Error")
        
    # Part 3 feedback
    with section("Part 3: Output Format"):
        set_section_score(30)  # This part worth 30 points
        assert_output(student, "Final result: 42")
        
    resolve()

**Output Format:**
```
Part 1: Basic Functions
✓ Addition function works correctly
✓ Subtraction function works correctly  
Score: 40/40

Part 2: Error Handling
✗ Division by zero should return "Error", got None
Score: 0/30

Part 3: Output Format  
✓ Output format is correct
Score: 30/30

Total Score: 70/100
```

**When to use:** Multi-part assignments, labs with distinct sections, or when you want organized feedback.

Advanced Resolver Usage
----------------------

**Mixing Resolvers:**

.. code-block:: python

    from pedal import *
    from pedal.resolvers.full import resolve as full_resolve
    
    # Use different resolvers conditionally
    if get_environment().name == "gradescope":
        # Show all feedback in gradescope
        full_resolve()
    else:
        # Use simple resolver for other environments
        resolve()

**Custom Resolution Logic:**

.. code-block:: python

    from pedal import *
    from pedal.core.report import get_all_feedback
    
    # Get all feedback without resolving
    feedback_list = get_all_feedback()
    
    # Custom logic
    syntax_errors = [f for f in feedback_list if f.category == 'syntax']
    if syntax_errors:
        # Only show syntax errors
        for error in syntax_errors:
            explain(error.message)
    else:
        # Show everything else
        from pedal.resolvers.full import resolve
        resolve()

**Resolver Configuration:**

.. code-block:: python

    from pedal import *
    from pedal.resolvers.full import resolve
    
    # Configure resolver behavior
    resolve(
        show_successes=True,      # Include success messages
        combine_scores=True,      # Add up partial scores  
        max_feedback_items=10,    # Limit number of feedback items
        prioritize_errors=True    # Show errors first
    )

Score Integration with Resolvers
-------------------------------

**Simple Resolver Scoring:**

.. code-block:: python

    from pedal import *
    
    set_maximum_score(100)
    
    # Only the first failing test affects the score
    if call("test1") == "correct":
        give_partial(50)  # 50 points
    if call("test2") == "correct":  
        give_partial(50)  # Only added if test1 passes
        
    resolve()

**Full Resolver Scoring:**

.. code-block:: python

    from pedal import *
    from pedal.resolvers.full import resolve
    
    set_maximum_score(100)
    
    # All partial scores are combined
    if call("test1") == "correct":
        give_partial(30)  # Always added if correct
    if call("test2") == "correct":
        give_partial(40)  # Always added if correct  
    if call("test3") == "correct":
        give_partial(30)  # Always added if correct
        
    resolve()  # Total can be 0, 30, 40, 60, 70, or 100

**Percentage-Based Scoring:**

.. code-block:: python

    from pedal import *
    from pedal.resolvers.full import resolve
    
    set_maximum_score(100)
    
    # Percentage of total score
    if function_exists("helper_function"):
        give_partial("10%")  # 10% of max score (10 points)
    if call("main_function") == "expected":
        give_partial("80%")  # 80% of max score (80 points)
    if "good_style" in analyze_code():
        give_partial("10%")  # 10% of max score (10 points)
        
    resolve()

**Deduction-Based Scoring:**

.. code-block:: python

    from pedal import *
    from pedal.resolvers.full import resolve
    
    set_maximum_score(100)
    give_partial(100)  # Start with full credit
    
    # Deduct points for issues
    if "eval" in get_program():
        give_partial(-10, "Used eval() function")
    if not function_exists("main"):
        give_partial(-20, "Missing main function")
    if line_count() > 50:
        give_partial(-5, "Code is too long")
        
    resolve()

Best Practices
--------------

**Choose the Right Resolver:**

* **Simple**: Beginner courses, step-by-step learning
* **Full**: Advanced courses, comprehensive feedback needed  
* **Sectional**: Multi-part assignments, organized rubrics

**Feedback Quality:**

.. code-block:: python

    # Good: Specific, actionable feedback
    assert_equal(call("calculate_area", 5), 25, 
                message="calculate_area(5) should return 25, not {student_answer}")
    
    # Better: Include hints
    assert_equal(call("calculate_area", 5), 25,
                message="calculate_area(5) should return 25. Remember: area = side²")

**Performance Considerations:**

.. code-block:: python

    from pedal import *
    
    # For large test suites, consider limiting feedback
    if get_environment().name == "gradescope":
        from pedal.resolvers.full import resolve
        resolve(max_feedback_items=15)  # Prevent overwhelming output
    else:
        resolve()  # Simple resolver naturally limits feedback

Common Patterns
--------------

**Progressive Difficulty:**

.. code-block:: python

    from pedal import *
    
    # Check basics first (simple resolver stops at first failure)
    verify()  # Syntax check
    ensure_function_call('def')  # Must define functions
    
    # Then test functionality  
    assert_equal(call("basic_function"), "expected")
    
    # Finally test advanced features
    assert_equal(call("advanced_function"), "complex_result")
    
    resolve()

**Comprehensive Testing:**

.. code-block:: python

    from pedal import *
    from pedal.resolvers.full import resolve
    
    # Test everything, show all results
    test_basic_functionality()
    test_edge_cases() 
    test_error_handling()
    check_code_style()
    verify_documentation()
    
    resolve()

**Guided Learning:**

.. code-block:: python

    from pedal import *
    from pedal.resolvers.sectional import resolve
    
    with section("Step 1: Define the function"):
        ensure_function_definition("my_function")
        
    with section("Step 2: Handle normal cases"):
        assert_equal(call("my_function", 5), 25)
        
    with section("Step 3: Handle edge cases"):
        assert_equal(call("my_function", 0), 0)
        
    resolve()