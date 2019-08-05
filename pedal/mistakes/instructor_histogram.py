from pedal.cait.cait_api import find_match, find_matches, data_state
from pedal.report.imperative import gently_r, explain_r


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

    Returns:
    """
    message = "The program should display a histogram."
    code = "histo_missing"
    tldr = "Missing Histogram"
    match = find_match("plt.hist(___)")
    if not match:
        return explain_r(message, code, label=tldr)
    return False


def plot_show_missing():
    """
    Name: plot_show_missing
    Pattern:
    Missing
       plt.show()

    Feedback: The plot must be explicitly shown to appear in the Printer area.

    Returns:
    """
    message = "The plot must be explicitly shown to appear in the Printer area."
    code = "plot_show_missing"
    tldr = "No Plot Shown"
    match = find_match("plt.show()")
    if not match:
        return explain_r(message, code, label=tldr)
    return False


def histogram_argument_not_list():
    """

    Name: histogram_argument_not_list
    Pattern:
       plt.hist(<argument>)
    Where type(<argument>) is not "list"

    Feedback: Making a histogram requires a list; <argument> is not a list.


    Returns:
    """
    message = "Making a histogram requires a list; <code>{0!s}</code> is not a list."
    code = "hist_arg_not_list"
    tldr = "Making Histogram from Non-list"
    matches = find_matches("plt.hist(_argument_)")
    if matches:
        for match in matches:
            _argument_ = match["_argument_"].astNode
            if not _argument_.get_data_state() or not _argument_.get_data_state().was_type('list'):
                return explain_r(message.format(_argument_.id), code, label=tldr)
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

    Returns:
    """
    message = "The list created in the iteration is not the list being used to create the histogram."
    code = "histo_wrong_list"
    tldr = "Plotting Wrong List"
    matches = find_matches("for ___ in ___:\n"
                           "    __expr__\n"
                           "plt.hist(_list_)")
    if matches:
        for match in matches:
            _list_ = match["_list_"].astNode
            __expr__ = match["__expr__"]
            submatches = __expr__.find_matches("_list_.append(___)")
            if submatches:
                return False
        return explain_r(message, code, label=tldr)
    return False


def histogram_wrong_placement():
    message = "The histogram should be plotted only once, after the new list has been created"
    code = "histo_wrong_place"
    tldr = "Histogram Plot Placed Incorrectly"
    matches = find_matches("for ___ in ___:\n"
                           "    pass\n")
    if matches:
        matches02 = find_matches("plt.hist(___)")
        for match in matches:
            if matches02:
                for match02 in matches02:
                    if match02.match_lineno > match.match_lineno:
                        return False
    return explain_r(message, code, label=tldr)
