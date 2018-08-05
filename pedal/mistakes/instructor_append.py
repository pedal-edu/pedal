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
                           "    ___.append(___)")
    if not matches:
        explain("You must construct a list by appending values one at a time to the list."
                "<br><br><i>(app_in_iter)<i></br>")
        return True
    return False


def wrong_not_append_to_list():
    matches = find_matches("for ___ in ___:\n"
                           "    _target_.append(___)")
    if matches:
        for match in matches:
            _target_ = match.symbol_table.get("_target_")[0].astNode
            if not data_type(_target_).is_instance(list):
                explain("Values can only be appended to a list. The property <code>{0!s}</code> is either not "
                        "initialized, not initialized correctly, or is confused with another property.<br><br><i>"
                        "(app_not_list)<i></br>".format(_target_.id))
                return True
    return False


def missing_append_list_initialization():
    std_ast = parse_program()
    for_loops = std_ast.find_all("For")
    loop_appends = []
    for loop in for_loops:
        loop_appends.extend(find_append_in(loop))
    assignments = std_ast.find_all("Assign")
    for append_call in loop_appends:
        append_loc = append_call.lineno
        append_var = append_call.func.value
        found_init = False
        for assignment in assignments:
            if assignment.has(append_var) and assignment.lineno < append_loc:
                found_init = True
                break
        if not found_init and append_var.id != "___":
            explain("The list property <code>{0!s}</code> must be initialized.<br><br><i>"
                    "(no_app_list_init)<i></br>".format(append_var.id))
            return True
    return False


def wrong_append_list_initialization():
    matches = find_matches("_list_ = __expr__\n"
                           "for ___ in ___:\n"
                           "    _list_.append(___)")
    if matches:
        for match in matches:
            _list_ = match.symbol_table.get("_list_")[0].astNode
            __expr__ = match.exp_table.get("__expr__")
            if (__expr__.ast_name == "List" and len(__expr__.elts) != 0 or
               __expr__.ast_name != "List"):
                explain("The list property <code>{0!s}</code> is either not initialized correctly or mistaken for"
                        " another property. The list you append to should be initialized to an empty list.<br><br><i>"
                        "(app_list_init)<i></br>".format(_list_.id))
                return True
    return False


def append_list_wrong_slot():
    matches = find_matches("_target_.append(_item_)")
    if matches:
        for match in matches:
            _item_ = match.symbol_table.get("_item_")[0].astNode
            _target_ = match.symbol_table.get("_target_")[0].astNode
            if data_type(_item_).is_instance(list):
                explain("You should not append a list (<code>{0!s}</code>) to <code>{1!s}</code>.<br><br><i>"
                        "(app_list_slot)<i></br>".format(_item_.id, _target_.id))
                return True
    return False

