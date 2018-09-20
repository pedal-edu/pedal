from pedal.cait.cait_api import *
from pedal.report.imperative import *


def append_group_on_change():
    wrong_not_append_to_list()


def append_group():
    missing_append_in_iteration()
    missing_append_list_initialization()
    wrong_append_list_initialization()
    wrong_not_append_to_list()
    append_list_wrong_slot()


def find_append_in(node):
    append_list = []
    calls = node.find_all("Call")
    for node in calls:
        if node.func.attr == "append":
            append_list.append(node)
    return append_list

'''
def missing_append_in_iteration():
    std_ast = parse_program()
    for_loops = std_ast.find_all("For")
    for loop in for_loops:
        if len(find_append_in(loop)):
            return False
    explain("You must construct a list by appending values one at a time to the list.<br><br><i>(app_in_iter)<i></br>")
    return True
'''


def missing_append_in_iteration():
    matches = find_matches("for ___ in ___:\n"
                           "    __expr__")
    if matches:
        for match in matches:
            __expr__ = match.exp_table.get("__expr__")
            submatch = find_expr_sub_matches("___.append(___)", __expr__, cut=True)
            if submatch:
                return False
        explain("You must construct a list by appending values one at a time to the list."
                "<br><br><i>(app_in_iter)<i></br>")
        return True
    return False


def wrong_not_append_to_list():
    matches = find_matches("for ___ in ___:\n"
                           "    __expr__")
    if matches:
        for match in matches:
            __expr__ = match.exp_table.get("__expr__")
            submatches = find_expr_sub_matches("_target_.append(___)", __expr__, cut=True)
            if submatches:
                for submatch in submatches:
                    _target_ = submatch.symbol_table.get("_target_")[0].astNode
                    if not data_state(_target_).was_type('list'):
                        explain("Values can only be appended to a list. The variable <code>{0!s}</code> is either "
                                "not initialized, not initialized correctly, or is confused with another variable."
                                "<br><br><i>(app_not_list)<i></br>".format(_target_.id))
                        return True
    return False


def missing_append_list_initialization():
    matches = find_matches("for ___ in ___:\n"
                           "    __expr__")
    if matches:
        for match in matches:
            __expr__ = match.exp_table.get("__expr__")
            submatches = find_expr_sub_matches("_new_list_.append(___)", __expr__, cut=True)
            if submatches:
                for submatch in submatches:
                    _new_list_ = submatch.symbol_table.get("_new_list_")[0].astNode
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
    if matches:
        for match in matches:
            _list_ = match.symbol_table.get("_list_")[0].astNode
            __expr1__ = match.exp_table.get("__expr1__")
            __expr2__ = match.exp_table.get("__expr2__")
            submatch = find_expr_sub_matches("{}.append(___)".format(_list_.id), __expr2__, cut=True)
            if submatch and (__expr1__.ast_name == "List" and
               len(__expr1__.elts) != 0 or
               __expr1__.ast_name != "List"):
                explain("The list variable <code>{0!s}</code> is either not initialized correctly or mistaken for"
                        " another variable. The list you append to should be initialized to an empty list.<br><br><i>"
                        "(app_list_init)<i></br>".format(_list_.id))
                return True
    return False


def append_list_wrong_slot():
    matches = find_matches("_target_.append(_item_)")
    if matches:
        for match in matches:
            _item_ = match.symbol_table.get("_item_")[0].astNode
            _target_ = match.symbol_table.get("_target_")[0].astNode
            if data_state(_item_).was_type('list'):
                explain("You should not append a list (<code>{0!s}</code>) to <code>{1!s}</code>.<br><br><i>"
                        "(app_list_slot)<i></br>".format(_item_.id, _target_.id))
                return True
    return False
