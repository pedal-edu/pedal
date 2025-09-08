.. _full_api:

Developer API
=============

This is the complete API reference for Pedal and its associated components.
If you are an instructor, you might find it more helpful to read over the :ref:`quickstart` too.

Important Concepts
******************

.. describe:: Feedback Function

    Any function that can attach a Feedback object to a Report is technically a Feedback Function, and
    should be clearly marked as such.

    Feedback Response should be Markdown, but should also provide a plain-text console-friendly version.

    Recommended to have a ``muted`` boolean parameter that allows you to use it strictly as a Condition.
    When muted, a function still attaches feedback but that feedback will not contribute to correctness
    or consider being displayed to the user. Its score will be added, though!

    Three perspectives:
        Grader Developer: We need to be able to create feedback responses that are delivered clearly
            to the autograder without being cumbersome.
        Feedback Experimenter: We need to be able to customize these messages in a way that exposes all
            the features.
        Researcher: We aren't trying to analyze Feedback through the source code. We want to be
            able to generate metadata about any piece of Feedback included in the Report.

    Tools should register all their known Feedback labels up front. Goal is to broadcast what the current
    feedback is. Ideally we'd also have a system for elegantly overriding that feedback's wording.

    Feedback Labels should have a standard naming schema; the other fields should also have some guidance
    on how they should be authored. In general, we attempt to follow Python variable naming
    rules (lowercase, underscores)

    An "Atomic" Feedback Function is one that has exactly one possible label outcome.
    They should have their metadata moved to be static function attributes.

    - TEMPLATE_TEXT ((**)=>str): A function that can be used to generate the ``text`` string. All of the fields will be passed in as keyword arguments.
    - MESSAGE_TEXT ((**)=>str): They might also have MESSAGE_TEXT with the same concept.
    - JUSTIFICATION (str): A static justification
    - TITLE (str): A static student-friendly title
    - VERSION (str): A semvar string (e.g., '0.0.1'), should be paired with a docstring changelog.

    A "Composite" Feedback Function has multiple possible label outcomes.
    - LABELS attribute could spell them all out?

    Feedback in tools:
        TIFA: Relatively centralized. Finite set. Desire for configurability, reuse of phrasings.
        Source: Mostly reporting syntax errors. Finite set.
        CAIT: No feedback functions, just feedback condition detectors.
        Assertions: Finite set. Desire for configurability, reuse of phrasings. Heavily procedurally developed.
        Questions: Finite set, but inherits from others?
        Sandbox: Runtime errors. Finite set, but also external? Strong desire for configurability.
        Toolkit: Could be Finite set. Often want to mute these and use them as conditions.

Core Commands
*************

.. automodule:: pedal.core.commands
    :members:

Report
******
    
.. automodule:: pedal.core.report
    :members:

Location
********

.. automodule:: pedal.core.location
    :members:

Feedback
********

.. automodule:: pedal.core.feedback
    :members:

**Core Feedback Functions Examples:**

The core feedback functions provide the foundation for creating educational feedback. Here are examples of the most commonly used core feedback functions:

.. code-block:: python

    from pedal import *
    
    # explain() - Basic feedback message
    explain("Your function should return a value", 
           title="Missing Return Statement")
    
    # set_success() - Positive feedback for correct solutions
    set_success("Excellent work! Your solution is correct.")
    
    # give_partial() - Award partial credit with explanation  
    give_partial(15, "Good attempt at the logic, minor calculation error")
    
    # score() - Direct score manipulation
    score("+10", "Bonus for clean code style")
    score("50%", "Partial credit for working function")
    
    # compliment() - Positive reinforcement
    compliment("Your variable names are very descriptive!")
    
    # feedback() - Generic feedback with custom parameters
    feedback("Consider using a more efficient algorithm",
            title="Performance Suggestion", 
            category="improvement",
            priority="low")

**Advanced Core Function Usage:**

.. code-block:: python

    # Conditional feedback based on student progress
    if function_exists("calculate_area"):
        result = call("calculate_area", 5)
        if result == 25:
            set_success("Perfect! Your area calculation is correct.")
        else:
            explain(f"Your function returned {result}, expected 25. "
                   f"Remember: area = side × side")
    else:
        explain("You need to define a 'calculate_area' function")
    
    # Feedback with scoring and categorization
    if "while True:" in get_program():
        explain("Your code contains an infinite loop. Consider using a for loop instead.",
               title="Infinite Loop Detected",
               category="logic_error", 
               score=-5,
               priority="high")

.. automodule:: pedal.core.feedback_category
    :members:

Environment
***********

