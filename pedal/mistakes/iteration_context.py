from pedal.cait.cait_api import (parse_program,
                                 find_matches, find_match,
                                 find_expr_sub_matches)
from pedal.report.imperative import explain, gently
import pedal.mistakes.instructor_append as append_api
from pedal.toolkit.utilities import *
from pedal.sandbox.compatibility import get_output, get_plots
from pedal.report.imperative import gently_r, explain_r


# ################8.2 Start#######################
def wrong_list_length_8_2():
    message = "You must have at least three pieces"
    code = "list length_8.2"
    tldr = "List too short"
    matches = find_matches("_list_ = __expr__")
    if matches:
        for match in matches:
            __expr__ = match["__expr__"]
            if __expr__.ast_name == "List" and len(__expr__.elts) < 3:
                return explain_r(message, code, label=tldr)
    return False


def missing_list_initialization_8_2():
    message = ('You must set the variable <code>shopping_cart</code>'
               'to a list containing the prices of items in the shopping cart.')
    code = "missing_list_init_8.2"
    tldr = "Missing list initialization"
    matches = find_matches("shopping_cart = __expr__")
    for match in matches:
        __expr__ = match["__expr__"]
        if __expr__.ast_name == "List":
            return False
    return explain_r(message, code, label=tldr)


def wrong_list_is_constant_8_2():
    message = 'You must set <code>shoppping_cart</code> to a list of values not to a single number.'
    code = "list_is_const_8.2"
    tldr = "Shopping Cart not set to list"
    matches = find_matches("shopping_cart = __expr__")
    for match in matches:
        __expr__ = match["__expr__"]
        if __expr__.ast_name == "Num":
            return explain_r(message, code, label=tldr)
    return False


def list_all_zeros_8_2():
    message = 'Try seeing what happens when you change the numbers in the list.'
    code = 'default_list_8.2'
    tldr = 'Use different numbers'
    matches = find_matches("_var_ = [__list__]")
    for match in matches:
        __list__ = match['__list__']
        list_node = __list__.parent
        all_num = list_node.find_all("Num")
        all_zeros = True
        for num in all_num:
            if num.n != 0:
                all_zeros = False
                break
        if all_zeros:
            return explain_r(message, code, label=tldr)
    return False

# ################8.2 End#######################


# ################8.3 Start#######################
def wrong_list_initialization_placement_8_3():
    message = ('The list of episode lengths (<code>episode_length_list</code>)'
               ' must be initialized before the iteration which uses this list.')
    code = "init_place_8.3"
    tldr = "Wrong Initialization Placement"
    for_matches = find_matches("for ___ in ___:\n"
                               "    pass")
    init_matches = find_matches("episode_length_list = ___")
    if init_matches and for_matches:
        for for_match in for_matches:
            for_lineno = for_match.match_lineno
            for init_match in init_matches:
                if init_match.match_lineno > for_lineno:
                    return explain_r(message, code, label=tldr)
    return False


def wrong_accumulator_initialization_placement_8_3():
    message = ('The variable to hold the sum of the episode lengths (<code>sum_length</code>) '
               'must be initialized before the iteration which uses this variable.')
    code = "accu_init_place_8.3"
    tldr = "Accumulator initialization misplaced"
    for_matches = find_matches("for ___ in ___:"
                               "    pass")
    init_matches = find_matches("sum_length = 0")
    if init_matches and for_matches:
        for for_match in for_matches:
            for_lineno = for_match.match_lineno
            for init_match in init_matches:
                if init_match.match_lineno > for_lineno:
                    return explain_r(message, code, label=tldr)
    return False


def wrong_iteration_body_8_3():
    message = "The addition of each episode length to the total length is not in the correct place."
    code = "iter_body_8.3"
    tldr = "Accumulation Misplaced"
    match = find_match("for _item_ in _list_:\n"
                       "    sum_length = ___ + ___\n")
    if not match:
        return explain_r(message, code, label=tldr)
    return False


def wrong_print_8_3():
    message = ('The output of the total length of time is not in the correct place. The total length of time should be'
               ' output only once after the total length of time has been computed.')
    code = "print_8.3"
    tldr = "Print statement misplaced"
    match = find_match("for _item_ in _list_:\n"
                       "    pass\n"
                       "print(_total_)")
    if not match:
        return explain_r(message, code, label=tldr)
    return False


# ################8.3 End#######################


# ################8.4 Start#######################
def missing_target_slot_empty_8_4():
    message = 'You must fill in the empty slot in the iteration.'
    code = 'target_empty_8.4'
    tldr = "Iteration Variable Empty"
    matches = find_matches("for _item_ in pages_count_list:\n"
                           "    pass")
    if matches:
        for match in matches:
            _item_ = match["_item_"][0]
            if _item_.id == "___":
                return explain_r(message, code, tldr)
    return False


def missing_addition_slot_empty_8_4():
    message = "You must fill in the empty slot in the addition."
    code = "add_empty_8.4"
    tldr = "Addition Blank"
    matches = find_matches("sum_pages + _item_")
    if matches:
        for match in matches:
            _item_ = match["_item_"][0]
            if _item_.id == "___":
                return explain_r(message, code, label=tldr)
    return False


