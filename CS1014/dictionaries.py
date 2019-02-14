from pedal.report.imperative import explain, gently
from pedal.cait.cait_api import *
from pedal.toolkit.utilities import *
from pedal.sandbox.compatibility import get_output


def gently_r(message,line=None):
    gently(message, line)
    return message


def explain_r(message, priority='medium', line=None):
    explain(message, priority, line)
    return message


def print_str_key(keys=False):
    matches = find_matches("print(__str__)")
    matches += find_matches("print([__str__])")
    for match in matches:
        if match["__str__"].ast_name == "Str":
            student_str = match["__str__"].s
            if keys and student_str in keys:
                    return gently_r("Printing key {} instead of key-value"
                                    "<br><br><i>(print_dict_str)<i></br>".format(student_str))
            else:
                return gently_r("Printing String instead of value<br><br><i>(print_str)<i></br>")
    return False


def print_var_key(keys):
    matches = find_matches("print(_var_)")
    matches += find_matches("print([_var_])")
    unused_list = []
    for key in keys:
        if find_match("_var_[{}]".format(key)) is None:
            unused_list.append(key)

    for match in matches:
        var_name = match["_var_"].id
        if var_name in unused_list:
            explain_r("using variable {} as key name<br><br><i>(var_as_key)<i></br>".format(var_name))
