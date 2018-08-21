from pedal.toolkit.utilities import *
from pedal.cait.cait_api import *
from pedal.sandbox import compatibility


PLOT_LABEL = {'plot': 'line plot', 
              'hist': 'histogram', 
              'scatter': 'scatter plot'}


def prevent_incorrect_plt():
    ast = parse_program()
    plts = [n for n in ast.find_all("Name") if n.id == 'plt']
    if plts and def_use_error(plts[0]):
        explain("You have imported the <code>matplotlib.pyplot</code> module, but you did not rename it to <code>plt</code> using <code>import matplotlib.pyplot as plt</code>.", 'verifier')
        return True
    for name in ['plot', 'hist', 'scatter', 'title', 'xlabel', 'ylabel', 'show']:
        for n in ast.find_all("Name"):
            if n.id == name:
                if def_use_error(n):
                    explain("You have attempt to use the MatPlotLib function named <code>{0}</code>. However, you imported MatPlotLib in a way that does not allow you to use the function directly. I recommend you use <code>plt.{0}</code> instead, after you use <code>import matplotlib.pyplot as plt</code>.".format(name), 'verifier')
                    return True
    return False
    
def ensure_correct_plot(function_name):
    for a_plot, label in PLOT_LABEL.items():
        if function_name == a_plot:
            if not function_is_called(function_name):
                gently("You are not calling the <code>{}</code> function.".format(function_name))
                return True
        elif function_is_called(a_plot):
            gently("You have called the <code>{}</code> function, which makes a {}.".format(a_plot, label))
            return True
    return False

def ensure_show():
    if not function_is_called("show"):
        gently("You have not called <code>show</code> function, which "
               "actually creates the graph.")
        return True
    return False

def compare_data(type, correct, given):
    if type == 'hist' and given['type'] == 'hist':
        return correct == given['values']
    elif type == 'hist':
        return correct == given['y']
    elif not correct: # TODO: Why this?
        return False
    elif isinstance(correct[0], list):
        if len(correct[0]) != len(given['x']):
            return False
        for given_x, correct_x in zip(correct[0], given['x']):
            if given_x != correct_x:
                return False
        for given_y, correct_y in zip(correct[1], given['y']):
            if given_y != correct_y:
                return False
        return True
    elif len(given) != len(correct):
        return False
    else:
        for x, (gx, gy, c) in enumerate(zip(given['x'], given['y'], correct)):
            if c != gy or x != gx:
                return False
    return True
            

GRAPH_TYPES = {'line': 'line plot', 
              'hist': 'histogram', 
              'scatter': 'scatter plot'}
def check_for_plot(type, data):
    '''
    Returns any errors found for this plot type and data.
    In other words, if it returns False, the plot was found correctly.
    '''
    if type == 'plot':
        type = 'line'
    type_found = False
    data_found = False
    for graph in compatibility.get_plots():
        for a_plot in graph['data']:
            data_found_here = compare_data(type, data, a_plot)
            if a_plot['type'] == type and data_found_here:
                return False
            if a_plot['type'] == type:
                type_found = True
            if data_found_here:
                data_found = True
    type = GRAPH_TYPES.get(type, type)
    if type_found and data_found:
        return ("You have created a {}, but it does not have the right data. That data appears to have been plotted in another graph.".format(type))
    elif type_found:
        return ("You have created a {}, but it does not have the right data.".format(type))
    elif data_found:
        return ("You have plotted the right data, but you appear to have not plotted it as a {}.".format(type))
    else:
        return ("You have not created a {} with the proper data.".format(type))