def wrong_names_not_agree_8_4():
    message = "Each value of <code>{0!s}</code> must be added to <code>{1!s}</code>."
    code = "name_agree_8.4"
    tldr = "Iteration Variable and Accumulation Mismatch"
    matches = find_matches("for _item1_ in pages_count_list:\n"
                           "    sum_pages = sum_pages + _item2_")
    if matches:
        for match in matches:
            # in theory, these will always be different? should test in test_cait
            _item1_ = match["_item1_"][0]
            _item2_ = match["_item2_"][0]
            if _item1_.id != _item2_.id:
                return explain_r(message.format(_item1_.id, _item2_.id), code, label=tldr)
    return False


# ################8.4 End#######################
def wrong_modifying_list_8_5():
    """

    # old code for record keeping because significantly different semantics
    std_ast = parse_program()
    list_init = std_ast.find_all('List')
    true_sum = 0
    if len(list_init) != 0:
        for value in list_init[0].elts:
            true_sum = value.n + true_sum
    if true_sum != sum([20473, 27630, 17849, 19032, 16378]) or len(list_init) == 0:
        explain('Don\'t modify the list<br><br><i>(mod_list_8.5)<i></br>')
        return True
    return  False

    Returns:
    """
    message = "Don't modify the list"
    code = "mod_list_8.5"
    match = find_match("[20473, 27630, 17849, 19032, 16378]")
    if not match:
        return explain_r(message, code)
    return False


def wrong_modifying_list_8_6():
    """
    std_ast = parse_program()
    list_init = std_ast.find_all('List')
    true_sum = 0
    for value in list_init[0].elts:
        true_sum = value.n + true_sum
    if true_sum != sum([2.9, 1.5, 2.3, 6.1]):
        explain('Don\'t modify the list<br><br><i>(mod_list_8.6)<i></br>')
    Returns:
    """
    message = "Don't modify the list"
    code = "mod_list_8.6"
    match = find_match("_list_ = [2.9, 1.5, 2.3, 6.1]")
    if not match:
        return explain_r(message, code)
    return False


def wrong_should_be_counting():
    """
    std_ast = parse_program()
    for_loops = std_ast.find_all('For')
    for loop in for_loops:
        iter_prop = loop.target
        assignments = loop.find_all('Assign')
        for assignment in assignments:
            binops = assignment.find_all('BinOp')
            for binop in binops:
                if binop.has(iter_prop) and binop.op == 'Add':
                    explain('This problem asks for the number of items in the list not the total of all the values in '
                            'the list.<br><br><i>(not_count)<i></br>')
    Returns:
    """
    message = "This problem asks for the number of items in the list not the total of all the values in the list."
    code = "not_count"
    tldr = "Summing instead of counting"
    matches = find_matches("for _item_ in ___:\n"
                           "    __expr__")
    if matches:
        for match in matches:
            _item_ = match["_item_"][0]
            __expr__ = match["__expr__"]
            submatches = __expr__.find_matches("___ = ___ + _item_")
            if submatches:
                return explain_r(message, code, label=tldr)
    return False


def wrong_should_be_summing():
    """
    std_ast = parse_program()
    for_loops = std_ast.find_all('For')
    for loop in for_loops:
        assignments = loop.find_all('Assign')
        for assignment in assignments:
            binops = assignment.find_all('BinOp')
            for binop in binops:
                if binop.has(1) and binop.op == 'Add':
                    explain('This problem asks for the total of all the values in the list not the number of items in '
                            'the list.<br><br><i>(not_sum)<i></br>')
    """
    message = "This problem asks for the total of all the values in the list not the number of items in the list."
    code = "not_sum"
    tldr = "Counting instead of summing"
    matches = find_matches("for _item_ in ___:\n"
                           "    __expr__")
    if matches:
        for match in matches:
            __expr__ = match["__expr__"]
            submatches = __expr__.find_matches("___ = 1 + ___", )
            if submatches:
                return explain_r(message, code, label=tldr)
    return False


def missing_addition_slot_empty():
    """
    std_ast = parse_program()
    assignments = std_ast.find_all('Assign')
    for assignment in assignments:
        # left = assignment.target
        right = assignment.value
        binOp = right.find_all('BinOp')
        if len(binOp) == 1:
            binOp = binOp[0]
            if binOp.op == 'Add':
                if binOp.left.ast_name == 'Name' and binOp.right.ast_name == 'Name':
                    if binOp.left.id == '___' or binOp.right.id == '___':
                        explain('You must fill in the empty slot in the addition.<br><br><i>(add_empty)<i></br>')
                        return True
    return False
    Returns:
    """
    message = "You must fill in the empty slot in the addition."
    code = "add_empty"
    tldr = "Addition Blank"
    matches = find_matches("___ + _item_")
    if matches:
        for match in matches:
            _item_ = match["_item_"][0]
            if _item_.id == "___":
                return explain_r(message, code, tldr)
    return False


