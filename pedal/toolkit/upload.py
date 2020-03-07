import re
from pedal.source import get_program
from pedal.sandbox.compatibility import get_output
from pedal.core.commands import gently, explain

# TODO: Move this into the CS1014 package!


# Feedback for author's name
def check_author_name_on_header():
    """

    """
    code = get_program()
    m_author = re.search('Author: \\w+', code)
    if not m_author:
        gently("You need to add your name to the author field at the top of the file.", label="name_missing",
                 title="Missing Name")


def get_plots(output):
    """

    Args:
        output:

    Returns:

    """
    # The p[0] is the first plot in a graph/show
    return [p[0] for p in output if isinstance(p[0], dict)]


def find_plot_of_type(plot_list, plot_type):
    """

    Args:
        plot_list:
        plot_type:

    Returns:

    """
    return [p['data'] for p in plot_list if p['type'] == plot_type]


# Feedback for copying output of the program in the documentation
def check_output_on_header(expected_output):
    """

    Args:
        expected_output:
    """
    code = get_program()
    expected_output = str(expected_output)
    between_stars = code.split("*****")[2].strip()
    between_stars = "\\n".join([x.strip() for x in between_stars.split("\\n")])
    if 'REPLACE THIS TEXT WITH THE OUTPUT OF THIS PROGRAM' in between_stars:
        gently("In your code, you need to 'REPLACE THIS TEXT WITH THE OUTPUT OF THIS PROGRAM'",
               label="wrong_output_blank",
               title="Blank Output")
    elif expected_output not in between_stars:
        gently("The output you copied between the *****, seems to be incorrect. "
               "You may have copied it into the wrong location, or it is incomplete.",
               label="wrong_output_fill", title="Missing Output")


def check_problem_submission(prob_id):
    """

    Args:
        prob_id:

    Returns:

    """
    if prob_id not in get_program():
        explain("Make sure that you are turning in {}</br>".format(prob_id),
                label="wrong_problem", title="Wrong Problem")
        return True


def check_print_output(multiple_lines):
    """

    Args:
        multiple_lines:

    Returns:

    """
    for line in multiple_lines:
        if line not in get_output():
            gently("You are not doing the correct calculation</br>", label="catch_all", title="Wrong Output")
            return True


def find_in_code(regex):
    """

    Args:
        regex:

    Returns:

    """
    code = get_program()
    return re.search(regex, code)
