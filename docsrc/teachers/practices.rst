Best Practices
==============

This document summarizes our recommendations for effectively using Pedal in your courses. These practices are based on years of experience using Pedal in various educational contexts.

General Pedagogical Principles
------------------------------

**Start Simple, Build Complexity Gradually**

Begin with basic functionality testing and gradually add more sophisticated checks:

.. code-block:: python

    from pedal import *
    
    # Level 1: Basic existence and syntax
    verify()  # Check syntax first
    ensure_function_definition("calculate_grade")
    
    # Level 2: Basic functionality  
    result = call("calculate_grade", 85, 92, 78)
    if result is not None:
        # Level 3: Correctness
        assert_equal(result, 85.0)
        
        # Level 4: Edge cases
        assert_equal(call("calculate_grade", 100, 100, 100), 100.0)
        assert_equal(call("calculate_grade", 0, 0, 0), 0.0)

**Provide Actionable Feedback**

Always give students specific guidance on what to do next:

.. code-block:: python

    # Bad: Vague feedback
    assert_equal(call("add", 1, 2), 3, message="Wrong answer")
    
    # Good: Specific, actionable feedback
    assert_equal(call("add", 1, 2), 3, 
                message="add(1, 2) returned {student_answer}, but should return 3. "
                       "Check your addition logic.")
    
    # Better: Include debugging help
    assert_equal(call("add", 1, 2), 3,
                message="add(1, 2) returned {student_answer}, expected 3. "
                       "Tip: Make sure you're returning the sum, not printing it.")

**Use Progressive Disclosure**

Don't overwhelm students with too much feedback at once:

.. code-block:: python

    from pedal import *
    
    # Simple resolver: Students see one issue at a time
    verify()  # Fix syntax first
    ensure_function_definition("process_data")  # Then structure
    assert_equal(call("process_data", [1, 2, 3]), [2, 4, 6])  # Then logic
    
    resolve()  # Uses simple resolver by default

Code Organization Best Practices
--------------------------------

**Structure Your Instructor Control Scripts**

Organize your grading scripts for maintainability:

.. code-block:: python

    from pedal import *
    
    def setup_environment():
        """Configure the grading environment."""
        set_maximum_score(100)
        # Set up any necessary test data
        
    def check_syntax_and_structure():
        """Verify basic code structure."""
        verify()
        ensure_function_definition("main_function")
        ensure_function_call("print")
        
    def test_basic_functionality():
        """Test core requirements."""
        assert_equal(call("main_function", 5), 25)
        assert_output(student, "Processing complete")
        
    def test_edge_cases():
        """Test boundary conditions."""
        assert_equal(call("main_function", 0), 0)
        assert_equal(call("main_function", -1), 1)
        
    def check_code_quality():
        """Verify coding best practices."""
        prevent_function_call("eval")
        if line_count() > 50:
            explain("Consider breaking your code into smaller functions")
    
    # Main grading logic
    setup_environment()
    check_syntax_and_structure()
    test_basic_functionality()
    test_edge_cases()  
    check_code_quality()
    
    resolve()

**Use Meaningful Labels and Categories**

.. code-block:: python

    from pedal import *
    
    # Good labeling for analytics and debugging
    assert_equal(call("calculate_gpa", [3.5, 4.0, 3.8]), 3.77,
                message="GPA calculation is incorrect",
                label="gpa_calculation_error",
                category="algorithmic")
    
    prevent_function_call("sum", 
                         message="Don't use the built-in sum() function",
                         label="prohibited_builtin_usage",
                         category="constraints")

**Modularize Common Patterns**

Create reusable testing functions:

.. code-block:: python

    from pedal import *
    
    def test_function_thoroughly(func_name, test_cases, points_per_case=5):
        """Comprehensive function testing utility."""
        if not function_exists(func_name):
            explain(f"Function '{func_name}' not defined", score=0)
            return
            
        for inputs, expected in test_cases:
            result = call(func_name, *inputs)
            assert_equal(result, expected,
                        message=f"{func_name}({', '.join(map(str, inputs))}) "
                               f"should return {expected}",
                        score=points_per_case)
    
    # Usage
    test_cases = [([1, 2], 3), ([0, 5], 5), ([-1, 1], 0)]
    test_function_thoroughly("add_numbers", test_cases)

Feedback Quality Guidelines
---------------------------

**Write for Your Audience**

Tailor feedback to your students' experience level:

