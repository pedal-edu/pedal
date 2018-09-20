from pedal.cait.cait_api import *
from pedal.report.imperative import *


def histogram_group():
    histogram_argument_not_list()
    histogram_wrong_list()
    histogram_missing()
    plot_show_missing()


def histogram_missing():
    """
    Name: histogram_missing
    Pattern:

    Missing
       plt.hist(___)

    Feedback: The program should display a histogram.

    :return:
    """
    match = find_match("plt.hist(___)")
    if not match:
        explain("The program should display a histogram.<br><br><i>(histo_missing)<i></br>")
        return True
    return False


def plot_show_missing():
    """
    Name: plot_show_missing
    Pattern:
    Missing
       plt.show()

    Feedback: The plot must be explicitly shown to appear in the Printer area.

    :return:
    """
    match = find_match("plt.show()")
    if not match:
        explain("The plot must be explicitly shown to appear in the Printer area."
                "<br><br><i>(plot_show_missing)<i></br>")
        return True
    return False


def histogram_argument_not_list():
    """

    Name: histogram_argument_not_list
    Pattern:
       plt.hist(<argument>)
    Where type(<argument>) is not "list"

    Feedback: Making a histogram requires a list; <argument> is not a list.


    :return:
    """
    matches = find_matches("plt.hist(_argument_)")
    if matches:
        for match in matches:
            _argument_ = match.symbol_table.get("_argument_")[0].astNode
            if not data_state(_argument_).was_type('list'):
                explain("Making a histogram requires a list; <code>{0!s}</code> is not a list.<br><br><i>"
                        "(hist_arg_not_list)<i></br>".format(_argument_.id))
                return True
    return False


def histogram_wrong_list():
    """

    Name: histogram_wrong_list
    Pattern:

    for ___ in ___:
       <target>.append(___)
    plt.hist(<list>)

    where name(<target>) != name(<list>)

    Feedback: The list created in the iteration is not the list being used to create the histogram.

    :return:
    """
    matches = find_matches("for ___ in ___:\n"
                           "    __expr__\n"
                           "plt.hist(_list_)")
    if matches:
        for match in matches:
            _list_ = match.symbol_table.get("_list_")[0].astNode
            __expr__ = match.exp_table.get("__expr__")
            submatches = find_expr_sub_matches("{}.append(___)".format(_list_.id), __expr__)
            if submatches:
                return False
        explain(
            "The list created in the iteration is not the list being used to create the histogram.<br><br><i>"
            "(histo_wrong_list)<i></br>")
        return True
    return False


def histogram_wrong_placement():
    matches = find_matches("for ___ in ___:\n"
                           "    pass\n")
    if matches:
        matches02 = find_matches("plt.hist(___)")
        for match in matches:
            if matches02:
                for match02 in matches02:
                    if match02.match_lineno > match.match_lineno:
                        return False
    explain("The histogram should be plotted only once, after the new list has been created"
            "<br><br><i>(histo_wrong_place)<i></br>")
    return True
