import re
from pedal.source import get_program
from pedal.sandbox.compatibility import get_output
from pedal.report.imperative import gently, explain


# Feedback for author's name
def check_author_name_on_header():
    code = get_program()
    m_author = re.search('Author: \\w+', code)
    if not m_author:
        gently("You need to add your name to the author field at the top of the file."
               "<br><br><i>(name_missing)<i></br></br>")


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
        gently("In your code, you need to 'REPLACE THIS TEXT WITH THE OUTPUT OF THIS PROGRAM'"
               "<br><br><i>(wrong_output_blank)<i></br></br>")
    elif expected_output not in between_stars:
        gently("The output you copied between the *****, seems to be incorrect. You may have copied it into the wrong "
               "location, or it is incomplete.<br><br><i>(wrong_output_fill)<i></br></br>")


def check_problem_submission(prob_id):
    if prob_id not in get_program():
        explain("Make sure that you are turning in {}<br><br><i>(wrong_problem)<i></br></br>".format(prob_id))
        return True


def check_print_output(multiple_lines):
    for line in multiple_lines:
        if line not in get_output():
            gently("You are not doing the correct calculation<br><br><i>(catch_all)<i></br></br>")
            return True


def find_in_code(regex):
    code = get_program()
    return re.search(regex, code)
