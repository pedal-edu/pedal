################################################################################
# BlockPy Examples
# In JS, patch `get_program`
from pedal.report import *
    # get_output, set_success, gently, explain
from pedal.tifa import tifa_analysis()
    # tifa_analysis
from pedal.mistakes import mistakes
    # misconceptions
tifa_analysis()

mistakes.filter_group()
mistakes.append.append_group()

if 'text' in get_output():
    gently("Hey now...")
set_success()

import pedal.feedback as feedback
_RESULT = feedback.select()
_PARTIALS = sum_partials()
    # Runs the feedback dispatcher, figures out what the HTML string is
    # Have to access the _RESULT from 
    # Calls blockpy.set_feedback(result)
    
################################################################################
# Jupyter Notebooks
from pedal.report import *
    # get_output, set_success, gently, explain
from pedal.tifa import tifa_analysis()
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