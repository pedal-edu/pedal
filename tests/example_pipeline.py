################################################################################
# BlockPy Examples
# Boiler plate code automatically prepended before execution
# Import get_output, set_success, gently, explain
from pedal.core import *
# In JS, patch `get_program`, and then imperative define the report's source
report.set_source(get_program())
# Run the tifa analysis; stuff is automatically added to the report
from pedal.tifa import tifa_analysis()
_tifa = tifa_analysis()

# Set up CAIT to know about TIFA
import pedal.cait as cait
cait.configure(tifa=_tifa)

# End of boiler plate

# Minor modifications to pathing for the instructor_* stuff
from pedal.mistakes import mistakes
mistakes.filter_group()
mistakes.append.append_group()

# But most code left unchanged
if 'text' in get_output():
    gently("Hey now...")
set_success()

# Boilerplate begins again.
import pedal.feedback as feedback
_RESULT = feedback.select()
_PARTIALS = sum_partials()
    # Runs the feedback dispatcher, figures out what the HTML string is
    # Have to access the _RESULT from 
    # Calls blockpy.set_feedback(_RESULT, _PARTIALS)
    
################################################################################
# Jupyter Notebooks
from pedal.core import *
report.set_source(STUDENT_SOURCE)
    # get_output, set_success, gently, explain
from pedal.tifa import tifa_analysis
    # tifa_analysis
from pedal.mistakes import mistakes
    # misconceptions
tifa_analysis()

import pedal.feedback as feedback
from IPython.display import display, HTML
display(HTML(_RESULT))
    # Runs the feedback dispatcher, figures out what the HTML string is
    # Calls the relevant markdown generating functions
    # Probably suppresses print? I feel like it's asking for trouble.

################################################################################
# WebCAT
from pedal.sandbox import load
from pedal.environments.webcat import WebCATTest, run_unit_tests, TifaTest

class TestEverything(WebCATTest):
    title = "Try out all the functions."
    def test_plotting(self):
        student = load('student_code.py')
        self.assertIn('name', student.variables)
        self.assertIn('summate', student.functions,
                      "You haven't created a summate function.")
        student.run('summate', [1,2,3])
        self.assertEquals(student._, 6)
        
run_unit_tests(TifaTest, TestEverything)
# 