def wrong_cannot_sum_list():
    """

    std_ast = parse_program()
    for_loops = std_ast.find_all('For')
    for loop in for_loops:
        list_prop = loop.iter
        assignments = loop.find_all('Assign')
        for assignment in assignments:
            binops = assignment.find_all('BinOp')
            for binop in binops:
                if binop.has(list_prop) and binop.op == 'Add':
                    explain('Addition can only be done with a single value at a time, not with an entire list at one'
                            ' time.<br><br><i>(sum_list)<i></br>')
    Returns:
    """
    message = 'Addition can only be done with a single value at a time, not with an entire list at one'
    code = "sum_list"
    tldr = "Cannot Sum a List"
    matches = find_matches("for ___ in _list_ :\n"
                           "    __expr__")
    if matches:
        for match in matches:
            _list_ = match["_list_"][0]
            __expr__ = match["__expr__"]
            # submatches = __expr__.find_matches("___ = ___ + {}".format(_list_.id), )
            submatches = __expr__.find_matches("___ = ___ + _list_")
            if submatches:
                return explain_r(message, code, label=tldr)
    return False


def missing_no_print():
    message = "Program does not output anything."
    code = "no_print"
    tldr = "Missing Output"
    prints = find_match('print(___)', cut=True)
    if not prints:
        return explain_r(message, code, label=tldr)
    return False


def missing_counting_list():
    """
    std_ast = parse_program()
    has_count = False
    for_loops = std_ast.find_all('For')
    if len(for_loops) > 0:
        for loop in for_loops:
            assignments = loop.find_all('Assign')
            if len(assignments) < 1:
                continue
            for assignment in assignments:
                binops = assignment.find_all('BinOp')
                if len(binops) < 1:
                    continue
                lhs = assignment.target
                for binop in binops:
                    if binop.has(lhs) and binop.has(1) and binop.op == 'Add':
                        has_count = True
    if not has_count:
        explain('Count the total number of items in the list using iteration.<br><br><i>(miss_count_list)<i></br>')
    Returns:
    """
    message = 'Count the total number of items in the list using iteration.'
    code = "miss_count_list"
    tldr = "Missing Count in Iteration"
    matches = find_matches("for _item_ in ___:\n"
                           "    __expr__")
    if matches:
        for match in matches:
            __expr__ = match["__expr__"]
            submatches = __expr__.find_matches("_sum_ = _sum_ + 1", )
            if submatches:
                return False
    return explain_r(message, code, label=tldr)


def missing_summing_list():
    """
    std_ast = parse_program()
    has_total = False
    for_loops = std_ast.find_all('For')
    if len(for_loops) > 0:
        for loop in for_loops:
            assignments = loop.find_all('Assign')
            if len(assignments) < 1:
                continue
            iter_prop = loop.target
            for assignment in assignments:
                binops = assignment.find_all('BinOp')
                if len(binops) < 1:
                    continue
                lhs = assignment.target
                for binop in binops:
                    if binop.has(lhs) and binop.has(iter_prop) and binop.op == 'Add':
                        has_total = True
    if not has_total:
        explain('Sum the total of all list elements using iteration.<br><br><i>(miss_sum_list)<i></br>')
    Returns:
    """
    message = 'Sum the total of all list elements using iteration.'
    code = "miss_sum_list"
    tldr = "Missing Sum in Iteration"
    matches = find_matches("for _item_ in ___:\n"
                           "    __expr__")
    if matches:
        for match in matches:
            _item_ = match["_item_"][0]
            __expr__ = match["__expr__"]
            submatches = __expr__.find_matches("_sum_ = _sum_ + _item_")
            if submatches:
                return False
    return explain_r(message, code, label=tldr)


def missing_zero_initialization():
    """

    std_ast = parse_program()
    for_loops = std_ast.find_all('For')
    accumulator = None
    loop_acu = None
    for loop in for_loops:
        assignments = loop.find_all('Assign')
        for assignment in assignments:
            binops = assignment.find_all('BinOp')
            if len(binops) > 0:
                lhs = assignment.target
                for binop in binops:
                    if binop.has(lhs) and binop.op == 'Add':
                        accumulator = lhs
                        loop_acu = loop
    accu_init = False
    if accumulator is not None:
        assignments = std_ast.find_all('Assign')
        for assignment in assignments:
            if loop_acu.lineno > assignment.lineno:
                lhs = assignment.target
                if lhs.id == accumulator.id and assignment.has(0):
                    accu_init = True
                    break
    if not accu_init and accumulator is not None:
        explain('The addition on the first iteration step is not correct because either the variable '
                '<code>{0!s}</code> has not been initialized to an appropriate initial value or it has not been placed'
                ' in an appropriate location<br><br><i>(miss_zero_init)<i></br>'.format(accumulator.id))
        return False
    return True
    Returns:
    """

    message = ('The addition on the first iteration step is not correct because either the variable <code>{0!s}</code> '
               'has not been initialized to an appropriate initial value '
               'or it has not been placed in an appropriate location')
    code = "miss_zero_init"
    tldr = "Missing Initialization for Accumulator"
    matches01 = find_matches("for ___ in ___:\n"
                             "    __expr__")
    if matches01:
        for match01 in matches01:
            __expr__ = match01["__expr__"]
            submatches01 = __expr__.find_matches("_sum_ = _sum_ + ___", )
            if submatches01:
                for submatch01 in submatches01:
                    _sum_ = submatch01["_sum_"][0]
                    matches02 = find_matches(("{} = 0\n"
                                              "for ___ in ___:\n"
                                              "    __expr__").format(_sum_.id))
                    if not matches02:
                        return explain_r(message.format(_sum_.id), code, label=tldr)
    return False


