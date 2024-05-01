import os
import sys
import io
from contextlib import redirect_stdout
import unittest

from pedal import MAIN_REPORT, call
from pedal.utilities.system import IS_AT_LEAST_PYTHON_311

pedal_library = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, pedal_library)

here = "" if os.path.basename(os.getcwd()) == "tests" else "tests/"

from tests.execution_helper import ExecutionTestCase
from pedal.environments.terminal import setup_environment
from pedal.source import next_section, verify_section, check_section_exists, set_source_file, separate_into_sections
from pedal.core.commands import compliment, clear_report, contextualize_report, log, explain
from pedal.assertions import assert_equal, prevent_ast


class TestEnvironmentTerminal(ExecutionTestCase):

    def checkFeedback(self, actual, expected):
        self.assertEqual(expected.strip(), actual.strip())

    def test_correct(self):
        with io.StringIO() as f, redirect_stdout(f):
            terminal = setup_environment(main_code="""1+2""")
            terminal.resolve()
            clear_report()
            self.checkFeedback(f.getvalue(), '''
[;7m YOUR CODE [0;0m We ran your code. Here's the output:


[;7m FEEDBACK [0;0m Based on your code, here are some tips and recommendations:

[1;92m✓[0;0m️  Your code ran successfully.

Great work! Based on your code submitted, there are no other recommendations available. You can proceed to the next page by using the “Next” button in your lesson.
''')

    def test_empty_source(self):
        with io.StringIO() as f, redirect_stdout(f):
            terminal = setup_environment(main_code="")
            terminal.resolve()
            clear_report()
            self.checkFeedback(f.getvalue(), '''
[;7m YOUR CODE [0;0m We ran your code. Here's the output:


[;7m FEEDBACK [0;0m Based on your code, here are some tips and recommendations:

[1;91m✗[0;0m  No Source Code

Source code file is blank.
''')

    def test_syntax_error(self):
        with io.StringIO() as f, redirect_stdout(f):
            terminal = setup_environment(main_code="""1 1 2 3""")
            terminal.resolve()
            clear_report()
            self.checkFeedback(f.getvalue(), '''
[;7m YOUR CODE [0;0m We ran your code. Here's the output:


[;7m FEEDBACK [0;0m Based on your code, here are some tips and recommendations:

[1;91m✗[0;0m  Syntax Error

Bad syntax on line [4m1[0;0m.
Suggestion: Check line [4m1[0;0m, the line before it, and the line after it. Ignore blank lines.

[;7m TERMINAL OUTPUT [0;0m For reference, here is the original Python error:

Line [4m1[0;0m of file [4manswer.py[0;0m
    1 1 2 3
''' + ('      ^\n' if IS_AT_LEAST_PYTHON_311 else "") + '''
SyntaxError: Invalid syntax.
''')

    def test_tifa_feedback(self):
        with io.StringIO() as f, redirect_stdout(f):
            terminal = setup_environment(main_code="""1+''""")
            terminal.resolve()
            clear_report()
            self.checkFeedback(f.getvalue(), '''
[;7m YOUR CODE [0;0m We ran your code. Here's the output:


[;7m FEEDBACK [0;0m Based on your code, here are some tips and recommendations:

[1;91m✗[0;0m  Incompatible types

You used an addition operation with an integer and a string on line [4m1[0;0m. But you can't do that with that operator. Make sure both sides of the operator are the right type.

[;7m TERMINAL OUTPUT [0;0m For reference, here is the original Python error:

Line [4m1[0;0m of file [4manswer.py[0;0m
    1+''
''' + ('    ^^^^\n' if IS_AT_LEAST_PYTHON_311 else "") + '''
TypeError: Unsupported operand type(s) for +: 'int' and 'str'
    ''')

    def test_runtime_feedback(self):
        with io.StringIO() as f, redirect_stdout(f):
            terminal = setup_environment(main_code="""import json\njson.loads('1')+''""")
            terminal.resolve()
            clear_report()
            self.checkFeedback(f.getvalue(), '''
[;7m YOUR CODE [0;0m We ran your code. Here's the output:


[;7m FEEDBACK [0;0m Based on your code, here are some tips and recommendations:

[1;91m✗[0;0m  Type Error

I ran your code.

A TypeError occurred:

    Unsupported operand type(s) for +: 'int' and 'str'

Type errors occur when you use an operator or function on the wrong type of value. For example, using `+` to add to a list (instead of `.append`), or dividing a string by a number.

Suggestion: To fix a type error, you should trace through your code. Make sure each expression has the type you expect it to have.

[;7m TERMINAL OUTPUT [0;0m For reference, here is the original Python error:

Line [4m2[0;0m of file [4manswer.py[0;0m
    json.loads('1')+''
''' + ('    ^^^^^^^^^^^^^^^^^^\n' if IS_AT_LEAST_PYTHON_311 else "") + '''
TypeError: Unsupported operand type(s) for +: 'int' and 'str'
''')

    def test_explain(self):
        with io.StringIO() as f, redirect_stdout(f):
            terminal = setup_environment(main_code="""import json\njson.loads('1')+''""")
            explain("You should not be using the JSON library at all.")
            terminal.resolve()
            clear_report()
            self.checkFeedback(f.getvalue(), '''
[;7m YOUR CODE [0;0m We ran your code. Here's the output:


[;7m FEEDBACK [0;0m Based on your code, here are some tips and recommendations:

[1;91m✗[0;0m  Instructor Feedback

You should not be using the JSON library at all.

[;7m TERMINAL OUTPUT [0;0m For reference, here is the original Python error:

Line [4m2[0;0m of file [4manswer.py[0;0m
    json.loads('1')+''
''' + ('    ^^^^^^^^^^^^^^^^^^\n' if IS_AT_LEAST_PYTHON_311 else "") + '''
TypeError: Unsupported operand type(s) for +: 'int' and 'str'
''')


    def test_call_assertion(self):
        with io.StringIO() as f, redirect_stdout(f):
            terminal = setup_environment(main_code="""def x(): return 1+''\nx""")
            assert_equal(call('x'), 5)
            terminal.resolve()
            clear_report()
            self.checkFeedback(f.getvalue(), '''
[;7m YOUR CODE [0;0m We ran your code. Here's the output:


[;7m FEEDBACK [0;0m Based on your code, here are some tips and recommendations:

[1;91m✗[0;0m  Type Error

I ran the code:
    x()

A TypeError occurred:

    Unsupported operand type(s) for +: 'int' and 'str'

Type errors occur when you use an operator or function on the wrong type of value. For example, using `+` to add to a list (instead of `.append`), or dividing a string by a number.

Suggestion: To fix a type error, you should trace through your code. Make sure each expression has the type you expect it to have.

[;7m TERMINAL OUTPUT [0;0m For reference, here is the original Python error:

Line [4m1[0;0m of file [4manswer.py[0;0m in x
    def x(): return 1+''
''' + ('                    ^^^^\n' if IS_AT_LEAST_PYTHON_311 else "") + '''
TypeError: Unsupported operand type(s) for +: 'int' and 'str'
''')