Environments in Pedal define the context in which student code is executed and feedback is delivered. 
They configure how Pedal integrates with different autograding platforms and educational tools.

.. automodule:: pedal.core.environment
    :members:

Creating Custom Environments
-----------------------------

When creating a new environment for a custom platform, you should specify:

**Required Configuration:**

- **Name**: A unique identifier for your environment
- **Formatter**: How feedback should be formatted (HTML, plain text, Markdown)
- **Resolver**: How multiple pieces of feedback should be combined
- **Sandbox settings**: Security and execution constraints
- **File handling**: How student submissions are loaded and processed

**Basic Environment Example:**

.. code-block:: python

    from pedal.core.environment import Environment
    from pedal.resolvers.simple import resolve
    from pedal.formatters.text import TextFormatter

    class CustomEnvironment(Environment):
        def __init__(self):
            super().__init__(
                name="custom",
                formatter=TextFormatter(),
                resolver=resolve,
                skip_run=False,  # Whether to automatically run student code
                skip_tifa=False,  # Whether to run type analysis
                threaded=False   # Whether to run in separate thread
            )
        
        def setup(self):
            """Called when environment is initialized."""
            # Configure any platform-specific settings
            self.configure_sandbox_security()
            self.setup_file_handling()
        
        def configure_sandbox_security(self):
            """Configure security restrictions for student code."""
            # Disable dangerous operations
            self.disable_imports(['os', 'sys', 'subprocess'])
            self.set_execution_timeout(30)  # 30 second timeout
        
        def finalize_feedback(self, report):
            """Transform feedback for your platform."""
            feedback = self.formatter.finalize(report)
            return self.platform_specific_formatting(feedback)

**Environment Integration Points:**

1. **Submission Loading**: How files are read from your platform
2. **Code Execution**: Security and timeout configuration  
3. **Feedback Delivery**: How results are sent back to your platform
4. **Scoring Integration**: How points are calculated and reported
5. **File Management**: Handling multiple files and dependencies

**Platform-Specific Examples:**

.. code-block:: python

    # Web-based platform environment
    class WebPlatformEnvironment(Environment):
        def __init__(self):
            super().__init__(
                name="webplatform",
                formatter=HtmlFormatter(),  # Rich HTML formatting
                resolver=full_resolve,      # Show all feedback
                skip_run=False
            )
        
        def handle_submission(self, submission_data):
            """Process submission from web platform."""
            code = submission_data['code']
            student_id = submission_data['student_id']
            return self.create_submission(code, student_id=student_id)
        
        def deliver_feedback(self, feedback, student_id):
            """Send feedback back to web platform."""
            return {
                'feedback': feedback,
                'score': self.get_final_score(),
                'student_id': student_id,
                'timestamp': datetime.now().isoformat()
            }

    # Command-line environment
    class CLIEnvironment(Environment):
        def __init__(self):
            super().__init__(
                name="cli",
                formatter=TextFormatter(),  # Plain text only
                resolver=simple_resolve,    # One issue at a time
                skip_run=False
            )
        
        def print_results(self, report):
            """Print results to console."""
            feedback = self.formatter.finalize(report)
            print(feedback)
            print(f"Score: {self.get_final_score()}")

**Best Practices for Environment Development:**

1. **Security First**: Always implement proper sandboxing
2. **Error Handling**: Gracefully handle platform communication failures
3. **Timeout Management**: Prevent infinite loops and long-running code
4. **File Security**: Validate and sanitize file operations
5. **Logging**: Include detailed logging for debugging
6. **Testing**: Test with various student code scenarios

**Common Environment Patterns:**

.. code-block:: python

    def create_secure_environment():
        """Pattern for creating a secure environment."""
        env = Environment(name="secure")
        
        # Disable dangerous imports
        env.disable_imports(['os', 'sys', 'subprocess', 'eval', 'exec'])
        
        # Set resource limits
        env.set_memory_limit('100MB')
        env.set_execution_timeout(30)
        env.set_file_size_limit('1MB')
        
        # Configure feedback
        env.set_max_feedback_items(10)
        env.enable_positive_feedback(True)
        
        return env
    
    def create_teaching_environment():
        """Pattern for educational environments."""
        env = Environment(name="teaching")
        
        # Use detailed feedback
        env.set_resolver(full_resolve)
        env.set_formatter(HtmlFormatter())
        
        # Enable all analysis tools
        env.enable_tifa(True)
        env.enable_cait(True)
        env.enable_style_checking(True)
        
        # Provide helpful error messages
        env.set_error_detail_level('high')
        
        return env

Submission
***********

.. automodule:: pedal.core.submission
    :members:

Tools
*****

.. automodule:: pedal.core.tool
    :members:
