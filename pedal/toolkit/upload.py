import re
from pedal.source import get_program
from pedal.sandbox.compatibility import get_output
from pedal.report.imperative import gently_r, explain_r


# Feedback for author's name
def check_author_name_on_header():
    code = get_program()
    m_author = re.search('Author: \\w+', code)
    if not m_author:
        gently_r("You need to add your name to the author field at the top of the file.", "name_missing",
                 label="Missing Name")


def get_plots(output):
    # The p[0] is the first plot in a graph/show
    return [p[0] for p in output if isinstance(p[0], dict)]


def find_plot_of_type(plot_list, plot_type):
    return [p['data'] for p in plot_list if p['type'] == plot_type]


# Feedback for copying output of the program in the documentation
def check_output_on_header(expected_output):
    code = get_program()
    expected_output = str(expected_output)
    between_stars = code.split("*****")[2].strip()
    between_stars = "\\n".join([x.strip() for x in between_stars.split("\\n")])
    if 'REPLACE THIS TEXT WITH THE OUTPUT OF THIS PROGRAM' in between_stars:
        gently_r("In your code, you need to 'REPLACE THIS TEXT WITH THE OUTPUT OF THIS PROGRAM'", "wrong_output_blank",
                 label="Blank Output")
    elif expected_output not in between_stars:
        gently_r("The output you copied between the *****, seems to be incorrect. "
                 "You may have copied it into the wrong location, or it is incomplete.", "wrong_output_fill", label="")


def check_problem_submission(prob_id):
    if prob_id not in get_program():
        explain_r("Make sure that you are turning in {}</br>".format(prob_id), "wrong_problem", label="Wrong Problem")
        return True


def check_print_output(multiple_lines):
    for line in multiple_lines:
        if line not in get_output():
            gently_r("You are not doing the correct calculation</br>", "catch_all", label="Wrong Output")
            return True


def find_in_code(regex):
    code = get_program()
    return re.search(regex, code)
