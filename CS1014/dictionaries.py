from pedal.report.imperative import explain, gently
from pedal.cait.cait_api import *
from pedal.toolkit.utilities import *
from pedal.sandbox.compatibility import get_output


def gently_r(message, code, line=None, tldr=""):
    if tldr != "":
        tldr = "<p><b>{}</b></p>".format(tldr)
    gently(tldr + message + "<br><br><i>({})<i></br></br>".format(code), line)
    return message


def explain_r(message, code, priority='medium', line=None, tldr=""):
    if tldr != "":
        tldr = "<p><b>{}</b></p>".format(tldr)
    explain(tldr + message + "<br><br><i>({})<i></br></br>".format(code), priority, line)
    return message


def hard_coding(val_list):
    message = ("Please show code that makes the computer extract "
               "the value from the dictionary.")
    code = "hard_code"

    # Pattern 1 possibility
    matches = find_matches("print(__exp__)")
    for match in matches:
        __exp__ = match["__exp__"]
        value = __exp__.value
        if value in val_list:
            return explain_r(message, code)

    # Pattern 2 possibility
    matches = find_matches("__exp__\n"
                           "print(_var_)")
    for match in matches:
        __exp__ = match["__exp__"]
        _var_ = match["_var_"]
        submatches = __exp__.find_matches("{} = __exp2__".format(_var_.id))
        for submatch in submatches:
            __exp2__ = submatch["__exp2__"]
            value = __exp2__.value
            if value in val_list:
                return explain_r(message, code)
    return False


def print_dict_key(keys):
    message = "You've printed the dictionary key <code>{}</code> instead of using an extracted value and printing it"
    code = "dict_k_print"

    matches = find_matches("print(__str__)")
    matches += find_matches("print([__str__])")

    for match in matches:
        __str__ = match["__str__"]
        if __str__.is_ast("Str") and __str__.value in keys:
            return gently_r(message.format(__str__.value), code)
    return False


def var_instead_of_key(keys):
    message = ("It looks like you are trying to use <code>{}</code>) as a dictionary key. "
               "Use the dictionary access syntax to get values from a dictionary")
    code = "var_as_k"

    matches = find_matches("_var_")
    matches += find_matches("[_var_]")
    for match in matches:
        _var_ = match["_var_"]
        if _var_.id in keys:
            submatch = find_match("_dict_['{}']".format(_var_.id))
            if submatch is None:
                return explain_r(message.format(_var_.id), code)
    return False


def parens_in_dict(keys):
    message = ("It seems like you ar having trouble with dictionary syntax. The dictionary key <code>{}"
               "</code>should use brackets.")
    code = "par_dict"

    matches = find_matches("_var_(__str__)")
    for match in matches:
        __str__ = match['__str__']
        if __str__.is_ast("Str") and __str__.value in keys:
            return explain_r(message.format(__str__.value), code)
    return False


def list_as_dict():
    message = ("A list of Dictionaries like <code>{}</code> is not itself a dictionary. "
               "To access key-value pairs of the dictionaries in the list, "
               "you need to access each dictionary in the list one at a time.")
    code = "list_dict"

    matches = find_matches("_list_[__exp__]")
    for match in matches:
        _list_ = match['_list_']
        if _list_.was_type("ListType") and str(_list_.value.type.subtype) == "DictType":
            return explain_r(message.format(_list_.id), code)
    return False


def dict_out_of_loop(keys):
    message = ("Remember that a list of dictionaries, like <code>{}</code>, "
               "is still a list of individual items. Each dictionary needs to be accessed with "
               "the appropriate key-value pair one at a time.")
    code = "dict_out_loop"

    matches = find_matches("__exp__\n"
                           "for ___ in _var_:\n"
                           "    pass")
    matches += find_matches("for ___ in _var_:\n"
                            "    pass\n"
                            "__exp__\n")
    for match in matches:
        __exp__ = match['__exp__']
        _var_ = match['_var_']
        submatches = __exp__.find_matches("{var}[__str__]".format(var=_var_.id))
        for submatch in submatches:
            __str__ = submatch['__str__']
            if __str__.is_ast("Str") and __str__.value in keys:
                return explain_r(message.format(_var_.id), code)
    return False