def wrong_printing_list():
    message = 'You should be printing a single value.'
    code = "list_print"
    tldr = "Printing in Iteration"
    matches = find_matches("for ___ in ___:\n"
                           "    __expr__")
    if matches:
        for match in matches:
            __expr__ = match["__expr__"]
            if __expr__.find_matches("print(___)", ):
                return explain_r(message, code, label=tldr)
    return False


# TODO: This might be reason to rethink letting instructor symbols map to multiple items
def missing_average():
    message = "An average value is not computed.<"
    code = "no_avg"
    tldr = "Missing Computation"
    matches_missing = find_matches("for ___ in ___:\n"
                                   "    pass\n"
                                   "__expr__")
    matches = []
    if matches_missing:
        for match in matches_missing:
            __expr__ = match["__expr__"]
            sub_matches = __expr__.find_matches("_total_/_count_", )
            if sub_matches:
                for sub_match in sub_matches:
                    _total_ = sub_match["_total_"][0]
                    _count_ = sub_match["_count_"][0]
                    if _total_.id != _count_.id:
                        matches.append(match)
    if not len(matches) > 0:
        return explain_r(message, code, label=tldr)
    return False


def warning_average_in_iteration():
    message = ('An average value is best computed after the properties name <code>{0!s}</code>(total) and '
               '<code>{1!s}</code> are completely known rather than recomputing the average on each iteration.')
    code = "avg_in_iter"
    tldr = "Redundant Average Calculation"
    matches = find_matches("for ___ in ___:\n"
                           "    __expr__\n")
    if matches:
        for match in matches:
            __expr__ = match["__expr__"]
            submatches = __expr__.find_matches("_average_ = _total_/_count_", )
            if submatches:
                for submatch in submatches:
                    _total_ = submatch["_total_"][0]
                    _count_ = submatch["_count_"][0]
                    _average_ = submatch["_average_"][0]
                    if _total_.id != _count_.id != _average_.id and _total_.id != _average_.id:
                        return explain_r(message.format(_total_.id, _count_.id), code, label=tldr)

    return False


def wrong_average_denominator():
    message = "The average is not calculated correctly."
    code = "avg_denom"
    tldr = "Incorrect Average Calculation"
    matches = find_matches("for ___ in ___:\n"
                           "    __expr__\n"  # where expr contains _count_ = _count_ + 1
                           "__expr2__")  # where expr2 contains ___/_value_
    # where _value_.id != _count_.id
    if matches:
        for match in matches:
            __expr__ = match["__expr__"]
            __expr2__ = match["__expr2__"]
            # _value_ = match["_value_"][0]
            submatches = __expr__.find_matches("_count_ = _count_ + 1", )
            submatches02 = find_expr_sub_matches("___/_value_", __expr2__)
            if submatches and submatches02:
                for submatch in submatches:
                    for submatch02 in submatches02:
                        _count_ = submatch["_count_"][0]
                        _value_ = submatch02["_value_"][0]
                        if _count_.id != _value_.id:
                            return explain_r(message, code, label=tldr)
    return False


def wrong_average_numerator():
    message = "The average is not calculated correctly."
    code = "avg_numer"
    tldr = "Incorrect Average Calculation"
    matches = find_matches("for _item_ in ___:\n"
                           "    __expr__\n"  # where expr contains _total_ = _total_ + 1
                           "__expr2__")  # where expr2 contains _value_/___
    if matches:
        for match in matches:
            __expr__ = match["__expr__"]
            __expr2__ = match["__expr2__"]
            _item_ = match["_item_"][0]
            # TODO: In theory, we could merge these matches to match variables...
            submatches = __expr__.find_matches("_total_ = _total_ + _item_")
            # submatches02 = find_expr_sub_matches("_value_/___", __expr2__)
            submatches02 = __expr2__.find_matches("_value_/___")
            if submatches and submatches02:
                for submatch in submatches:
                    for submatch02 in submatches02:
                        _value_ = submatch02["_value_"][0]
                        _total_ = submatch["_total_"][0]
                        if _total_.id != _value_.id:
                            return explain_r(message, code, label=tldr)
    return False


# #######################AVERAGE END###########################
def wrong_compare_list():
    message = "Each item in the list <code>{0!s}</code> must be compared one item at a time."
    code = "comp_list"
    tldr = "Not Comparing Each Item"
    matches = find_matches("for ___ in _list_:\n"
                           "    if __expr__:\n"
                           "        pass")
    if matches:
        for match in matches:
            _list_ = match["_list_"][0]
            __expr__ = match["__expr__"]
            if __expr__.has(_list_.astNode):
                return explain_r(message.format(_list_.id), code, label=tldr)
    return False


