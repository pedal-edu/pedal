from pedal.cait.cait_api import parse_program
from pedal.core.commands import gently
from pedal.core.report import MAIN_REPORT
from pedal.sandbox import commands
import ast

from pedal.utilities.ast_tools import FindExecutableLines

DELTA = 0.001


def match_function(name, root=None):
    """

    Args:
        name:
        root:

    Returns:

    """
    if root is None:
        ast = parse_program()
    else:
        ast = root
    defs = ast.find_all('FunctionDef')
    for a_def in defs:
        if a_def._name == name:
            return a_def
    return None


def match_signature_muted(name, length, *parameters):
    """

    Args:
        name:
        length:
        *parameters:

    Returns:

    """
    ast = parse_program()
    defs = ast.find_all('FunctionDef')
    for a_def in defs:
        if a_def._name == name:
            found_length = len(a_def.args.args)
            if found_length != length:
                return None
            elif parameters:
                for parameter, arg in zip(parameters, a_def.args.args):
                    arg_name = get_arg_name(arg)
                    if arg_name != parameter:
                        return None
                else:
                    return a_def
            else:
                return a_def
    return None


def match_signature(name, length, *parameters):
    """

    Args:
        name:
        length:
        *parameters:

    Returns:

    """
    ast = parse_program()
    defs = ast.find_all('FunctionDef')
    for a_def in defs:
        if a_def._name == name:
            found_length = len(a_def.args.args)
            if found_length < length:
                gently("The function named <code>{}</code> has fewer parameters ({}) "
                         "than expected ({}). ".format(name, found_length, length), label="insuff_args")
            elif found_length > length:
                gently("The function named <code>{}</code> has more parameters ({}) "
                         "than expected ({}). ".format(name, found_length, length), label="excess_args")
            elif parameters:
                for parameter, arg in zip(parameters, a_def.args.args):
                    arg_name = get_arg_name(arg)
                    if arg_name != parameter:
                        gently("Error in definition of <code>{}</code>. Expected a parameter named {}, "
                                 "instead found {}.".format(name, parameter, arg_name), label="name_missing")
                        return None
                else:
                    return a_def
            else:
                return a_def
    else:
        gently("No function named <code>{name}</code> was found.".format(name=name),
                 label="missing_func", title="Missing Function", fields={'name': name})
    return None


TEST_TABLE_HEADER = "<table class='blockpy-feedback-unit table table-sm table-bordered table-hover'>"
TEST_TABLE_OUTPUT = TEST_TABLE_HEADER+(
    "<tr class='table-active'><th></th><th>Arguments</th><th>Expected</th><th>Actual</th></tr>"
)
TEST_TABLE_UNITS = TEST_TABLE_HEADER+(
    "<tr class='table-active'><th></th><th>Arguments</th><th>Returned</th><th>Expected</th></tr>"
)
GREEN_CHECK = "<td class='green-check-mark'>&#10004;</td>"
RED_X = "<td>&#10060;</td>"


