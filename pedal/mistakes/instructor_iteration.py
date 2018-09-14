from pedal.cait.cait_api import *
from pedal.report.imperative import *


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
    match = find_match("for _item_ in ___:\n    pass")
    if match:
        _item_ = match.symbol_table.get("_item_")[0].astNode
        if data_state(_item_).was_type('list'):
            explain('The variable <code>{0!s}</code> is a list and should not be placed in the iteration variable slot'
                    ' of the "for" block<br><br><i>(target_is_list)<i></br>.'.format(_item_.id))
            return True
    return False


# this conflicts with list_in_wrong_slot_in_for
def wrong_list_repeated_in_for():
    match = find_match("for _item_ in _item_:\n    pass")
    if match:
        _item_ = match.symbol_table.get("_item_")[0].astNode
        if data_state(_item_).was_type('list'):
            explain('The <code>{0!s}</code> variable can only appear once in the "for" block <br><br><i>'
                    '(list_repeat)<i></br>'.format(_item_.id))
            return True
    return False


# this isn't consistent with the pattern you wrote
def missing_iterator_initialization():
    match = find_match("for ___ in _list_:\n    pass")
    if match:
        _list_ = match.symbol_table.get("_list_")[0].astNode
        if _list_.id == "___":
            explain("The slot to hold a list in the iteration is empty.<br><br><i>(no_iter_init-blank)<i></br>")
            return True
        elif not data_state(_list_).was_type('list'):
            explain("The variable <code>{0!s}</code> is in the list slot of the iteration but is not a list."
                    "<br><br><i>(no_iter_init)<i></br>".format(_list_.id))
            return True
    return False


# TODO: We need to cover the different cases for these
def wrong_iterator_not_list():
    match = find_match("for ___ in _item_:\n    pass")
    if match:
        _item_ = match.symbol_table.get("_item_")[0].astNode
        if not data_state(_item_).was_type('list'):
            explain("The variable <code>{0!s}</code> has been set to something that is not a list but is placed in the "
                    "iteration block that must be a list.<br><br><i>(iter_not_list)<i></br>".format(_item_.id))
            return True
    return False


def missing_target_slot_empty():
    match = find_match("for _item_ in ___:\n    pass")
    if match:
        _item_ = match.symbol_table.get("_item_")[0].astNode
        if _item_.id == "___":
            explain("You must fill in the empty slot in the iteration.<br><br><i>(target_empty)<i></br>")
            return True
    return False


def list_not_initialized_on_run():
    match = find_match("for ___ in _item_:\n    pass")
    if match:
        _item_ = match.symbol_table.get("_item_")[0].astNode
        if def_use_error(_item_):
            explain("The list in your for loop has not been initialized<br><br><i>(no_list_init)<i></br>")
            return True
    return False


def list_initialization_misplaced():
    match = find_match("for ___ in _item_:\n    pass")
    if match:
        _item_ = match.symbol_table.get("_item_")[0].astNode
        if data_state(_item_).was_type('list') and def_use_error(_item_):
            explain("Initialization of <code>{0!s}</code> is a list but either in the wrong place or redefined"
                    "<br><br><i>(list_init_misplaced)<i></br>".format(_item_.id))
            return True
    return False


def missing_for_slot_empty():
    match = find_match("for _item_ in _list_:\n    pass")
    if match:
        _item_ = match.symbol_table.get("_item_")[0].astNode
        _list_ = match.symbol_table.get("_list_")[0].astNode
        if _item_.id == "___" or _list_.id == "___":
            explain("You must fill in the empty slot in the iteration.<br><br><i>(for_incomplete)<i></br>")
            return True
    return False


def wrong_target_reassigned():
    matches = find_matches("for _item_ in ___:\n"
                           "   __expr__")
    if matches:
        for match in matches:
            __expr__ = match.exp_table.get("__expr__")
            _item_ = match.symbol_table.get("_item_")[0]
            submatches = find_expr_sub_matches("{} = ___".format(_item_.id), __expr__, as_expr=False)
            if submatches:
                for submatch in submatches:
                    explain("The variable <code>{0!s}</code> has been reassigned. "
                            "The iteration variable shouldn't be reassigned"
                            "<br><br><i>(target_reassign)<i></br>".format(_item_.id))
                    return True
    return False