.. code-block:: python

    from pedal import *
    
    # For beginners
    if not function_exists("calculate"):
        explain("You need to create a function. Start with: def calculate():")
    
    # For intermediate students  
    if not function_exists("calculate"):
        explain("Define a function named 'calculate' that takes parameters and returns a result")
    
    # For advanced students
    if not function_exists("calculate"):
        explain("Missing calculate() function. Ensure it handles edge cases and follows the specified interface.")

**Use Positive Reinforcement**

Include positive feedback when students do things correctly:

.. code-block:: python

    from pedal import *
    from pedal.resolvers.full import resolve
    
    # Test multiple aspects
    assert_equal(call("add", 1, 2), 3, 
                message="Addition function works correctly! ✓",
                else_message="Great job implementing the add function!")
    
    if function_exists("helper_function"):
        explain("Excellent! You created a helper function. This shows good code organization.",
               correct=True, unscored=True)
    
    resolve()  # Shows both positive and negative feedback

**Provide Context and Examples**

Help students understand not just what's wrong, but why:

.. code-block:: python

    from pedal import *
    
    result = call("format_name", "john", "doe")
    if result != "John Doe":
        explain(f"""
Your format_name function returned '{result}', but should return 'John Doe'.

**Expected behavior:**

- Capitalize the first letter of each name
- Separate with a single space

**Example:**

.. code-block:: python

    def format_name(first, last):
        return first.capitalize() + " " + last.capitalize()
""")

Environment-Specific Best Practices
-----------------------------------

**GradeScope Integration**

.. code-block:: python

    from pedal import *
    from pedal.resolvers.full import resolve
    
    set_maximum_score(100)
    
    # Use full resolver to show all feedback
    # GradeScope can handle comprehensive feedback well
    
    # Provide detailed rubric-style feedback
    test_basic_requirements()    # 40 points
    test_advanced_features()     # 30 points  
    check_code_quality()         # 20 points
    award_style_points()         # 10 points
    
    resolve()

**Interactive Environments (BlockPy, Jupyter)**

.. code-block:: python

    from pedal import *
    
    # Use simple resolver for step-by-step learning
    verify()
    ensure_literal(42, message="Remember to use the number 42 in your solution")
    assert_output(student, "Hello World")
    
    resolve()  # Shows one issue at a time

**Command Line/Terminal Usage**

.. code-block:: python

    from pedal import *
    
    # Provide concise but informative feedback
    assert_equal(call("main"), "expected_output",
                message="main() should return 'expected_output'")
    
    resolve()

Scoring Best Practices
----------------------

**Be Transparent About Scoring**

.. code-block:: python

    from pedal import *
    
    set_maximum_score(100)
    
    # Make point values clear
    assert_equal(call("part1"), "result1", 
                message="Part 1 correct (25 points)", 
                score=25)
    
    assert_equal(call("part2"), "result2",
                message="Part 2 correct (25 points)",
                score=25)
    
    # Award partial credit thoughtfully
    if function_exists("part3"):
        give_partial(10, "Part 3 function defined (+10 points)")
        result = call("part3")
        if result == "expected":
            give_partial(40, "Part 3 works correctly (+40 points)")
        else:
            give_partial(20, "Part 3 attempts solution (+20 points)")

**Use Appropriate Deduction Strategies**

.. code-block:: python

    from pedal import *
    
    # Additive scoring (recommended for beginners)
    set_maximum_score(100)
    if call("test1") == "correct":
        give_partial(25)
    if call("test2") == "correct":
        give_partial(25)
    # etc.
    
    # Deductive scoring (for advanced students)
    set_maximum_score(100)
    give_partial(100)  # Start with full credit
    
    if "eval" in get_program():
        give_partial(-10, "Unsafe function usage")
    if line_count() > 100:
        give_partial(-5, "Code too verbose")

Testing Strategy Best Practices
--------------------------------

**Test Incrementally**

.. code-block:: python

    from pedal import *
    
    # 1. Syntax and basic structure
    verify()
    ensure_function_definition("solve_problem")
    
    # 2. Basic functionality
    result = call("solve_problem", "simple_input")
    if result is not None:
        # 3. Correctness
        assert_equal(result, "expected_simple_output")
        
        # 4. Multiple test cases
        assert_equal(call("solve_problem", "input2"), "output2")
        assert_equal(call("solve_problem", "input3"), "output3")
        
        # 5. Edge cases
        assert_equal(call("solve_problem", ""), "")
        assert_equal(call("solve_problem", "edge_case"), "edge_result")

**Handle Student Code Errors Gracefully**

