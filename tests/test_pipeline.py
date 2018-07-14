################################################################################
# BlockPy Examples
from teacher import *
    # get_output, set_success, gently, explain
    # set_environment, tifa_analysis, misconceptions
set_environment('blockpy')
tifa_analysis()

misconceptions.filter_group()
misconceptions.append.append_group()

if 'text' in get_output():
    gently("Hey now...")
set_success()

feedback.resolve()
    # Runs the feedback dispatcher, figures out what the HTML string is
    # Calls blockpy.set_feedback(result)
    
################################################################################
# Jupyter Notebooks
from teacher import set_environment, misconceptions
set_environment('jupyter')
from teacher.plugins.jupyter import *
'Largely the same as above'

feedback.resolve()
    # Runs the feedback dispatcher, figures out what the HTML string is
    # Calls the relevant markdown generating functions
    # Probably suppresses print? I feel like it's asking for trouble.

################################################################################
# WebCAT
import teacher
teacher.set_environment('webcat')
from teacher.plugins.webcat import *

class TestEverything(WebCATTest):
    title = "Try out all the functions."
    def test_plotting(self):
        student = teacher.load('student_code.py')
        self.assertIn('name', student.variables)
        self.assertIn('summate', student.functions,
                      "You haven't created a summate function.")
        student.run('summate', [1,2,3])
        self.assertEquals(student._, 6)
        
run_unit_tests(TestEverything)

feedback.resolve()

# 