def wrong_for_inside_if():
    message = "The iteration should not be inside the decision block."
    code = "for_in_if"
    tldr = "For inside if"
    match = find_match("if ___:\n"
                       "    for ___ in ___:\n"
                       "        pass")
    if match:
        return explain_r(message, code, label=tldr)
    return False


def iterator_is_function():
    message = "You should make a variable for the list instead of using a function call for the list"
    code = "iter_is_func"
    tldr = "Using Function Call instead of List"
    std_ast = parse_program()
    for_loops = std_ast.find_all('For')
    # noinspection PyBroadException
    try:
        for loop in for_loops:
            list_prop = loop.iter
            if list_prop.ast_name == 'Call':
                return explain_r(message, code, label=tldr)
    except Exception:
        return False
    return False


# ##########################9.1 START############################
def wrong_list_initialization_9_1():
    message = "The list of rainfall amounts (<code>rainfall_list</code>) is not initialized properly."
    code = "list_init_9.1"
    tldr = "Incorrect List Initialization"
    match = find_match('rainfall_list = weather.get("Data.Precipitation","Station.Location","Blacksburg, VA")')
    if not match:
        return explain_r(message, code, label=tldr)
    return False


def wrong_accumulator_initialization_9_1():
    message = ("The variable to hold the total value of the rainfall amounts (<code>rainfall_sum</code>) "
               "is not initialized properly.")
    code = "accu_init_9.1"
    tldr = "Incorrect Accumulation Variable initialization"
    match = find_match("rainfall_sum = 0")
    if not match:
        return explain_r(message, code, label=tldr)
    return False


def wrong_accumulation_9_1():
    message = "The addition of each rainfall amount to <code>rainfall_sum</code> is not correct."
    code = "accu_9.1"
    tldr = "Incorrect Accumulation Statement"
    matches = find_matches("rainfall_sum = _item_ + rainfall")
    if matches:
        for match in matches:
            _item_ = match["_item_"][0]
            if _item_.id != "rainfall_sum":
                return explain_r(message, code, label=tldr)
    return False


def wrong_list_initialization_placement_9_1():
    message = ("The list of rainfall amount (<code>rainfall_list</code>) "
               "must be initialized before the iteration that uses this list.")
    code = "list_init_place_9.1"
    tldr = "List initialization Misplaced or Missing"
    match = find_match("rainfall_list = ___\n"
                       "for _item_ in _list_:\n"
                       "    pass")
    if not match:
        return explain_r(message, code, label=tldr)
    return False


def wrong_accumulator_initialization_placement_9_1():
    message = ("The variable for the sum of all the rainfall amounts (<code>rainfall_sum</code>) "
               "must be initialized before the iteration which uses this variable.")
    code = "accu_init_place_9.1"
    tldr = "Accumulator Initialization Misplaced or missing"
    matches = find_matches("rainfall_sum = ___\n"
                           "for _item_ in _list_:\n"
                           "    pass")
    if not matches:
        return explain_r(message, code, label=tldr)
    return False


def wrong_iteration_body_9_1():
    message = "The addition of each rainfall amount to the total rainfall is not in the correct place."
    code = "iter_body_9.1"
    tldr = "Accumulation Statement Misplaced or Missing"
    matches = find_matches("for _item_ in _list_:\n"
                           "    rainfall_sum = ___")
    if not matches:
        return explain_r(message, code, label=tldr)
    return False


def wrong_print_9_1():
    """
    Returns:
    """
    message = ('The output of the total rainfall amount is not in the correct place. The total rainfall should be '
               'output only once after the total rainfall has been computed.')
    code = "print_9.1"
    tldr = "Print Statement Misplaced or Missing"
    match = find_match("for _item_ in _list_:\n"
                       "    pass\n"
                       "print(_total_)")
    if not match:
        return explain_r(message, code, label=tldr)
    return False


# ##########################9.1 END############################


# ##########################9.2 START############################
def wrong_list_initialization_9_2():
    message = "The list of rainfall amounts (<code>rainfall_list</code>) is not initialized properly."
    code = "list_init_9.2"
    tldr = "Incorrect List Initialization"
    matches = find_matches('rainfall_list = weather.get("Data.Precipitation","Station.Location","Blacksburg, VA")')
    if not matches:
        return explain_r(message, code, label=tldr)
    return False


def wrong_accumulator_initialization_9_2():
    message = ("The variable to hold the total value of the rainfall amounts "
               "(<code>rainfall_count</code>) is not initialized properly.")
    code = "accu_init_9.2"
    tldr = "Incorrect Initialization"
    if not find_matches("rainfall_count = 0"):
        return explain_r(message, code, label=tldr)
    return False


def wrong_accumulation_9_2():
    message = ('The adding of another day with rainfall to the total '
               'count of days with rainfall (<code>rainfall_count</code>) is not correct.')
    code = "accu_9.2"
    tldr = "Accumulation Statement Incorrect"
    matches = find_matches("rainfall_count = _item_ + 1")
    if matches:
        for match in matches:
            _item_ = match["_item_"][0]
            if _item_.id != "rainfall_count":
                return explain_r(message, code, label=tldr)
    return False