def wrong_keys(unused_keys):
    message = "This problem does not require the key <code>{}</code>.\n"
    code = "unused_key"

    matches = find_matches("_var_[__str__]")
    for match in matches:
        __str__ = match["__str__"]
        if __str__.is_ast("Str") and __str__.value in unused_keys:
            return explain_r(message.format(__str__.value), code)
    return False


def dict_access_not_in_loop():
    message = ("You haven't used the dictionary access syntax in a for loop. "
               "Remember that a list of dictionaries is still a list of individual items. "
               "Each dictionary needs to be accessed with the appropriate key-value pair one at a time.")
    code = "dict_acc_loop"

    matches = find_matches("for ___ in ___:\n"
                           "    __exp__")
    for match in matches:
        submatches = match["__exp__"].find_matches("_var_[__str__]")
        if not submatches:
            return explain_r(message, code)
    return False


def hard_coded_list(val_list):
    message = ("In later abstractions, it's not possible to view the values of a specific key in a list."
               "You should use a dictionary key-value pair to access values in the list of dictionaries.")
    code = "hard_list"

    matches = find_matches("[__exp__]")
    for match in matches:
        __exp__ = match['__exp__'].parent
        if __exp__.ast_name == "List":
            try:
                vals = sum([x.value for x in __exp__.elts])
                if sum(val_list) == vals:
                    return explain_r(message, code)
            except TypeError:
                pass  # This should be the only error
    return False


def iter_as_key(keys):
    message = ("It looks like you are using the iteration variable <code>{}"
               "</code> to access a value of a specific key in a dictionary. "
               "To access a key-value from a list of dictionaries, use <code>")
    code = "iter_key"

    matches = find_matches("for _var_ in ___:\n"
                           "    pass")
    for match in matches:
        _var_ = match['_var_']
        submatches = find_matches("_var2_[__str__]")
        missing = True
        for submatch in submatches:
            __str__ = submatch["__str__"]
            if __str__.is_ast("Str") and __str__.value == _var_.id:
                missing = False
                break
        if missing and _var_.id in keys:
            return explain_r(message.format(_var_.id), code)
    return False


def dict_acc_as_lis_var(keys):
    message = ("The list variable in an iteration can only take lists. "
               "To grab individual values in a list of dictionaries, "
               "you need to use the appropriate key for each dictionary.")
    code = "list_var_dict"

    matches = find_matches("for ___ in [__str__]:\n"
                           "    pass")
    for match in matches:
        __str__ = match["__str__"]
        if __str__.is_ast("Str") and __str__.value in keys:
            return explain_r(message, code)
    return False


def append_and_sum():
    message = ("It looks like you're trying to build a list and "
               "then calculate a value. While this will get you a "
               "correct answer, you can calculate the value directly instead of first building a list.")
    code = "app_sum"

    matches = find_match("for ___ in ___:\n"
                         "    _var_.append()\n"
                         "for ___ in _var_:\n"
                         "    ___ = ___ + ___")
    if matches:
        return explain_r(message, code)
    return False


def iter_prop_dict_acc():
    message = ("Improper usage of iteration variable."
               "The for statement gives the iteration variable a value, "
               "in this case, a dictionary. That dictionary can only be accessed in the body of the iteration.")
    code = "iter_dict_acc"

    match = find_match("for _var_[__str__] in ___:\n"
                       "    pass")
    if match:
        return explain_r(message, code)
    return False


def list_str_dict(keys):
    message = ("When using dictionaries with iteration, the list cannot just be a key "
               "value like <code>{}</code>, it must be the list of dictionaries.")
    code = "list_str"

    matches = find_matches("for ___ in __str__:\n"
                           "    pass")
    for match in matches:
        __str__ = match['__str__']
        if __str__.is_ast("Str") and __str__.value in keys:
            return explain_r(message.format(__str__.value), code)
    return False


def missing_key(keys):
    message = "You seem to be missing the following dictionary keys:<ul>{}</ul>"
    code = "miss_key"

    str_list = ""
    for key in keys:
        matches = find_matches("'{}'".format(key))
        if not matches:
            str_list += '<li><code>"' + key + '"</code></li>'

    if str_list != "":
        return explain_r(message.format(str_list), code)
    return False
