import os
import sys
import io
from contextlib import redirect_stdout

pedal_library = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, pedal_library)

here = "" if os.path.basename(os.getcwd()) == "tests" else "tests/"

from tests.execution_helper import ExecutionTestCase
from pedal.environments.nbgrader import setup_environment
from pedal.source import next_section, verify_section, check_section_exists, set_source_file, separate_into_sections
from pedal.core.commands import compliment, clear_report, contextualize_report, log
from pedal.assertions import assert_equal, prevent_ast


class TestNBGrader(ExecutionTestCase):

    def test_parse_file(self):
        with io.StringIO() as f, redirect_stdout(f):
            nbgrader = setup_environment("*", main_file=here+'datafiles/jupyter_notebook_example.ipynb')
            print(nbgrader.report.submission.main_code)
            self.assertEqual('''def squares(n):
    """Compute the squares of numbers from 1 to n, such that the 
    ith element of the returned list equals i^2.
    
    """
    ### BEGIN SOLUTION
    if n < 1:
        raise ValueError("n must be greater than or equal to 1")
    return [i ** 2 for i in range(1, n + 1)]
    ### END SOLUTION
''', f.getvalue())

    def test_parse_whole_file(self):
        with io.StringIO() as f, redirect_stdout(f):
            nbgrader = setup_environment("**", main_file=here + 'datafiles/jupyter_notebook_example.ipynb')
            print(nbgrader.report.submission.main_code)
            self.assertEqual('''"""For this problem set, we'll be using the Jupyter notebook:

![](jupyter.png)"""
"""---
## Part A (2 points)

Write a function that returns a list of numbers, such that $x_i=i^2$, for $1\leq i \leq n$. Make sure it handles the case where $n<1$ by raising a `ValueError`."""
def squares(n):
    """Compute the squares of numbers from 1 to n, such that the 
    ith element of the returned list equals i^2.
    
    """
    ### BEGIN SOLUTION
    if n < 1:
        raise ValueError("n must be greater than or equal to 1")
    return [i ** 2 for i in range(1, n + 1)]
    ### END SOLUTION
"""Your function should print `[1, 4, 9, 16, 25, 36, 49, 64, 81, 100]` for $n=10$. Check that it does:"""
squares(10)
"""Check that squares returns the correct output for several inputs"""
assert squares(1) == [1]
assert squares(2) == [1, 4]
assert squares(10) == [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]
assert squares(11) == [1, 4, 9, 16, 25, 36, 49, 64, 81, 100, 121]
from pedal import *
from pedal.environments.nbgrader import setup_environment

if setup_environment('squares'):
    prevent_ast("If")
    prevent_ast("If")
    prevent_embedded_answer(1)
    prevent_import('numpy')


"""Check that squares raises an error for invalid inputs"""
try:
    squares(0)
except ValueError:
    pass
else:
    raise AssertionError("did not raise")

try:
    squares(-4)
except ValueError:
    pass
else:
    raise AssertionError("did not raise")
''', f.getvalue())

    def test_check_file(self):
        with io.StringIO() as f, redirect_stdout(f):
            nbgrader = setup_environment("*", main_file=here + 'datafiles/jupyter_notebook_example.ipynb')
            with self.assertRaises(AssertionError) as ae:
                prevent_ast("If")
            self.assertEqual("You used an IF statement on line 7. You may not use that.", str(ae.exception))