def wrong_list_initialization_placement_9_2():
    message = ("The list of rainfall amount (<code>rainfall_list</code>) "
               "must be initialized before the iteration that uses this list.")
    code = "list_init_place_9.2"
    tldr = "Incorrect List Initialization Placement"
    matches = find_matches("rainfall_list = ___\n"
                           "for _item_ in _list_:\n"
                           "    pass")
    if not matches:
        return explain_r(message, code, label=tldr)
    return False


def wrong_accumulator_initialization_placement_9_2():
    message = ("The variable for the count of the number of days having rain (<code>rainfall_count</code>) "
               "must be initialized before the iteration which uses this variable.")
    code = "accu_init_place_9.2"
    tldr = "Accumulator Initialization Misplaced"
    matches = find_matches("rainfall_count = ___\n"
                           "for _item_ in _list_:\n"
                           "    pass")
    if not matches:
        return explain_r(message, code, label=tldr)
    return False


def wrong_iteration_body_9_2():
    message = ("The test (if) to determine if a given amount "
               "of rainfall is greater than (>) zero is not in the correct place.")
    code = "iter_body_9.2"
    tldr = "If statement misplaced"
    matches = find_matches("for _item_ in _list_:\n"
                           "    if __expr__:\n"
                           "        pass")
    if matches:
        for match in matches:
            __expr__ = match["__expr__"]
            if __expr__.numeric_logic_check(1, 'var > 0'):
                return False
    return explain_r(message, code, label=tldr)


def wrong_decision_body_9_2():
    message = ("The increase by 1 in the number of days having rainfall "
               "(<code>rainfall_count</code>) is not in the correct place.")
    code = "dec_body_9.2"
    tldr = "Accumulation Statement Misplaced"
    matches = find_matches("if __expr__:\n"
                           "    rainfall_count = rainfall_count + 1")
    if matches:
        for match in matches:
            __expr__ = match["__expr__"]
            if __expr__.numeric_logic_check(1, 'var > 0'):
                return False
    return explain_r(message, code, label=tldr)


def wrong_print_9_2():
    message = ("The output of the total number of days with rainfall is not in the correct place. The total number of "
               "days should be output only once after the total number of days has been computed.")
    code = "print_9.2"
    tldr = "Misplaced Print Statement"
    match = find_match("for _item_ in _list_:\n"
                       "    pass\n"
                       "print(_total_)")
    if not match:
        return explain_r(message, code, label=tldr)
    return False


# ##########################9.2 END############################


# ##########################9.6 START############################
def wrong_comparison_9_6():
    message = "In this problem you should be finding temperatures above 80 degrees."
    code = "comp_9.6"
    tldr = "Incorrect Comparison Statement"
    matches = find_matches("if __comp__:\n"
                           "    pass")
    if matches:
        for match in matches:
            __comp__ = match["__comp__"]
            if not __comp__.numeric_logic_check(1, 'var > 80'):
                return explain_r(message, code, label=tldr)
    return False


# ##########################9.6 END############################


# ##########################10.2 START############################
def wrong_conversion_10_2():
    """
    '''missing
    for _target_ in ____ :
        _target_ * 0.4
    '''
    Returns:
    """
    message = "The conversion of <code>{0!s}</code> to inches is either missing, incorrect, or misplaced."
    code = "conv_10.2"
    tldr = "Incorrect/Missing Conversion"
    matches = find_matches("for _target_ in ___:\n"
                           "    __expr__")
    for match in matches:
        # code version 1 start
        _target_ = match["_target_"][0]
        __expr__ = match["__expr__"]
        matches02 = __expr__.find_matches("_target_*0.04".format(_target_.id))
        if matches02:
            return False
        return explain_r(message.format(_target_.id), code, label=tldr)
    return False


# ##########################10.2 END############################


# ##########################10.3 START############################
def wrong_filter_condition_10_3():
    message = "The condition used to filter the year when artists died is not correct."
    code = "filt_10.3"
    tldr = "Incorrect Condition"
    matches = find_matches("if __expr__:\n"
                           "    pass")
    if matches:
        for match in matches:
            __expr__ = match["__expr__"]
            if __expr__.numeric_logic_check(1, "var > 0") or __expr__.numeric_logic_check(1, "var != 0"):
                return False
        return explain_r(message, code, label=tldr)
    return False


# ##########################10.3 END############################


# ##########################10.4 START############################
def wrong_and_filter_condition_10_4():
    message = ("The condition used to filter the temperatures "
               "into the specified range of temperatures is not correct.")
    code = "filt_and_10.4"
    tldr = "Incorrect Condition Statement"
    matches = find_matches("for _temp_ in _list_:\n"
                           "    if __expr__:\n"
                           "        pass")
    if matches:
        for match in matches:
            _temp_ = match["_temp_"][0]
            __expr__ = match["__expr__"]
            if (__expr__.has(_temp_.astNode) and
                    not __expr__.numeric_logic_check(1, "32 <= temp <= 50")):
                return explain_r(message, code, label=tldr)
    return False


