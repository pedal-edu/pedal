from pedal.cait.cait_api import find_matches, find_expr_sub_matches, data_state
from pedal.report.imperative import gently_r, explain_r


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
    message = "You must construct a list by appending values one at a time to the list."
    code = "app_in_iter"
    tldr = "For Loop Append Not Found"
    matches = find_matches("for ___ in ___:\n"
                           "    __expr__")
    if matches:
        for match in matches:
            __expr__ = match["__expr__"]
            submatch = __expr__.find_matches("___.append(___)")
            if submatch:
                return False
        return explain_r(message, code, label=tldr)
    return False


def wrong_not_append_to_list():
    message = ("Values can only be appended to a list. The variable <code>{0!s}</code> is either not initialized, "
               "not initialized correctly, or is confused with another variable.")
    code = "app_not_list"
    tldr = "Not Appending to List"
    matches = find_matches("for ___ in ___:\n"
                           "    __expr__")
    for match in matches:
        __expr__ = match["__expr__"]
        submatches = __expr__.find_matches("_target_.append(___)")
        for submatch in submatches:
            _target_ = submatch["_target_"]
            if not data_state(_target_).was_type('list'):
                return explain_r(message.format(_target_), code, label=tldr)
    return False


def missing_append_list_initialization():
    message = "The list variable <code>{0!s}</code> must be initialized."
    code = "no_app_list_init"
    tldr = "List Not Initialized"
    matches = find_matches("for ___ in ___:\n"
                           "    __expr__")
    for match in matches:
        __expr__ = match["__expr__"]
        submatches = __expr__.find_matches("_new_list_.append(___)", )
        for submatch in submatches:
            _new_list_ = submatch["_new_list_"].astNode
            # TODO: In theory revisit this by merging matches
            matches02 = find_matches("{} = []\n"
                                     "for ___ in ___:\n"
                                     "    __expr__".format(_new_list_.id))
            if not matches02:
                return explain_r(message.format(_new_list_.id), code, label=tldr)
    return False


def wrong_append_list_initialization():
    message = ("The list variable <code>{0!s}</code> is either not initialized "
               "correctly or mistaken for another variable. "
               "The list you append to should be initialized to an empty list.")
    code = "app_list_init"
    tldr = "Incorrect Initialization or Usage of Empty List"
    matches = find_matches("_list_ = __expr1__\n"
                           "for ___ in ___:\n"
                           "    __expr2__")
    for match in matches:
        _list_ = match["_list_"].astNode
        __expr1__ = match["__expr1__"]
        __expr2__ = match["__expr2__"]
        submatch = __expr2__.find_matches("_list_.append(___)")
        if submatch and (__expr1__.ast_name == "List" and
                         len(__expr1__.elts) != 0 or
                         __expr1__.ast_name != "List"):
            return explain_r(message.format(_list_.id), code, label=tldr)
    return False


def append_list_wrong_slot():
    message = "You should not append a list (<code>{0!s}</code>) to <code>{1!s}</code>."
    code = "app_list_slot"
    tldr = "Appending List Error"
    matches = find_matches("_target_.append(_item_)")
    if matches:
        for match in matches:
            _item_ = match["_item_"].astNode
            _target_ = match["_target_"].astNode
            if data_state(_item_).was_type('list'):
                return explain_r(message.format(_item_.id, _target_.id), code, label=tldr)
    return False


def app_assign():
    message = ("Appending modifies the list, so unlike addition,"
               " an assignment statement is not needed when using append.")
    code = "app_asgn"

    matches = find_matches("_sum_ = _sum_.append(__exp__)")
    if matches:
        return explain_r(message, code)
    return False
