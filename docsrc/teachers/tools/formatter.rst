.. _teacher_formatter:

Formatter
=========

.. _teacher_formatter:

Formatter
=========

**Overview**

Formatters in Pedal are responsible for converting feedback messages into the appropriate format for different environments. This is primarily used by autograding environments and platforms to ensure feedback appears correctly in their interfaces.

**When Do You Need to Know About Formatters?**

As an instructor writing grading scripts, you typically don't need to work directly with formatters. However, understanding them is useful when:

- You want to include rich formatting (code snippets, HTML, Markdown) in your feedback messages
- You're integrating Pedal with a custom environment
- You need to customize how feedback appears in different platforms
- You're debugging formatting issues in your feedback

**How Formatters Work**

Pedal uses Formatters to adapt Feedback Function :attr:`message_template` fields to different
environments. For example, it can be used to generate HTML or Markdown in web-based
environments, or just regular text for consoles.

The power of the Formatter is that it provides `conversion flags <https://docs.python.org/3/library/string.html#formatstrings>`_
for the ``message_template``. As long as the Feedback author is careful, fields can be interpolated with the appropriate
formatting.

**Basic Usage Example:**

.. code-block:: python

    from pedal import *
    
    # Simple message - works the same in all environments
    assert_equal(call("add", 1, 2), 3, message="Addition function failed")
    
    # Rich message with code formatting
    student_result = call("calculate", 5)
    assert_equal(student_result, 25, 
                message="Your function returned {actual!python_value}, expected {expected!python_value}",
                actual=student_result, expected=25)

**Conversion Flags:**

.. code-block::

    # A message_template can have fields and conversion flags:
    "Your code returned {student_answer!python_value}"

    # Which will generate the HTML output:
    "Your code returned <code>5</code>"

    # Or the plain-text output:
    "Your code returned 5"

**Environment-Specific Behavior:**

Different environments use different formatters:

- **Terminal/Console**: Plain text formatting
- **Web-based (Gradescope, BlockPy)**: HTML formatting with syntax highlighting  
- **Jupyter**: Rich HTML with enhanced styling
- **Markdown environments**: Markdown-formatted output

**Advanced Formatting Examples:**

.. code-block:: python

    from pedal import *
    
    # Format code blocks
    expected_code = "def hello():\n    print('Hello world')"
    explain("You should define a function like this:\n{code!python_code}",
           code=expected_code)
    
    # Format expressions and values
    student_expr = "2 + 2"
    result = eval(student_expr)
    explain("The expression {expr!python_expression} evaluates to {value!python_value}",
           expr=student_expr, value=result)
    
    # Custom field formatting
    explain("Test case failed: {func_name}({args}) returned {actual!python_value}, expected {expected!python_value}",
           func_name="calculate_area",
           args="5, 3", 
           actual=8,
           expected=15)

**Common Formatting Use Cases:**

.. code-block:: python

    from pedal import *
    
    def show_rich_feedback_examples():
        # 1. Code comparison
        student_code = get_program()
        if "while True:" in student_code:
            explain("""
Your code contains an infinite loop:
{problematic_code!python_code}

Consider using a different approach:
{suggested_code!python_code}
""", 
                   problematic_code="while True:\n    # This runs forever!",
                   suggested_code="for i in range(10):\n    # This runs 10 times")
        
        # 2. Variable value inspection
        student = run()
        if 'total' in student.data:
            value = student.data['total']
            explain("Your variable {var_name!python_expression} has value {var_value!python_value}",
                   var_name="total", var_value=value)
        
        # 3. Function call results
        result = call("process_list", [1, 2, 3])
        explain("Calling {func_call!python_expression} returned {result!python_value}",
                func_call="process_list([1, 2, 3])", result=result)

The following formatter classes are available:

.. class:: Formatter

    The base formatter that all others inherit from.

    .. attribute:: python_code

        A block of Python code, which might be turned into syntax highlighted code.

        Defaults to returning a block of code with 4 spaces at the start of each line.

    .. attribute:: python_expression

        A span of Python code, which might be turned into syntax highlighted code. Should not have line breaks.

        Defaults to just returning the code unchanged.

    .. attribute:: python_value

        A span of Python code, which might be turned into syntax highlighted code. Should not have line breaks.

        Defaults to just returning the code unchanged.

    .. attribute:: name

        A span of a Python name, such as the name of a function or class.

        Defaults to just returning the name unchanged.

    .. attribute:: inputs

        A block of inputs that were either entered by the user or provided to Pedal by the ICS. Meant to
        explain how a program was interacted with during execution. Think "standard input" inputs!

        Defaults to returning a block of text with 4 spaces at the start of each line, and additional new lines
        before and after the block.

    .. attribute:: output

        A block of output text that was printed by the students' program (or meant to be printed). Meant
        to explain how a program is supposed to render text during execution. Think "standard output" outputs!

        Defaults to returning a block fo text with 4 spaces at the start of each line.

    .. attribute:: line
        :type: int

        A line number in code, which might be highlighted by the environment (in which case it assumes that the
        line is in the main file). Should therefore be numeric.

        Defaults to just returning the number.

    .. attribute:: filename

        A filename, probably relevant to the project. An environment might hyperlink this to an actual file.

        Defaults to just returning the filename.

    .. attribute:: exception

        A block of an Exception trace. Mostly internal.

        Defaults to returning a block of text with 4 spaces at the start of each line.

    .. attribute:: frame

        A span of a code Frame. Mostly internal.

        Defaults to returning the text of the frame unmodified.

    .. attribute:: traceback

        A block of a traceback. Mostly internal.

        Defaults to returning the text of the frame unmodified.

    .. method:: check_mark

        A check mark symbol, to indicate the student was correct. Must be called by using the report's
        formatter, rather than as a conversion flag.

        .. code-block::

            self.report.formatter.check_mark()

        Defaults to a white space character (might be a mistake?)

    .. method:: negative_mark

        An "X" (cross) that indicates the student was incorrect. Must be called by using the report's
        formatter, rather than as a conversion flag.

        .. code-block::

            self.report.formatter.negative_mark()

        Defaults to the character ``"×"``

    .. method:: indent

        Generates an indentation in the text. Must be called by using the report's
        formatter, rather than as a conversion flag.

        .. code-block::

            self.report.formatter.negative_mark()

        Defaults to four spaces (``"    "``).

    .. method:: table(rows, columns)

        A function provided by the formatter to create a table of data. Must provide both
        the columns and rows. Has to be called by using the report's formatter, rather than as a conversion
        flag.

        .. code-block::

            self.report.formatter.table([ [10,2,3], [3,4,5] ], ["X", "Y", "Z"])

        Results in something like this by default::

            X | Y | Z
            10 | 2 | 3
            3 | 4 | 5

        :param rows: The 2D list of data to render inside the table
        :type rows: list[list[str]]
        :param columns: The 1D list of columns to render on top of the table.
        :type columns: list[str]

.. class:: TextFormatter

    Generates regular text. Default for command line environments.
    Provides no additional conversion flags over the regular :obj:`Formatter`, and uses its default behavior.


.. class:: HtmlFormatter

    Generates HTML formatted text. Default for HTML-capable environments like
    BlockPy.