def wrong_nested_filter_condition_10_4():
    message = ("The decisions used to filter the temperatures into "
               "the specified range of temperatures is not correct.")
    code = "nest_filt_10.4"
    tldr = "Incorrect Set of Decisions"
    matches = find_matches("for _temp_ in _list_:\n"
                           "    if __cond1__:\n"
                           "        if __cond2__:\n"
                           "            pass")
    if matches:
        for match in matches:
            _temp_ = match["_temp_"][0].astNode
            __cond1__ = match["__cond1__"]
            __cond2__ = match["__cond2__"]
            if not (__cond1__.has(_temp_) and __cond2__.has(_temp_) and (
                    __cond1__.numeric_logic_check(1, "32 <= temp") and __cond2__.numeric_logic_check(1, "temp <= 50") or
                    __cond2__.numeric_logic_check(1, "32 <= temp") and
                    __cond1__.numeric_logic_check(1, "temp <= 50"))):
                return explain_r(message, code, label=tldr)
    return False


# ##########################10.4 END############################


# ########################10.5 START###############################
def wrong_conversion_problem_10_5():
    message = "The conversion from kilometers to miles is not correct."
    code = "conv_10.5"
    tldr = "Incorrect Conversion"
    matches = find_matches("for _item_ in ___:\n"
                           "    __expr__")
    if matches:
        for match in matches:
            _item_ = match["_item_"][0]
            __expr__ = match["__expr__"]
            matches02 = __expr__.find_matches("_item_*0.62")
            if matches02:
                return False
        return explain_r(message, code, label=tldr)
    return False


def wrong_filter_problem_atl1_10_5():
    """
    find pattern where expression is equal to _item_*0.62 and
    where the condition is not equivalent to _expr_ > 10
    Returns:
    """
    message = "You are not correctly filtering out values from the list."
    code = "filt_alt1_10.5"
    tldr = "Incorrect Filter Statement"
    matches = find_matches("for _item_ in ___:\n"
                           "    if __cond__:\n"
                           "        _list_.append(__expr__)")
    if matches:
        for match in matches:
            _item_ = match["_item_"][0].astNode
            __cond__ = match["__cond__"]
            __expr__ = match["__expr__"]
            # matches02 = __expr__.find_matches("{0!s}*0.62".format(_item_.id))
            matches02 = __expr__.find_matches("_item_*0.62")
            if matches02:
                for match02 in matches02:
                    if (__cond__.has(_item_) and
                            not __cond__.numeric_logic_check(0.1, "item > 16.1290322580645")):
                        return explain_r(message, code, label=tldr)
    return False


def wrong_filter_problem_atl2_10_5():
    message = "You are not correctly filtering out values from the list."
    code = "filt_alt2_10.5"
    tldr = "Incorrect Filter Statement"
    matches = find_matches("for _item_ in ___:\n"
                           "    _miles_ = __expr__\n"
                           "    if __cond__:\n"
                           "        _list_.append(_miles_)")
    if matches:
        for match in matches:
            __expr__ = match["__expr__"]
            __cond__ = match["__cond__"]
            _item_ = match["_item_"][0].astNode
            _miles_ = match["_miles_"][0].astNode
            matches02 = __expr__.find_matches("_item_*0.62")
            for _ in matches02:
                if not (__cond__.has(_miles_) and
                        __cond__.numeric_logic_check(1, "_item_ > 10")):
                    return explain_r(message, code, label=tldr)
    return False


def wrong_append_problem_atl1_10_5():
    message = "You are not appending the correct values.<br><br><i>(app_alt1_10.5"
    code = "app_alt1_10.5"
    tldr = "Incorrect Value Appended"
    matches = find_matches("for _item_ in ___:\n"
                           "    if __cond__:\n"
                           "        _list_.append(__expr__)")
    if matches:
        for match in matches:
            _item_ = match["_item_"][0].astNode
            __cond__ = match["__cond__"]
            __expr__ = match["__expr__"]
            if (__cond__.numeric_logic_check(0.1, "item > 16.1290322580645") and
                    __cond__.has(_item_)):
                # new_code = "{}*0.62".format(_item_.id)
                new_code = "_item_*0.62"
                matches02 = __expr__.find_matches(new_code)
                if not matches02:
                    return explain_r(message, code, label=tldr)
    return False


def wrong_append_problem_atl2_10_5():
    message = "You are not appending the correct values."
    code = "app_alt2_10.5"
    tldr = "Incorrect Value Appended"
    matches = find_matches("for _item_ in ___:\n"
                           "    _miles_ = _item_ * 0.62\n"
                           "    if __cond__:\n"
                           "        _list_.append(_var_)")
    for match in matches:
        __cond__ = match["__cond__"]
        _miles_ = match["_miles_"][0]
        _var_ = match["_var_"][0]
        if __cond__.has(_miles_) and __cond__.numeric_logic_check(1, "_miles_ > 10"):
            if _var_.id != _miles_.id:
                return explain_r(message, code, label=tldr)
    return False


