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
        if data_type(_item_).is_instance(list):
            explain('The property <code>{0!s}</code> is a list and should not be placed in the iteration property slot'
                    ' of the "for" block<br><br><i>(target_is_list)<i></br>.'.format(_item_.id))
            return True
    return False


# this conflicts with list_in_wrong_slot_in_for
def wrong_list_repeated_in_for():
    match = find_match("for _item_ in _item_:\n    pass")
    if match:
        _item_ = match.symbol_table.get("_item_")[0].astNode
        if data_type(_item_).is_instance(list):
            explain('The <code>{0!s}</code> property can only appear once in the "for" block <br><br><i>'
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
        elif not data_type(_list_).is_instance(list):
            explain("The property <code>{0!s}</code> is in the list slot of the iteration but is not a list."
                    "<br><br><i>(no_iter_init)<i></br>".format(_list_.id))
            return True
    return False


# TODO: We need to cover the different cases for these
def wrong_iterator_not_list():
    match = find_match("for ___ in _item_:\n    pass")
    if match:
        _item_ = match.symbol_table.get("_item_")[0].astNode
        if not data_type(_item_).is_instance(list):
            explain("The property <code>{0!s}</code> has been set to something that is not a list but is placed in the "
                    "iteration block that must be a list.<br><br><i>(iter_not_list)<i></br>".format(_item_.id))
            return True
    return False


def missing_target_slot_empty():
    for_loops = all_for_loops()
    for loop in for_loops:
        iter_prop = loop.target
        if iter_prop.id == "___":
            explain("You must fill in the empty slot in the iteration.<br><br><i>(target_empty)<i></br>")
            return True
    return False


def list_not_initialized_on_run():
    for_loops = all_for_loops()
    for loop in for_loops:
        list_prop = loop.iter
        if list_prop.data_type is None:
            explain("The list in your for loop has not been initialized<br><br><i>(no_list_init)<i></br>")


def list_initialization_misplaced():
    for_loops = all_for_loops()
    for loop in for_loops:
        list_prop = loop.iter
        if list_prop.data_type == "List" and def_use_error(list_prop):
            explain("Initialization of <code>{0!s}</code> is a list but either in the wrong place or redefined"
                    "<br><br><i>(list_init_misplaced)<i></br>".format(list_prop.id))


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
        if data_type(_item_).is_instance(None):
            explain("The list in your for loop has not been initialized<br><br><i>(no_list_init)<i></br>")
            return True
    return False


def list_initialization_misplaced():
    match = find_match("for ___ in _item_:\n    pass")
    if match:
        _item_ = match.symbol_table.get("_item_")[0].astNode
        if data_type(_item_).is_instance(list) and def_use_error(_item_):
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
    match = find_match("for _item_ in ___:\n   _item_ = ___")
    if match:
        _item_ = match.symbol_table.get("_item_")[0].astNode
        explain("The property <code>{0!s}</code> has been reassigned. The iteration property shouldn't be reassigned"
                "<br><br><i>(target_reassign)<i></br>".format(_item_.id))
        return True
    return False
