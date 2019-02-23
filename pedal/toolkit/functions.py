from pedal.cait.cait_api import parse_program
from pedal.report.imperative import gently, explain, MAIN_REPORT
from pedal.sandbox import compatibility
import ast

DELTA = 0.001


def all_documented():
    ast = parse_program()
    defs = ast.find_all('FunctionDef') + ast.find_all("ClassDef")
    for a_def in defs:
        if a_def.name == "__init__":
            continue
        if (a_def.body and
                (a_def.body[0].ast_name != "Expr" or
                 a_def.body[0].value.ast_name != "Str")):
            if a_def.ast_name == 'FunctionDef':
                gently("You have an undocumented function: " + a_def.name)
            else:
                gently("You have an undocumented class: " + a_def.name)
            return False
    return True


def get_arg_name(node):
    name = node.id
    if name is None:
        return node.arg
    else:
        return name


def match_function(name, root=None):
    if root is None:
        ast = parse_program()
    else:
        ast = root
    defs = ast.find_all('FunctionDef')
    for a_def in defs:
        if a_def._name == name:
            return a_def
    return None


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
                message = "<td><code>{}</code></td>" + ("<td><pre>{}</pre></td>" * 2)
                test_out = compatibility.capture_output(the_function, *inp)
                if isinstance(out, str):
                    if len(test_out) < 1:
                        message = message.format(inputs, repr(out), "<i>No output</i>", tip)
                        message = "<tr class=''>" + RED_X + message + "</tr>"
                        if tip:
                            message += "<tr class='info'><td colspan=4>" + tip + "</td></tr>"
                        success = False
                    elif len(test_out) > 1:
                        message = message.format(inputs, repr(out), "<i>Too many outputs</i>", tip)
                        message = "<tr class=''>" + RED_X + message + "</tr>"
                        if tip:
                            message += "<tr class='info'><td colspan=4>" + tip + "</td></tr>"
                        success = False
                    elif out not in test_out:
                        message = message.format(inputs, repr(out), repr(test_out[0]), tip)
                        message = "<tr class=''>" + RED_X + message + "</tr>"
                        if tip:
                            message += "<tr class='info'><td colspan=4>" + tip + "</td></tr>"
                        success = False
                    else:
                        message = message.format(inputs, repr(out), repr(test_out[0]), tip)
                        message = "<tr class=''>" + GREEN_CHECK + message + "</tr>"
                        success_count += 1
                elif out != test_out:
                    if len(test_out) < 1:
                        message = message.format(inputs, repr(out), "<i>No output</i>", tip)
                    else:
                        message = message.format(inputs, repr(out), repr(test_out[0]), tip)
                    message = "<tr class=''>" + RED_X + message + "</tr>"
                    if tip:
                        message += "<tr class='info'><td colspan=4>" + tip + "</td></tr>"
                    success = False
                else:
                    message = message.format(inputs, repr(out), repr(test_out[0]), tip)
                    message = "<tr class=''>" + GREEN_CHECK + message + "</tr>"
                    success_count += 1
                result += message
            if success:
                return the_function
            else:
                result = ("I ran your function <code>{}</code> on some new arguments, and it gave the wrong output "
                          "{}/{} times.".format(name, len(tests) - success_count, len(tests)) + result)
                gently(result + "</table>")
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
                message = ("<td><code>{}</code></td>" * 3)
                test_out = the_function(*inp)
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
                        message += "<tr class='info'><td colspan=4>" + tip + "</td></tr>"
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
                gently(result + "</table>")
                return None
        else:
            gently("You defined {}, but did not define it as a function.".format(name))
            return None
    else:
        gently("The function <code>{}</code> was not defined.".format(name))
        return None


class _LineVisitor(ast.NodeVisitor):
    """
    NodeVisitor subclass that visits every statement of a program and tracks
    their line numbers in a list.
    
    Attributes:
        lines (list[int]): The list of lines that were visited.
    """

    def __init__(self):
        self.lines = []

    def _track_lines(self, node):
        self.lines.append(node.lineno)
        self.generic_visit(node)

    visit_FunctionDef = _track_lines
    visit_AsyncFunctionDef = _track_lines
    visit_ClassDef = _track_lines
    visit_Return = _track_lines
    visit_Delete = _track_lines
    visit_Assign = _track_lines
    visit_AugAssign = _track_lines
    visit_AnnAssign = _track_lines
    visit_For = _track_lines
    visit_AsyncFor = _track_lines
    visit_While = _track_lines
    visit_If = _track_lines
    visit_With = _track_lines
    visit_AsyncWith = _track_lines
    visit_Raise = _track_lines
    visit_Try = _track_lines
    visit_Assert = _track_lines
    visit_Import = _track_lines
    visit_ImportFrom = _track_lines
    visit_Global = _track_lines
    visit_Nonlocal = _track_lines
    visit_Expr = _track_lines
    visit_Pass = _track_lines
    visit_Continue = _track_lines
    visit_Break = _track_lines


def check_coverage(report=None):
    """
    Checks that all the statements in the program have been executed.
    This function only works when a tracer_style has been set in the sandbox,
    or you are using an environment that automatically traces calls (e.g.,
    BlockPy).
    
    TODO: Make compatible with tracer_style='coverage'
    
    Args:
        report (Report): The Report to draw source code from; if not given,
            defaults to MAIN_REPORT.
    Returns:
        bool or set[int]: If the source file was not parsed, None is returned.
            If there were fewer lines traced in execution than are found in
            the AST, then the set of unexecuted lines are returned. Otherwise,
            False is returned.
    """
    if report is None:
        report = MAIN_REPORT
    if not report['source']['success']:
        return None, 0
    lines_executed = set(compatibility.trace_lines())
    if -1 in lines_executed:
        lines_executed.remove(-1)
    student_ast = report['source']['ast']
    visitor = _LineVisitor()
    visitor.visit(student_ast)
    lines_in_code = set(visitor.lines)
    if lines_executed < lines_in_code:
        return lines_in_code - lines_executed, len(lines_executed)/len(lines_in_code)
    else:
        return False, 1

def ensure_coverage(percentage=.5, destructive=False, report=None):
    '''
    Note that this avoids destroying the current sandbox instance stored on the
    report, if there is one present.
    
    Args:
        destructive (bool): Whether or not to remove the sandbox.
    '''
    if report is None:
        report = MAIN_REPORT
    student_code = report['source']['code']
    unexecuted_lines, percent_covered = check_coverage(report)
    if unexecuted_lines:
        if percent_covered <= percentage:
            gently("Your code coverage is not adequate. You must cover at least half your code to receive feedback.")
            return False
    return True

def ensure_cisc108_tests(test_count, report=None):
    student = compatibility.get_student_data()
    if 'assert_equal' not in student.data:
        gently("You have not imported assert_equal from the cisc108 module.")
        return False
    assert_equal = student.data['assert_equal']
    if not hasattr(assert_equal, 'student_tests'):
        gently("The assert_equal function has been modified. Do not let it be overwritten!",
               label="Assertion Function Corrupted")
        return False
    student_tests = assert_equal.student_tests
    if student_tests.tests == 0:
        gently("You are not unit testing the result.", label="No Student Unit Tests")
        return False
    elif student_tests.tests < test_count:
        gently("You have not written enough unit tests.", label="Not Enough Student Unit Tests")
        return False
    elif student_tests.failures > 0:
        gently("Your unit tests are not passing.", label="Student Unit Tests Failing")
        return False
    return True