# ########################10.5 END###############################
def wrong_debug_10_6():
    """
    Should be on change feedback as opposed to on-run
    Returns:
    """
    message = "This is not one of the two changes needed. Undo the change and try again."
    code = "debug_10.6"
    tldr = "At least one unnecessary change"
    matches = find_matches('quakes = earthquakes.get("location.depth","(None)","")\n'
                           'quakes_in_miles = []\n'
                           'for quake in _list1_:\n'
                           '    _list2_.append(quake * 0.62)\n'
                           'plt.hist(quakes_in_miles)\n'
                           'plt.xlabel("Depth in Miles")\n'
                           'plt.ylabel("Number of Earthquakes")\n'
                           'plt.title("Distribution of Depth in Miles of Earthquakes")\n'
                           'plt.show()')
    for match in matches:
        name1 = match["_list1_"][0].ast_node.id
        name2 = match["_list2_"][0].ast_node.id
        master_list = ["quake", "quakes", "quakes_in_miles"]
        if (name1 in master_list and name2 in master_list and
                name1 != "quakes_in_miles" and name2 != "quakes" and
                (name1 != "quake" or name2 != "quake")):
            return False
    return explain_r(message, code, label=tldr)


def wrong_debug_10_7():
    message = "This is not the change needed. Undo the change and try again."
    code = "debug_10.7"
    tldr = "At least one unnecessary change"
    match = find_match("filtered_sentence_counts = []\n"
                       "book_sentence_counts = classics.get('metrics.statistics.sentences','(None)','')\n"
                       "for book in book_sentence_counts:\n"
                       "    if book >= 5000:\n"
                       "        filtered_sentence_counts.append(book)\n"
                       "plt.hist(filtered_sentence_counts)\n"
                       "plt.title('Distribution of Number of Sentences in Long Books')\n"
                       "plt.xlabel('Number of Sentences')\n"
                       "plt.ylabel('Number of Long Books')\n"
                       "plt.show()\n")

    if not match:
        return explain_r(message, code, label=tldr)
    return False


# ########################.....###############################
def wrong_initialization_in_iteration():
    message = ("You only need to initialize <code>{0!s}</code> once. "
               "Remember that statements in an iteration block happens multiple times")
    code = "wrong_init_in_iter"
    tldr = "Initialization in Iteration"
    matches = find_matches("for ___ in ___:\n"
                           "    __expr__")
    if matches:
        for match in matches:
            __expr__ = match["__expr__"]
            submatches = __expr__.find_matches("_assign_ = __expr__", )
            if submatches:
                for submatch in submatches:
                    __expr__sub = submatch["__expr__"]
                    _assign_ = submatch["_assign_"][0].astNode
                    if len(__expr__sub.find_all("Name")) == 0:
                        return explain_r(message.format(_assign_.id), code, label=tldr)
    return False


def wrong_duplicate_var_in_add():
    message = "You are adding the same variable twice; you need two different variables in your addition."
    code = "dup_var"
    tldr = "Duplicate Division"
    match = find_match("_item_ + _item_")
    if match:
        return explain_r(message, code, label=tldr)
    return False


# ########################PLOTTING###############################
def plot_group_error(output=None, plots=None):
    if output is None:
        output = get_output()
    if plots is None:
        plots = get_plots()
    if len(plots) > 1:
        explain_r('You should only be plotting one thing!', "print_one", "Multiple Calls to plot")
        return True
    elif len(plots) == 0:
        explain_r('The algorithm is plotting an empty list. Check your logic.', 'blank_plot', "Blank Plot")
        return True
    elif output:
        explain('You should be plotting, not printing!', 'printing', "Printing instead of Plotting")
        return True
    elif len(plots[0]['data']) != 1:
        explain('You should only be plotting one thing!', 'one_plot', "Too Many Plots")
        return True


def all_labels_present():  # TODO: make sure it's before the show, maybe check for default values
    """
    plt.title("Distribution of Number of Sentences in Long Books")
    plt.xlabel("Number of Sentences")
    plt.ylabel("Number of Long Books")
    plt.show()
    Returns:
    """
    message = "Make sure you supply labels to all your axes and provide a title and then call show"
    code = "labels_present"
    tldr = "Missing Label(s)"
    match = find_match("plt.title(___)\nplt.show()")
    match02 = find_match("plt.xlabel(___)\nplt.show()")
    match03 = find_match("plt.ylabel(___)\nplt.show()")

    if (not match) or (not match02) or (not match03):
        return gently_r(message, code, label=tldr)
    return False


def show_parens():
    message = "Make sure you add parenthesis to <code>plt.show</code>"
    code = "show_parens"
    tldr = "Incorrect Show"
    if not find_match("plt.show"):
        return gently_r()
    return False


def hard_code_8_5():  # TODO: This one's weird
    message = "Use iteration to calculate the sum."
    code = "hard_code_8.5"
    tldr = "Hard Coded Answer"
    match = find_matches("print(__num__)")
    if match:
        for m in match:
            __num__ = m["__num__"]
            if len(__num__.find_all("Num")) > 0:
                return explain_r(message, code, label=tldr)
    return False