.. code-block:: python

    from pedal import *
    
    def safe_test_function(func_name, *args, **kwargs):
        """Safely test a function that might not exist or might error."""
        if not function_exists(func_name):
            explain(f"Function '{func_name}' is not defined")
            return None
            
        try:
            return call(func_name, *args, **kwargs)
        except Exception as e:
            explain(f"Function '{func_name}' raised an error: {e}")
            return None
    
    # Usage
    result = safe_test_function("risky_function", "test_input")
    if result is not None:
        assert_equal(result, "expected_output")

**Create Meaningful Test Suites**

.. code-block:: python

    from pedal import *
    
    def create_comprehensive_test_suite():
        """Example of a well-designed test suite."""
        
        # Test normal cases
        normal_tests = [
            ([5, 10], 15),
            ([0, 0], 0),  
            ([100, 200], 300)
        ]
        
        # Test edge cases
        edge_tests = [
            ([0, 1], 1),
            ([-5, 5], 0),
            ([1000000, 1], 1000001)  # Large numbers
        ]
        
        # Test error cases (if applicable)
        try:
            result = call("add_numbers", "not", "numbers")
            explain("Your function should handle invalid input appropriately")
        except:
            pass  # Expected to fail
        
        # Run all tests
        for inputs, expected in normal_tests + edge_tests:
            assert_equal(call("add_numbers", *inputs), expected)

Performance and Efficiency
--------------------------

**Avoid Expensive Operations**

.. code-block:: python

    from pedal import *
    
    # Good: Cache expensive computations
    student_code = get_program()  # Get once, use multiple times
    if "expensive_function" in student_code:
        explain("Consider optimizing expensive_function")
    if student_code.count("for") > 3:
        explain("Multiple loops detected - consider efficiency")
    
    # Good: Limit sandbox executions
    student = run()  # Run once
    result1 = student.data.get('variable1')
    result2 = student.data.get('variable2')

**Set Appropriate Timeouts**

.. code-block:: python

    from pedal import *
    
    # For potentially slow student code
    student = run(timeout=5)  # 5 second timeout
    
    # Test with reasonable limits
    if line_count() > 1000:
        explain("Code is extremely long - this may indicate an infinite loop")

Common Pitfalls to Avoid
------------------------

**Don't Over-Test**

.. code-block:: python

    # Bad: Testing every possible input
    for i in range(1000):
        assert_equal(call("add_one", i), i + 1)
    
    # Good: Representative test cases
    test_cases = [0, 1, -1, 100, -100]
    for test_input in test_cases:
        assert_equal(call("add_one", test_input), test_input + 1)

**Avoid Cryptic Error Messages**

.. code-block:: python

    # Bad
    assert_equal(call("func", 5), 25, message="Wrong")
    
    # Good  
    assert_equal(call("func", 5), 25, 
                message="func(5) should return 25 (5 squared)")

**Don't Assume Student Intent**

.. code-block:: python

    # Bad: Assuming why something is wrong
    if call("calculate", 5) != 25:
        explain("You forgot to square the number")
    
    # Good: Describe what's wrong, let them figure out why
    result = call("calculate", 5)
    assert_equal(result, 25,
                message=f"calculate(5) returned {result}, expected 25")

**Handle Missing Functions Gracefully**

.. code-block:: python

    # Good pattern for optional functionality
    if function_exists("bonus_feature"):
        if call("bonus_feature") == "expected":
            give_partial(5, "Bonus feature implemented correctly!")
        else:
            explain("Bonus feature exists but doesn't work correctly")
    # Don't penalize students for not implementing bonus features

Documentation and Maintenance
-----------------------------

**Document Your Grading Scripts**

.. code-block:: python

    """
    Assignment 3: Data Processing
    
    This grading script tests:
    1. Basic file reading (20 points)
    2. Data filtering (30 points)  
    3. Statistical calculations (30 points)
    4. Output formatting (20 points)
    
    Total: 100 points
    
    Last updated: 2024-01-15
    Known issues: None
    """
    
    from pedal import *
    
    def test_file_reading():
        """Test basic file reading functionality (20 points)."""
        # Implementation here

**Version Control Your Scripts**

- Keep instructor control scripts in version control
- Comment significant changes  
- Test scripts thoroughly before releasing to students
- Keep backups of working versions

**Monitor and Iterate**

.. code-block:: python

    from pedal import *
    
    # Include analytics hooks for monitoring
    def log_common_error():
        if "common_mistake" in get_program():
            explain("This is a common mistake...", 
                   label="common_mistake_v2")  # Version your labels
    
    # Regularly review feedback effectiveness
    # Update messages based on student responses
    # Refine test cases based on edge cases students find

