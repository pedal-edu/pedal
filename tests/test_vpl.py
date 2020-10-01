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
from pedal.core.commands import compliment, clear_report, contextualize_report


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


    def test_sections(self):
        vpl = VPLEnvironment(main_file=here+'datafiles/student_example.py')
        separate_into_sections()
        with io.StringIO() as f, redirect_stdout(f):
            vpl.resolve()
            self.assertEqual("NoSectionalErrors", f.getvalue())

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

    def test_resolve(self):
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
            vpl.resolve()
            self.assertEqual("""<|--
-##### Part 1
-##### Part 2
Hey, not a bad job!
-##### Part 3
Invalid syntax on line 15

-Overall
Incomplete
--|>
Grade :=>> 0""", f.getvalue())


if __name__ == '__main__':
    unittest.main(buffer=False)
