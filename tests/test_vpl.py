import unittest
import os
import sys
from textwrap import dedent
from contextlib import redirect_stdout
import io

from pedal import verify, run

pedal_library = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, pedal_library)

here = "" if os.path.basename(os.getcwd()) == "tests" else "tests/"

from tests.execution_helper import ExecutionTestCase
from pedal.environments.vpl import VPLEnvironment, VPLFormatter, resolve
from pedal.source import next_section, verify_section, check_section_exists, set_source_file, separate_into_sections
from pedal.core.commands import compliment, clear_report, contextualize_report, log
from pedal.assertions import assert_equal


class TestVPL(ExecutionTestCase):

    def test_vpl_loads_with_syntax_error(self):
        vpl = VPLEnvironment(main_file=here+'datafiles/student_example.py')
        with io.StringIO() as f, redirect_stdout(f):
            vpl.resolve()
            self.assertEqual("""<|--
-Syntax Error
Bad syntax on line 15

The traceback was:
Line 15 of file datafiles/student_example.py
>a syntax error in this section!


Suggestion: Check line 15, the line before it, and the line after it.
--|>
Grade :=>> 0
""", f.getvalue())

    def test_file_not_found(self):
        vpl = VPLEnvironment(main_file=here + 'datafiles/banana_cream_pudding.py')
        with io.StringIO() as f, redirect_stdout(f):
            vpl.resolve()
            self.assertEqual("""<|--
-Source File Not Found
The given filename datafiles/banana_cream_pudding.py was either not found or could not be opened. Please make sure the file is available.
--|>
Grade :=>> 0
""", f.getvalue())

    def test_simple_system(self):
        clear_report()
        vpl = VPLEnvironment(main_code='1+2')
        with io.StringIO() as f, redirect_stdout(f):
            log("Message Printed")
            assert_equal(1, 2)
            vpl.resolve()
            self.assertEqual("""<|--
-System Notes
Message Printed
-Failed Instructor Test
Student code failed instructor test.
>1 != 2
--|>
Grade :=>> 0
""", f.getvalue())

    def test_simple_system_correct(self):
            clear_report()
            vpl = VPLEnvironment(main_code='1+2')
            with io.StringIO() as f, redirect_stdout(f):
                log("Message Printed")
                vpl.resolve()
                self.assertEqual("""<|--
-System Notes
Message Printed
-Complete
Great work!
--|>
Grade :=>> 1
""", f.getvalue())

    def test_resolve(self):
        clear_report()
        vpl = VPLEnvironment(main_file=here+'datafiles/student_example.py')
        separate_into_sections()
        # Part 0 - usually skipped
        # Part 1
        vpl.next_section()
        # Part 2
        vpl.next_section()
        compliment('Hey, not a bad job!')
        # Part 3
        vpl.next_section()
        # Part 4
        vpl.next_section()
        # Resolve entire thing
        with io.StringIO() as f, redirect_stdout(f):
            vpl.sectional_resolve()
            self.assertEqual("""<|--
-Part 0
No feedback for this section
-Part 1
No feedback for this section
-Part 2
Complete
Great work!
-Part 3
Syntax Error
Bad syntax on line 15

The traceback was:
Line 15 of file datafiles/student_example.py
>a syntax error in this section!


Suggestion: Check line 15, the line before it, and the line after it.
-Part 4
No feedback for this section
--|>
Grade :=>> 1
""", f.getvalue())


if __name__ == '__main__':
    unittest.main(buffer=False)
