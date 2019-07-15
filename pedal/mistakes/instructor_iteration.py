from pedal.cait.cait_api import (parse_program, find_match, find_matches,
                                 find_expr_sub_matches, data_state,
                                 def_use_error)
from pedal.report.imperative import gently_r, explain_r


def iteration_group():
    list_initialization_misplaced()
    wrong_target_is_list()
    wrong_list_repeated_in_for()
    missing_iterator_initialization()
    list_not_initialized_on_run()
    wrong_iterator_not_list()
    missing_target_slot_empty()
    missing_for_slot_empty()
    wrong_target_reassigned()


def iteration_group_on_change():
    wrong_target_is_list()
    wrong_list_repeated_in_for()
    wrong_iterator_not_list()


def all_for_loops():
    std_ast = parse_program()
    return std_ast.find_all("For")


# this conflics with list_repeated_in_for
def wrong_target_is_list():
    message = ('The variable <code>{0!s}</code> is a list and '
               'should not be placed in the iteration variable slot of the "for" block')
    code = "target_is_list"
    tldr = "Iteration Variable Overwriting List"
    match = find_match("for _item_ in ___:\n    pass")
    if match:
        _item_ = match["_item_"].astNode
        if data_state(_item_).was_type('list'):
            return explain_r(message.format(_item_.id), code, label=tldr)
    return False


# this conflicts with list_in_wrong_slot_in_for
def wrong_list_repeated_in_for():
    message = 'The <code>{0!s}</code> variable can only appear once in the "for" block.'
    code = "list_repeat"
    tldr = "Duplicate Iteration Variable"
    match = find_match("for _item_ in _item_:\n    pass")
    if match:
        _item_ = match["_item_"].astNode
        if data_state(_item_).was_type('list'):
            return explain_r(message.format(_item_.id), code, label=tldr)
    return False


# this isn't consistent with the pattern you wrote TODO: Fix this
def missing_iterator_initialization():
    message1 = "The slot to hold a list in the iteration is empty."
    code1 = "no_iter_init-blank"
    tldr1 = "Iteration Variable is Blank"

    message2 = "The variable <code>{0!s}</code> is in the list slot of the iteration but is not a list."
    code2 = "no_iter_init"
    tldr2 = "Iteration Variable is Not a List"

    match = find_match("for ___ in _list_:\n    pass")
    if match:
        _list_ = match["_list_"].astNode
        if _list_.id == "___":
            return explain_r(message1, code1, label=tldr1)
        elif not data_state(_list_).was_type('list'):
            return explain_r(message2.format(_list_.id), code2, label=tldr2)
    return False


# TODO: We need to cover the different cases for these
def wrong_iterator_not_list():
    message = ("The variable <code>{0!s}</code> has been set to something that is not a list but is placed "
               "in the iteration block that must be a list.")
    code = "iter_not_list"
    tldr = "Iteration List is not list"

    match = find_match("for ___ in _item_:\n    pass")
    if match:
        _item_ = match["_item_"].astNode
        if not data_state(_item_).was_type('list'):
            return explain_r(message.format(_item_.id), code, label=tldr)
    return False


def missing_target_slot_empty():
    message = "You must fill in the empty slot in the iteration."
    code = "target_empty"
    tldr = "Missing Iteration Variable"
    match = find_match("for _item_ in ___:\n    pass")
    if match:
        _item_ = match["_item_"].astNode
        if _item_.id == "___":
            return explain_r(message, code, label=tldr)
    return False


def list_not_initialized_on_run():
    message = "The list in your for loop has not been initialized."
    code = "no_list_init"
    tldr = "List Variable Uninitialized"
    match = find_match("for ___ in _item_:\n    pass")
    if match:
        _item_ = match["_item_"][0].astNode
        if def_use_error(_item_):
            return explain_r(message, code, label=tldr)
    return False


def list_initialization_misplaced():
    message = "Initialization of <code>{0!s}</code> is a list but either in the wrong place or redefined"
    code = "list_init_misplaced"
    tldr = "Iterating over Non-list"
    match = find_match("for ___ in _item_:\n    pass")
    if match:
        _item_ = match["_item_"][0].astNode
        if data_state(_item_).was_type('list') and def_use_error(_item_):
            return explain_r(message.format(_item_.id), code, label=tldr)
    return False


def missing_for_slot_empty():
    message = "You must fill in the empty slot in the iteration."
    code = "for_incomplete"
    tldr = "Iteration Incomplete"
    match = find_match("for _item_ in _list_:\n    pass")
    if match:
        _item_ = match["_item_"][0].astNode
        _list_ = match["_list_"][0].astNode
        if _item_.id == "___" or _list_.id == "___":
            return explain_r(message, code, label=tldr)
    return False


def wrong_target_reassigned():
    message = "The variable <code>{0!s}</code> has been reassigned. The iteration variable shouldn't be reassigned"
    code = "target_reassign"
    tldr = "Iteration Variable has been Reassigned"
    matches = find_matches("for _item_ in ___:\n"
                           "   __expr__")
    for match in matches:
        __expr__ = match["__expr__"]
        _item_ = match["_item_"][0]
        submatches = __expr__.find_matches("_item_ = ___")
        if submatches:
            return explain_r(message.format(_item_), code, label=tldr)
    return False
