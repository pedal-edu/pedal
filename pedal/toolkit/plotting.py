from pedal.toolkit.utilities import function_is_called
from pedal.cait.cait_api import parse_program, def_use_error
from pedal.report.imperative import explain, gently
from pedal.sandbox import compatibility

PLOT_LABEL = {'plot': 'line plot',
              'hist': 'histogram',
              'scatter': 'scatter plot'}


def prevent_incorrect_plt():
    ast = parse_program()
    plts = [n for n in ast.find_all("Name") if n.id == 'plt']
    if plts and def_use_error(plts[0]):
        explain("You have imported the <code>matplotlib.pyplot</code> module, "
                "but you did not rename it to <code>plt</code> using "
                "<code>import matplotlib.pyplot as plt</code>.<br><br><i>(plt_rename_err)<i>", 'verifier')
        return True
    matplotlib_names = ['plot', 'hist', 'scatter',
                        'title', 'xlabel', 'ylabel', 'show']
    for name in matplotlib_names:
        for n in ast.find_all("Name"):
            if n.id == name:
                if def_use_error(n):
                    explain(("You have attempted to use the MatPlotLib "
                             "function named <code>{0}</code>. However, you "
                             "imported MatPlotLib in a way that does not "
                             "allow you to use the function directly. I "
                             "recommend you use <code>plt.{0}</code> instead, "
                             "after you use <code>import matplotlib.pyplot as "
                             "plt</code>.<br><br><i>(plt_wrong_import)<i>").format(name), 'verifier')
                    return True
    return False


def ensure_correct_plot(function_name):
    for a_plot, label in PLOT_LABEL.items():
        if function_name == a_plot:
            if not function_is_called(function_name):
                gently("You are not calling the <code>{func_name}</code> function."
                       "<br><br><i>(no_{func_name}_call)<i>".format(func_name=function_name))
                return True
        elif function_is_called(a_plot):
            gently("You have called the <code>{}</code> function, which makes a {}."
                   "<br><br><i>(wrong_plt)<i>".format(a_plot, label))
            return True
    return False


def ensure_show():
    if not function_is_called("show"):
        gently("You have not called <code>show</code> function, which "
               "actually creates the graph.<br><br><i>(no_show)<i>")
        return True
    return False


def compare_data(plt_type, correct, given):
    """
    Determines whether the given data matches any of the data found in the
    correct data. This handles plots of different types: if a histogram
    was plotted with the expected data for a line plot, it will return True.

    Args:
        plt_type (str): The expected type of this plot
        correct (List of Int or List of List of Int): The expected data.
        given (Dict): The actual plotted data and information
    Returns:
        bool: Whether the correct data was found in the given plot.
    """
    # Infer arguments
    if plt_type == 'hist':
        correct_xs = None
        correct_ys = correct
    elif not correct:
        correct_xs = []
        correct_ys = []
    elif isinstance(correct[0], (tuple, list)):
        # We were given a list of lists of ints
        correct_xs, correct_ys = correct
    else:
        # Assume it is a singular list
        correct_xs = list(range(len(correct)))
        correct_ys = correct

    if given['type'] == 'hist':
        return correct_ys == given['values']
    elif plt_type == 'hist':
        return correct_ys == given['y']
    else:
        return correct_xs == given['x'] and correct_ys == given['y']


GRAPH_TYPES = {'line': 'line plot',
               'hist': 'histogram',
               'scatter': 'scatter plot'}


def check_for_plot(plt_type, data):
    """
    Returns any errors found for this plot type and data.
    In other words, if it returns False, the plot was found correctly.
    """
    if plt_type == 'plot':
        plt_type = 'line'
    type_found = False
    data_found = False
    for graph in compatibility.get_plots():
        for a_plot in graph['data']:
            data_found_here = compare_data(plt_type, data, a_plot)
            if a_plot['type'] == plt_type and data_found_here:
                return False
            if a_plot['type'] == plt_type:
                type_found = True
            if data_found_here:
                data_found = True
    plt_type = GRAPH_TYPES.get(plt_type, plt_type)
    if type_found and data_found:
        return ("You have created a {}, but it does not have the right data. That data appears to have been plotted "
                "in another graph.<br><br><i>(other_plt)<i>".format(plt_type))
    elif type_found:
        return ("You have created a {}, but it does not have the right data."
                "<br><br><i>(wrong_plt_data)<i>".format(plt_type))
    elif data_found:
        return ("You have plotted the right data, but you appear to have not plotted it as a {}."
                "<br><br><i>(wrong_plt_type)<i>".format(plt_type))
    else:
        return ("You have not created a {} with the proper data."
                "<br><br><i>(no_plt)<i>".format(plt_type))
