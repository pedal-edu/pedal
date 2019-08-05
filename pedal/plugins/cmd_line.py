from pedal.cait.cait_api import *
from pedal.report import MAIN_REPORT
from pedal.source import set_source
from pedal.tifa import tifa_analysis
from pedal.sandbox.compatibility import *
import importlib.util
import numpy as np
import pandas as pd

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


def process(file, module, ins_code, report):
    student_code1 = file.read()
    setup(student_code1, inputs)  # setup returns a sandbox object
    module.loader.exec_module(ins_code)
    feedback = report.feedback
    return feedback


p2Flag = True
secrets = False
assignment_id = -1
if __name__ == "__main__":
    # processing args
    feedback_code = sys.argv[1]
    code_dir = sys.argv[2]
    flag = sys.argv[3]
    if flag == "-p2":
        p2Flag = True
        inputs = sys.argv[4:]
    elif flag == "-secrets":
        p2Flag = True
        secrets = True
        inputs = sys.argv[4:]
    else:
        inputs = sys.argv[3:]
else:
    # feedback_suffix = "prequiz.py"
    # assignment_id = 409
    feedback_suffix = "postquiz1.py"
    assignment_id = 410 # Pass Count = 1
    # feedback_suffix = "postquiz2-1.py"
    # assignment_id = 411 # Pass Count = 2
    # feedback_suffix =  "postquiz2-2.py"
    # assignment_id = 412
    # feedback_code = ("C:/Users/User/Documents/Luke_Stuff/Research/ComputationalThinking/DictionaryUnit/test_cmd/"
    #                 "ins_script.py")
    feedback_code = ("C:/Users/User/Documents/Luke_Stuff/Research/ComputationalThinking/"
                     "DictionaryUnit/ID/Assessments/")
    feedback_code += feedback_suffix

    code_dir = ("C:/Users/User/Documents/Luke_Stuff/Research/ComputationalThinking/ResearchData/"
                "ComputationalThinking/Tests/results/")
    code_dir += "Spring2019/DictionaryData/cs1014_spr2019_log-v1/"
    # code_dir += "Fall2018/DictionaryData/exported-f18/"
    p2Flag = True
    secrets = True
    inputs = []

# Grabbing instructor feedback code
ins_mod = re.match("(?:.*/)(.*).py", feedback_code)[1]
my_spec = importlib.util.spec_from_file_location(ins_mod, feedback_code)
foo = importlib.util.module_from_spec(my_spec)

# preparing to process


# Grabbing student files
if p2Flag:
    student_feedback = []
    pass_count = 0
    main_table = "MainTable"
    if secrets:
        main_table += "-2"
    main_table += ".csv"
    df = pd.read_csv(code_dir + main_table)
    code_states = code_dir + "CodeStates/"
    for index, row in df.iterrows():
        scan = True
        if assignment_id >= 0:
            if secrets:
                if int(row["AssignmentID"]) != assignment_id:
                    scan = False
        if scan:
            code_f = code_states + str(int(row['CodeStateID'])) + "/__main__.py"
            # check assignment and find corresponding answer key in DictionaryUnit/ID/Assessments/...
            with open(code_f) as code:
                feedback_result = process(code, my_spec, foo, MAIN_REPORT)
                # df.at[index, 'InterventionMessage'] = feedback_result
                student_feedback.append(feedback_result)
                score = 0.0
                if not feedback_result:
                    score = 1.0
                    pass_count += 1
                df.at[index, 'Score'] = score
    df.to_csv(code_dir + "processed.csv", index=False)
else:
    student_feedback = []
    print(os.getcwd())
    student_files_base = os.listdir(code_dir)
    student_files = []
    for code_name in student_files_base:
        student_files.append(code_dir + code_name)
    for code_name in student_files:
        with open(code_name) as code_f:
            student_feedback.append(process(code_f, my_spec, foo, MAIN_REPORT))
    if __name__ == "__main__":
        print(student_feedback)
