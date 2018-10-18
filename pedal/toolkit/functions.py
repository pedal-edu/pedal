from pedal.cait.cait_api import parse_program
from pedal.report.imperative import gently, explain
from pedal.toolkit.utilities import ensure_literal
from pedal.sandbox import compatibility

DELTA = 0.001


def get_arg_name(node):
    name = node.id
    if name is None:
        return node.arg
    else:
        return name


def match_signature(name, length, *parameters):
    ast = parse_program()
    defs = ast.find_all('FunctionDef')
    for a_def in defs:
        if a_def._name == name:
            found_length = len(a_def.args.args)
            if found_length < length:
                gently("The function named <code>{}</code> has fewer parameters ({}) than expected ({})."
                       "<br><br><i>(insuff_args)<i>".format(name, found_length, length))
            elif found_length > length:
                gently("The function named <code>{}</code> has more parameters ({}) than expected ({})."
                       "<br><br><i>(excess_args)<i>".format(name, found_length, length))
            elif parameters:
                for parameter, arg in zip(parameters, a_def.args.args):
                    arg_name = get_arg_name(arg)
                    if arg_name != parameter:
                        gently("Error in definition of <code>{}</code>. Expected a parameter named {}, instead "
                               "found {}.<br><br><i>(name_missing)<i>".format(name, parameter, arg_name))
                        return None
                else:
                    return a_def
            else:
                return a_def
    else:
        gently("No function named <code>{name}</code> was found."
               "<br><br><i>(missing_func_{name})<i>".format(name=name))
    return None


GREEN_CHECK = "<td class='green-check-mark'>&#10004;</td>"
RED_X = "<td>&#10060;</td>"


def output_test(name, *tests):
    student = compatibility.get_student_data()
    if name in student.data:
        the_function = student.data[name]
        if callable(the_function):
            result = ("<table class='blockpy-feedback-unit table table-condensed table-bordered table-hover'>"
                      "<tr class='active'><th></th><th>Arguments</th><th>Expected</th><th>Actual</th></tr>"
                      )
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
                message = "<td><code>{}</code></td>"+("<td><pre>{}</pre></td>"*2)
                test_out = compatibility.capture_output(the_function, *inp)
                if isinstance(out, str):
                    if len(test_out) < 1:
                        message = message.format(inputs, repr(out), "<i>No output</i>", tip)
                        message = "<tr class=''>"+RED_X+message+"</tr>"
                        if tip:
                            message += "<tr class='info'><td colspan=4>"+tip+"</td></tr>"
                        success = False
                    elif len(test_out) > 1:
                        message = message.format(inputs, repr(out), "<i>Too many outputs</i>", tip)
                        message = "<tr class=''>"+RED_X+message+"</tr>"
                        if tip:
                            message += "<tr class='info'><td colspan=4>"+tip+"</td></tr>"
                        success = False
                    elif out not in test_out:
                        message = message.format(inputs, repr(out), repr(test_out[0]), tip)
                        message = "<tr class=''>"+RED_X+message+"</tr>"
                        if tip:
                            message += "<tr class='info'><td colspan=4>"+tip+"</td></tr>"
                        success = False
                    else:
                        message = message.format(inputs, repr(out), repr(test_out[0]), tip)
                        message = "<tr class=''>"+GREEN_CHECK+message+"</tr>"
                        success_count += 1
                elif out != test_out:
                    if len(test_out) < 1:
                        message = message.format(inputs, repr(out), "<i>No output</i>", tip)
                    else:
                        message = message.format(inputs, repr(out), repr(test_out[0]), tip)
                    message = "<tr class=''>"+RED_X+message+"</tr>"
                    if tip:
                        message += "<tr class='info'><td colspan=4>"+tip+"</td></tr>"
                    success = False
                else:
                    message = message.format(inputs, repr(out), repr(test_out[0]), tip)
                    message = "<tr class=''>"+GREEN_CHECK+message+"</tr>"
                    success_count += 1
                result += message
            if success:
                return the_function
            else:
                result = ("I ran your function <code>{}</code> on some new arguments, and it gave the wrong output "
                          "{}/{} times.".format(name, len(tests)-success_count, len(tests))+result)
                gently(result+"</table>")
                return None
        else:
            gently("You defined {}, but did not define it as a function."
                   "<br><br><i>(not_func_def)<i>".format(name))
            return None
    else:
        gently("The function <code>{}</code> was not defined.<br><br><i>(no_func_def)<i>".format(name))
        return None


def unit_test(name, *tests):
    """
    Show a table
    :param name:
    :param tests:
    :return:
    """
    student = compatibility.get_student_data()
    if name in student.data:
        the_function = student.data[name]
        if callable(the_function):
            result = ("<table class='blockpy-feedback-unit table table-condensed table-bordered table-hover'>"
                      "<tr class='active'><th></th><th>Arguments</th><th>Returned</th><th>Expected</th></tr>"
                      )
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
                message = ("<td><code>{}</code></td>"*3)
                test_out = the_function(*inp)
                message = message.format(inputs, repr(test_out), repr(out))
                if (isinstance(out, float) and
                        isinstance(test_out, (float, int)) and
                        abs(out-test_out) < DELTA):
                    message = "<tr class=''>"+GREEN_CHECK+message+"</tr>"
                    success_count += 1
                elif out != test_out:
                    # gently(message)
                    message = "<tr class=''>"+RED_X+message+"</tr>"
                    if tip:
                        message += "<tr class='info'><td colspan=4>"+tip+"</td></tr>"
                    success = False
                else:
                    message = "<tr class=''>"+GREEN_CHECK+message+"</tr>"
                    success_count += 1
                result += message
            if success:
                return the_function
            else:
                result = "I ran your function <code>{}</code> on some new arguments, " \
                         "and it failed {}/{} tests.".format(name, len(tests)-success_count, len(tests))+result
                gently(result+"</table>")
                return None
        else:
            gently("You defined {}, but did not define it as a function.".format(name))
            return None
    else:
        gently("The function <code>{}</code> was not defined.".format(name))
        return None
