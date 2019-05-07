from pedal.cait.cait_api import *
from pedal.report import MAIN_REPORT
from pedal.source import set_source
from pedal.tifa import tifa_analysis
from pedal.sandbox.compatibility import *
import importlib.util

import sys
import os
import re


def setup(student_code, input_vals):
    """
    Clears MAIN_REPORT, sets source, and runs TIFA
    Args:
        student_code: String of student code
        input_vals: list of inputs to be queued.
    Returns:
        None
    """
    MAIN_REPORT.clear()
    set_source(student_code)
    tifa_analysis()
    if len(input_vals) != 0:
        queue_input(*input_vals)
    run_student(True)
    return get_sandbox()


if __name__ == "__main__":
    # processing args
    feedback_code = sys.argv[1]
    code_dir = sys.argv[2]
    inputs = sys.argv[3:]
else:
    feedback_code = ("C:/Users/User/Documents/Luke_Stuff/Research/ComputationalThinking/DictionaryUnit/test_cmd/"
                     "ins_script.py")
    code_dir = "C:/Users/User/Documents/Luke_Stuff/Research/ComputationalThinking/DictionaryUnit/test_cmd/students/"
    inputs = []

# Grabbing instructor feedback code
ins_mod = re.match("(?:.*/)(.*).py", feedback_code)[1]
my_spec = importlib.util.spec_from_file_location(ins_mod, feedback_code)
foo = importlib.util.module_from_spec(my_spec)

# Grabbing folder of student files
print(os.getcwd())
student_files = os.listdir(code_dir)

# preparing to process
student_feedback = []
report = MAIN_REPORT

for code_name in student_files:
    with open(code_dir + code_name) as code_f:
        student_code1 = code_f.read()
        student = setup(student_code1, inputs)
        my_spec.loader.exec_module(foo)
        feedback = report.feedback
        student_feedback.append(feedback)

if __name__ == "__main__":
    print(student_feedback)