def output_test(name, *tests):
    """

    Args:
        name:
        *tests:

    Returns:

    """
    student_data = commands.get_student_data()
    if name in student_data:
        the_function = student_data[name]
        if callable(the_function):
            result = TEST_TABLE_OUTPUT
            success = True
            success_count = 0
            for test in tests:
                inp = test[:-1]
                inputs = ', '.join(["<code>{}</code>".format(repr(i)) for i in inp])
                out = test[-1]
                tip = ""
                if isinstance(out, tuple):
                    tip = out[1]
                    out = out[0]
                message = "<td><code>{}</code></td>" + ("<td><pre>{}</pre></td>" * 2)
                test_out = commands.call(the_function, *inp)
                if isinstance(out, str):
                    if len(test_out) < 1:
                        message = message.format(inputs, repr(out), "<i>No output</i>", tip)
                        message = "<tr class=''>" + RED_X + message + "</tr>"
                        if tip:
                            message += "<tr class='table-info'><td colspan=4>" + tip + "</td></tr>"
                        success = False
                    elif len(test_out) > 1:
                        message = message.format(inputs, "\n".join(out), "<i>Too many outputs</i>", tip)
                        message = "<tr class=''>" + RED_X + message + "</tr>"
                        if tip:
                            message += "<tr class='info'><td colspan=4>" + tip + "</td></tr>"
                        success = False
                    elif out not in test_out:
                        message = message.format(inputs, "\n".join(out), "\n".join(test_out), tip)
                        message = "<tr class=''>" + RED_X + message + "</tr>"
                        if tip:
                            message += "<tr class='table-info'><td colspan=4>" + tip + "</td></tr>"
                        success = False
                    else:
                        message = message.format(inputs, "\n".join(out), "\n".join(test_out), tip)
                        message = "<tr class=''>" + GREEN_CHECK + message + "</tr>"
                        success_count += 1
                elif out != test_out:
                    if len(test_out) < 1:
                        message = message.format(inputs, "\n".join(out), "<i>No output</i>", tip)
                    else:
                        message = message.format(inputs, "\n".join(out), "\n".join(test_out), tip)
                    message = "<tr class=''>" + RED_X + message + "</tr>"
                    if tip:
                        message += "<tr class='table-info'><td colspan=4>" + tip + "</td></tr>"
                    success = False
                else:
                    message = message.format(inputs, "\n".join(out), "\n".join(test_out), tip)
                    message = "<tr class=''>" + GREEN_CHECK + message + "</tr>"
                    success_count += 1
                result += message
            if success:
                return the_function
            else:
                result = ("I ran your function <code>{}</code> on some new arguments, and it gave the wrong output "
                          "{}/{} times.".format(name, len(tests) - success_count, len(tests)) + result)
                gently(result + "</table>", label="wrong_output")
                return None
        else:
            gently("You defined {}, but did not define it as a function.".format(name), label="not_func_def")
            return None
    else:
        gently("The function <code>{}</code> was not defined.".format(name), label="no_func_def")
        return None


def unit_test(name, *tests):
    """
    Show a table
    :param name:
    :param tests:
    :return:
    """
    student_data = commands.get_student_data()
    if name in student_data:
        the_function = student_data[name]
        if callable(the_function):
            result = TEST_TABLE_UNITS
            success = True
            success_count = 0
            for test in tests:
                inp = test[:-1]
                inputs = ', '.join(["<code>{}</code>".format(repr(i)) for i in inp])
                out = test[-1]
                tip = ""
                if isinstance(out, tuple):
                    tip = out[1]
                    out = out[0]
                message = ("<td><code>{}</code></td>" * 3)
                ran = True
                try:
                    test_out = the_function(*inp)
                except Exception as e:
                    message = message.format(inputs, str(e), repr(out))
                    message = "<tr class=''>" + RED_X + message + "</tr>"
                    success = False
                    ran = False
                if not ran:
                    result += message
                    continue
                message = message.format(inputs, repr(test_out), repr(out))
                if (isinstance(out, float) and
                        isinstance(test_out, (float, int)) and
                        abs(out - test_out) < DELTA):
                    message = "<tr class=''>" + GREEN_CHECK + message + "</tr>"
                    success_count += 1
                elif out != test_out:
                    # gently(message)
                    message = "<tr class=''>" + RED_X + message + "</tr>"
                    if tip:
                        message += "<tr class='table-info'><td colspan=4>" + tip + "</td></tr>"
                    success = False
                else:
                    message = "<tr class=''>" + GREEN_CHECK + message + "</tr>"
                    success_count += 1
                result += message
            if success:
                return the_function
            else:
                result = "I ran your function <code>{}</code> on some new arguments, " \
                         "and it failed {}/{} tests.".format(name, len(tests) - success_count, len(tests)) + result
                gently(result + "</table>", label="tests_failed")
                return None
        else:
            gently("You defined {}, but did not define it as a function.".format(name))
            return None
    else:
        gently("The function <code>{}</code> was not defined.".format(name))
        return None


