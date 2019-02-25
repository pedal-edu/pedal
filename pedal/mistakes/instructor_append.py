from pedal.cait.cait_api import find_matches, find_expr_sub_matches, data_state
from pedal.mistakes.feedback_mod import *


def append_group_on_change():
    wrong_not_append_to_list()


def append_group():
    missing_append_in_iteration()
    missing_append_list_initialization()
    wrong_append_list_initialization()
    wrong_not_append_to_list()
    append_list_wrong_slot()
    # TODO: add app_assign on next iteration of experiment!
    # app_assign()


def find_append_in(node):
    append_list = []
    calls = node.find_all("Call")
    for node in calls:
        if node.func.attr == "append":
            append_list.append(node)
    return append_list


"""
def missing_append_in_iteration():
    std_ast = parse_program()
    for_loops = std_ast.find_all("For")
    for loop in for_loops:
        if len(find_append_in(loop)):
            return False
    explain("You must construct a list by appending values one at a time to the list.<br><br><i>(app_in_iter)<i></br>")
    return True
"""


def missing_append_in_iteration():
    matches = find_matches("for ___ in ___:\n"
                           "    __expr__")
    if matches:
        for match in matches:
            __expr__ = match["__expr__"]
            submatch = __expr__.find_matches("___.append(___)")
            if submatch:
                return False
        explain("You must construct a list by appending values one at a time to the list."
                "<br><br><i>(app_in_iter)<i></br>")
        return True
    return False


def wrong_not_append_to_list():
    matches = find_matches("for ___ in ___:\n"
                           "    __expr__")
    for match in matches:
        __expr__ = match["__expr__"]
        submatches = __expr__.find_matches("_target_.append(___)")
        for submatch in submatches:
            _target_ = submatch["_target_"]
            if not data_state(_target_).was_type('list'):
                explain("Values can only be appended to a list. The variable <code>{0!s}</code> is either "
                        "not initialized, not initialized correctly, or is confused with another variable."
                        "<br><br><i>(app_not_list)<i></br>".format(_target_))
                return True
    return False


def missing_append_list_initialization():
    matches = find_matches("for ___ in ___:\n"
                           "    __expr__")
    for match in matches:
        __expr__ = match["__expr__"]
        submatches = __expr__.find_matches("_new_list_.append(___)", )
        for submatch in submatches:
            _new_list_ = submatch["_new_list_"].astNode
            matches02 = find_matches("{} = []\n"
                                     "for ___ in ___:\n"
                                     "    __expr__".format(_new_list_.id))
            if not matches02:
                explain("The list variable <code>{0!s}</code> must be initialized.<br><br><i>"
                        "(no_app_list_init)<i></br>".format(_new_list_.id))
                return True
    return False


def wrong_append_list_initialization():
    matches = find_matches("_list_ = __expr1__\n"
                           "for ___ in ___:\n"
                           "    __expr2__")
    for match in matches:
        _list_ = match["_list_"].astNode
        __expr1__ = match["__expr1__"]
        __expr2__ = match["__expr2__"]
        submatch = find_expr_sub_matches("{}.append(___)".format(_list_.id), __expr2__)
        if submatch and (__expr1__.ast_name == "List" and
                         len(__expr1__.elts) != 0 or
                         __expr1__.ast_name != "List"):
            explain("The list variable <code>{0!s}</code> is either not "
                    "initialized correctly or mistaken for"
                    " another variable. The list you append to should be "
                    "initialized to an empty list.<br><br><i>"
                    "(app_list_init)<i></br>".format(_list_.id))
            return True
    return False


def append_list_wrong_slot():
    matches = find_matches("_target_.append(_item_)")
    if matches:
        for match in matches:
            _item_ = match["_item_"].astNode
            _target_ = match["_target_"].astNode
            if data_state(_item_).was_type('list'):
                explain("You should not append a list (<code>{0!s}</code>) to <code>{1!s}</code>.<br><br><i>"
                        "(app_list_slot)<i></br>".format(_item_.id, _target_.id))
                return True
    return False


def app_assign():
    message = ("Appending modifies the list, so unlike addition,"
               " an assignment statement is not needed when using append.")
    code = "app_asgn"

    matches = find_matches("_sum_ = _sum_.append(__exp__)")
    if matches:
        return explain_r(message, code)
    return False
