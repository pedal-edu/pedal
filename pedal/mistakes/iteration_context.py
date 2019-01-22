from pedal.cait.cait_api import (parse_program,
                                 find_matches, find_match,
                                 find_expr_sub_matches)
from pedal.report.imperative import explain, gently
import pedal.mistakes.instructor_append as append_api
from pedal.toolkit.utilities import *
from pedal.sandbox.compatibility import get_output


# ################8.2 Start#######################
def wrong_list_length_8_2():
    matches = find_matches("_list_ = __expr__")
    if matches:
        for match in matches:
            __expr__ = match["__expr__"]
            if __expr__.ast_name == "List" and len(__expr__.elts) < 3:
                explain('You must have at least three pieces<br><br><i>(list length_8.2)<i></br>')
                return True
    return False


def missing_list_initialization_8_2():
    matches = find_matches("shopping_cart = __expr__")
    for match in matches:
        __expr__ = match["__expr__"]
        if __expr__.ast_name == "List":
            return False
    explain(
        'You must set the variable <code>shopping_cart</code> to a list containing the prices of items in the'
        ' shopping cart.<br><br><i>(missing_list_init_8.2)<i></br>')
    return True


def wrong_list_is_constant_8_2():
    matches = find_matches("shopping_cart = __expr__")
    for match in matches:
        __expr__ = match["__expr__"]
        if __expr__.ast_name == "Num":
            explain(
                'You must set <code>shoppping_cart</code> to a list of values not to a single number.<br><br><i>'
                '(list_is_const_8.2)<i></br>')
            return True
    return False


def list_all_zeros_8_2():
    std_ast = parse_program()
    lists = std_ast.find_all('List')
    is_all_zero = True
    for init_list in lists:
        for node in init_list.elts:
            if node.ast_name == 'Num' and node.n != 0:
                is_all_zero = False
                break
        if is_all_zero:
            break
    if is_all_zero:
        explain('Try seeing what happens when you change the numbers in the list.<br><br><i>(default_list_8.2)<i></br>')
        return True
    return False


# ################8.2 End#######################


# ################8.3 Start#######################
def wrong_list_initialization_placement_8_3():
    for_matches = find_matches("for ___ in ___:\n"
                               "    pass")
    init_matches = find_matches("episode_length_list = ___")
    if init_matches and for_matches:
        for for_match in for_matches:
            for_lineno = for_match.match_lineno
            for init_match in init_matches:
                if init_match.match_lineno > for_lineno:
                    explain(
                        'The list of episode lengths (<code>episode_length_list</code>) must be initialized before the'
                        ' iteration which uses this list.<br><br><i>(init_place_8.3)<i></br>')
                    return True
    return False


def wrong_accumulator_initialization_placement_8_3():
    for_matches = find_matches("for ___ in ___:"
                               "    pass")
    init_matches = find_matches("sum_length = 0")
    if init_matches and for_matches:
        for for_match in for_matches:
            for_lineno = for_match.match_lineno
            for init_match in init_matches:
                if init_match.match_lineno > for_lineno:
                    explain(
                        'The variable to hold the sum of the episode lengths (<code>sum_length</code>) must be '
                        'initialized before the iteration which uses this variable.<br><br><i>'
                        '(accu_init_place_8.3)<i></br>')
                    return True
    return False


def wrong_iteration_body_8_3():
    match = find_match("for _item_ in _list_:\n"
                       "    sum_length = ___ + ___\n")
    if not match:
        explain('The addition of each episode length to the total length is not in the correct place.<br><br><i>'
                '(iter_body_8.3)<i></br>')
        return True
    return False


def wrong_print_8_3():
    match = find_match("for _item_ in _list_:\n"
                       "    pass\n"
                       "print(_total_)")
    if not match:
        explain('The output of the total length of time is not in the correct place. The total length of time should be'
                ' output only once after the total length of time has been computed.<br><br><i>(print_8.3)<i></br>')
        return True
    return False


# ################8.3 End#######################


# ################8.4 Start#######################
def missing_target_slot_empty_8_4():
    matches = find_matches("for _item_ in pages_count_list:\n"
                           "    pass")
    if matches:
        for match in matches:
            _item_ = match["_item_"][0]
            if _item_.id == "___":
                explain('You must fill in the empty slot in the iteration.<br><br><i>(target_empty_8.4)<i></br>')
                return True
    return False


def missing_addition_slot_empty_8_4():
    matches = find_matches("sum_pages + _item_")
    if matches:
        for match in matches:
            _item_ = match["_item_"][0]
            if _item_.id == "___":
                explain('You must fill in the empty slot in the addition.<br><br><i>(add_empty_8.4)<i></br>')
                return True
    return False


def wrong_names_not_agree_8_4():
    matches = find_matches("for _item1_ in pages_count_list:\n"
                           "    sum_pages = sum_pages + _item2_")
    if matches:
        for match in matches:
            # in theory, these will always be different? should test in test_cait
            _item1_ = match["_item1_"][0]
            _item2_ = match["_item2_"][0]
            if _item1_.id != _item2_.id:
                explain('Each value of <code>{0!s}</code> must be added to <code>{1!s}</code>.<br><br><i>'
                        '(name_agree_8.4)<i></br>'.format(_item1_.id, _item2_.id))
                return True
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
    match = find_match("[20473, 27630, 17849, 19032, 16378]")
    if not match:
        explain('Don\'t modify the list<br><br><i>(mod_list_8.5)<i></br>')
        return True
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
    match = find_match("_list_ = [2.9, 1.5, 2.3, 6.1]")
    if not match:
        explain('Don\'t modify the list<br><br><i>(mod_list_8.6)<i></br>')
        return True
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
    matches = find_matches("for _item_ in ___:\n"
                           "    __expr__")
    if matches:
        for match in matches:
            _item_ = match["_item_"][0]
            __expr__ = match["__expr__"]
            submatches = __expr__.find_matches("___ = ___ + {}".format(_item_.id), )
            if submatches:
                explain(
                    'This problem asks for the number of items in the list not the total of all the values in the list.'
                    '<br><br><i>(not_count)<i></br>')
                return True
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
    matches = find_matches("for _item_ in ___:\n"
                           "    __expr__")
    if matches:
        for match in matches:
            __expr__ = match["__expr__"]
            submatches = __expr__.find_matches("___ = 1 + ___", )
            if submatches:
                explain('This problem asks for the total of all the values in the list not the number of '
                        'items in the list.<br><br><i>(not_sum)<i></br>')
                return True
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
    matches = find_matches("___ + _item_")
    if matches:
        for match in matches:
            _item_ = match["_item_"][0]
            if _item_.id == "___":
                explain('You must fill in the empty slot in the addition.<br><br><i>(add_empty)<i></br>')
                return True
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
    matches = find_matches("for ___ in _list_ :\n"
                           "    __expr__")
    if matches:
        for match in matches:
            _list_ = match["_list_"][0]
            __expr__ = match["__expr__"]
            submatches = __expr__.find_matches("___ = ___ + {}".format(_list_.id), )
            if submatches:
                explain('Addition can only be done with a single value at a time, not with an entire list at one'
                        ' time.<br><br><i>(sum_list)<i></br>')
                return True
    return False


def missing_no_print():
    prints = find_match('print(___)', cut=True)
    if not prints:
        explain('Program does not output anything.<br><br><i>(no_print)<i></br>')
        return True
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
    matches = find_matches("for _item_ in ___:\n"
                           "    __expr__")
    if matches:
        for match in matches:
            __expr__ = match["__expr__"]
            submatches = __expr__.find_matches("_sum_ = _sum_ + 1", )
            if submatches:
                return False
    explain(
        'Count the total number of items in the list using iteration.<br><br><i>(miss_count_list)<i></br>')
    return True


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
    matches = find_matches("for _item_ in ___:\n"
                           "    __expr__")
    if matches:
        for match in matches:
            _item_ = match["_item_"][0]
            __expr__ = match["__expr__"]
            submatches = find_expr_sub_matches("_sum_ = _sum_ + {}"
                                               .format(_item_.id), __expr__)
            if submatches:
                return False
    explain('Sum the total of all list elements using iteration.<br><br><i>(miss_sum_list)<i></br>')
    return True


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
                        explain('The addition on the first iteration step is not correct because either the variable '
                                '<code>{0!s}</code> has not been initialized to an appropriate initial value or it has '
                                'not been placed in an appropriate location<br><br><i>'
                                '(miss_zero_init)<i></br>'.format(_sum_.id))
                        return True
    return False


def wrong_printing_list():
    matches = find_matches("for ___ in ___:\n"
                           "    __expr__")
    if matches:
        for match in matches:
            __expr__ = match["__expr__"]
            if __expr__.find_matches("print(___)", ):
                explain('You should be printing a single value.<br><br><i>(list_print)<i></br>')
                return True
    return False


# TODO: This might be reason to rethink letting instructor symbols map to multiple items
def missing_average():
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
        explain('An average value is not computed.<br><br><i>(no_avg)<i></br>')
        return True
    return False


def warning_average_in_iteration():
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
                        explain('An average value is best computed after the properties name <code>{0!s}</code>(total)'
                                ' and <code>{1!s}</code> are completely known rather than recomputing the average on'
                                ' each iteration.<br><br><i>(avg_in_iter)<i></br>'.format(_total_.id, _count_.id))
                        return True

    return False


def wrong_average_denominator():
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
                            explain('The average is not calculated correctly.<br><br><i>(avg_denom)<i></br>')
                            return True
    return False


def wrong_average_numerator():
    matches = find_matches("for _item_ in ___:\n"
                           "    __expr__\n"  # where expr contains _total_ = _total_ + 1
                           "__expr2__")  # where expr2 contains _value_/___
    if matches:
        for match in matches:
            __expr__ = match["__expr__"]
            __expr2__ = match["__expr2__"]
            _item_ = match["_item_"][0]
            submatches = __expr__.find_matches("_total_ = _total_ + {}".format(_item_.id), )
            submatches02 = find_expr_sub_matches("_value_/___", __expr2__)
            if submatches and submatches02:
                for submatch in submatches:
                    for submatch02 in submatches02:
                        _value_ = submatch02["_value_"][0]
                        _total_ = submatch["_total_"][0]
                        if _total_.id != _value_.id:
                            explain('The average is not calculated correctly.<br><br><i>(avg_numer)<i></br>')
                            return True
    return False


# #######################AVERAGE END###########################
def wrong_compare_list():
    matches = find_matches("for ___ in _list_:\n"
                           "    if __expr__:\n"
                           "        pass")
    if matches:
        for match in matches:
            _list_ = match["_list_"][0]
            __expr__ = match["__expr__"]
            if __expr__.has(_list_.astNode):
                explain('Each item in the list <code>{0!s}</code> must be compared one item at a time.<br><br><i>'
                        '(comp_list)<i></br>'.format(_list_.id))
                return True
    return False


def wrong_for_inside_if():
    match = find_match("if ___:\n"
                       "    for ___ in ___:\n"
                       "        pass")
    if match:
        explain('The iteration should not be inside the decision block.<br><br><i>(for_in_if)<i></br>')
        return True
    return False


def iterator_is_function():
    std_ast = parse_program()
    for_loops = std_ast.find_all('For')
    # noinspection PyBroadException
    try:
        for loop in for_loops:
            list_prop = loop.iter
            if list_prop.ast_name == 'Call':
                explain('You should make a variable for the list instead of using a function call for the list'
                        '<br><br><i>(iter_is_func)<i></br>')
                return True
    except Exception:
        return False
    return False


# ##########################9.1 START############################
def wrong_list_initialization_9_1():
    match = find_match('rainfall_list = weather.get("Precipitation","Location","Blacksburg, VA")')
    if not match:
        explain('The list of rainfall amounts (<code>rainfall_list</code>) is not initialized properly.'
                '<br><br><i>(list_init_9.1)<i></br>')
        return True
    return False


def wrong_accumulator_initialization_9_1():
    match = find_match("rainfall_sum = 0")
    if not match:
        explain('The variable to hold the total value of the rainfall amounts (<code>rainfall_sum</code>) is not '
                'initialized properly.<br><br><i>(accu_init_9.1)<i></br>')
        return True
    return False


def wrong_accumulation_9_1():
    matches = find_matches("rainfall_sum = _item_ + rainfall")
    if matches:
        for match in matches:
            _item_ = match["_item_"][0]
            if _item_.id != "rainfall_sum":
                explain('The addition of each rainfall amount to <code>rainfall_sum</code> is not correct.'
                        '<br><br><i>(accu_9.1)<i></br>')
                return True
    return False


def wrong_list_initialization_placement_9_1():
    match = find_match("rainfall_list = ___\n"
                       "for _item_ in _list_:\n"
                       "    pass")
    if not match:
        explain('The list of rainfall amount (<code>rainfall_list</code>) must be initialized before the iteration that'
                ' uses this list.<br><br><i>(list_init_place_9.1)<i></br>')
        return True
    return False


# TODO: Convert this to matching API
def wrong_accumulator_initialization_placement_9_1():
    std_ast = parse_program()
    assignments = std_ast.find_all('Assign')
    loops = std_ast.find_all('For')
    list_init = None
    init_after_loop = False
    for assignment in assignments:
        if assignment.target.id == 'rainfall_sum':
            list_init = assignment
            break
    for loop in loops:
        if list_init is not None and loop.lineno > list_init.lineno:
            init_after_loop = True
            break
    if list_init is None or not init_after_loop:
        explain('The variable for the sum of all the rainfall amounts (<code>rainfall_sum</code>) must be initialized '
                'before the iteration which uses this variable.<br><br><i>(accu_init_place_9.1)<i></br>')


# TODO: Convert this to matching API
def wrong_iteration_body_9_1():
    std_ast = parse_program()
    loops = std_ast.find_all('For')
    assignment_in_for = False
    for loop in loops:
        assignments = loop.find_all('Assign')
        for assignment in assignments:
            if assignment.target.id == 'rainfall_sum':
                assignment_in_for = True
                break
        if assignment_in_for:
            break
    if not assignment_in_for:
        explain('The addition of each rainfall amount to the total rainfall is not in the correct place.<br><br><i>'
                '(iter_body_9.1)<i></br>')


def wrong_print_9_1():
    """

    std_ast = parse_program()
    for_loops = std_ast.find_all('For')
    # has_for = len(for_loops) > 0
    for_loc = []
    wrong_print_placement = True
    for loop in for_loops:
        end_node = loop.next_tree
        if end_node is not None:
            for_loc.append(end_node.lineno)
    calls = std_ast.find_all('Call')
    for call in calls:
        if call.func.id == 'print':
            for loc in for_loc:
                if call.func.lineno >= loc:
                    wrong_print_placement = False
                    break
            if not wrong_print_placement:
                break
    if wrong_print_placement:
        explain('The output of the total rainfall amount is not in the correct place. The total rainfall should be '
                'output only once after the total rainfall has been computed.<br><br><i>(print_9.1)<i></br>')
    Returns:
    """
    match = find_match("for _item_ in _list_:\n"
                       "    pass\n"
                       "print(_total_)")
    if not match:
        explain('The output of the total rainfall amount is not in the correct place. The total rainfall should be '
                'output only once after the total rainfall has been computed.<br><br><i>(print_9.1)<i></br>')
        return True
    return False


# ##########################9.1 END############################


# ##########################9.2 START############################
# TODO: Convert this to matching API
def wrong_list_initialization_9_2():
    std_ast = parse_program()
    assignments = std_ast.find_all('Assign')
    has_call = False
    for assignment in assignments:
        if assignment.target.id == 'rainfall_list':
            call = assignment.find_all('Call')
            if len(call) == 1:
                args = call[0].args
                if len(args) == 3:
                    if args[0].s == 'Precipitation' and args[1].s == 'Location' and args[2].s == 'Blacksburg, VA':
                        has_call = True
                        break
    if not has_call:
        explain('The list of rainfall amounts (<code>rainfall_list</code>) is not initialized properly.'
                '<br><br><i>(list_init_9.2)<i></br>')
    return not has_call


# TODO: Convert this to matching API
def wrong_accumulator_initialization_9_2():
    std_ast = parse_program()
    assignments = std_ast.find_all('Assign')
    has_assignment = False
    for assignment in assignments:
        if assignment.target.id == 'rainfall_count' and assignment.value.ast_name == 'Num':
            if assignment.value.n == 0:
                has_assignment = True
                break
    if not has_assignment:
        explain('The variable to hold the total value of the rainfall amounts (<code>rainfall_count</code>) is not '
                'initialized properly.<br><br><i>(accu_init_9.2)<i></br>')
    return not has_assignment


def wrong_accumulation_9_2():
    matches = find_matches("rainfall_count = _item_ + 1")
    if matches:
        for match in matches:
            _item_ = match["_item_"][0]
            if _item_.id != "rainfall_count":
                explain(
                    'The adding of another day with rainfall to the total count of days with rainfall '
                    '(<code>rainfall_count</code>) is not correct.<br><br><i>(accu_9.2)<i></br>')
                return True
    return False


# TODO: Convert this to matching API
def wrong_list_initialization_placement_9_2():
    std_ast = parse_program()
    assignments = std_ast.find_all('Assign')
    loops = std_ast.find_all('For')
    list_init = None
    init_after_loop = False
    for assignment in assignments:
        if assignment.target.id == 'rainfall_list':
            list_init = assignment
            break
    for loop in loops:
        if list_init is not None and loop.lineno > list_init.lineno:
            init_after_loop = True
            break
    if list_init is None or not init_after_loop:
        explain('The list of rainfall amount (<code>rainfall_list</code>) must be initialized before the iteration that'
                ' uses this list.<br><br><i>(list_init_place_9.2)<i></br>')
        return True
    return False


# TODO: Convert this to matching API
def wrong_accumulator_initialization_placement_9_2():
    std_ast = parse_program()
    assignments = std_ast.find_all('Assign')
    loops = std_ast.find_all('For')
    list_init = None
    init_after_loop = False
    for assignment in assignments:
        if assignment.target.id == 'rainfall_count':
            list_init = assignment
            break
    if list_init is not None:
        for loop in loops:
            if loop.lineno > list_init.lineno:
                init_after_loop = True
                break
    if list_init is None or not init_after_loop:
        explain('The variable for the count of the number of days having rain (<code>rainfall_count</code>) must be '
                'initialized before the iteration which uses this variable.<br><br><i>(accu_init_place_9.2)<i></br>')
        return True
    return False


def wrong_iteration_body_9_2():
    matches = find_matches("for _item_ in _list_:\n"
                           "    if __expr__:\n"
                           "        pass")
    if matches:
        for match in matches:
            __expr__ = match["__expr__"]
            if __expr__.numeric_logic_check(1, 'var > 0'):
                return False
    explain('The test (if) to determine if a given amount of rainfall is greater than (>) zero is not in the '
            'correct place.<br><br><i>(iter_body_9.2)<i></br>')
    return True


def wrong_decision_body_9_2():
    matches = find_matches("if __expr__:\n"
                           "    rainfall_count = rainfall_count + 1")
    if matches:
        for match in matches:
            __expr__ = match["__expr__"]
            if __expr__.numeric_logic_check(1, 'var > 0'):
                return False
    explain('The increase by 1 in the number of days having rainfall (<code>rainfall_count</code>) is not in the '
            'correct place.<br><br><i>(dec_body_9.2)<i></br>')
    return True


def wrong_print_9_2():
    match = find_match("for _item_ in _list_:\n"
                       "    pass\n"
                       "print(_total_)")
    if not match:
        explain('The output of the total number of days with rainfall is not in the correct place. The total number of '
                'days should be output only once after the total number of days has been computed.<br><br><i>'
                '(print_9.2)<i></br>')
        return True
    return False


# ##########################9.2 END############################


# ##########################9.6 START############################
def wrong_comparison_9_6():
    matches = find_matches("if __comp__:\n"
                           "    pass")
    if matches:
        for match in matches:
            __comp__ = match["__comp__"]
            if not __comp__.numeric_logic_check(1, 'var > 80'):
                explain(
                    'In this problem you should be finding temperatures above 80 degrees.<br><br><i>(comp_9.6)<i></br>')
                return True
    return False


# ##########################9.6 END############################


# ##########################10.2 START############################
def wrong_conversion_10_2():
    """
    '''
    # code version 2 start
    binops = __expr__.find_all('BinOp')
    for binop in binops:
        if binop.has(_target_.astNode) and binop.has(0.04) and binop.op_name == 'Mult':
            return False
    # code version 2 end
    '''
    Returns:
    """
    matches = find_matches("for _target_ in ___:\n"
                           "    __expr__")
    if matches:
        for match in matches:
            # code version 1 start
            _target_ = match["_target_"][0]
            __expr__ = match["__expr__"]
            matches02 = __expr__.find_matches("_target_*0.04", )
            if matches02:
                for match02 in matches02:
                    _target_02 = match02["_target_"][0]
                    if _target_.id == _target_02.id:
                        return False
            # code version 1 end
        explain('The conversion of <code>{0!s}</code> to inches is not correct.<br><br><i>'
                '(conv_10.2)<i></br>'.format(_target_.id))
        return True
    return False


# ##########################10.2 END############################


# ##########################10.3 START############################
def wrong_filter_condition_10_3():
    matches = find_matches("if __expr__:\n"
                           "    pass")
    if matches:
        for match in matches:
            __expr__ = match["__expr__"]
            if __expr__.numeric_logic_check(1, "var > 0") or __expr__.numeric_logic_check(1, "var != 0"):
                return False
        explain('The condition used to filter the year when artists died is not correct.<br><br><i>(filt_10.3)<i></br>')
        return True
    return False


# ##########################10.3 END############################


# ##########################10.4 START############################
def wrong_and_filter_condition_10_4():
    matches = find_matches("for _temp_ in _list_:\n"
                           "    if __expr__:\n"
                           "        pass")
    if matches:
        for match in matches:
            _temp_ = match["_temp_"][0]
            __expr__ = match["__expr__"]
            if (__expr__.has(_temp_.astNode) and
                    not __expr__.numeric_logic_check(1, "32 <= temp <= 50")):
                explain(
                    'The condition used to filter the temperatures into the specified range of temperatures is not '
                    'correct.<br><br><i>(filt_and_10.4)<i></br>')
                return True
    return False


def wrong_nested_filter_condition_10_4():
    matches = find_matches("for _temp_ in _list_:\n"
                           "    if __cond1__:\n"
                           "        if __cond2__:\n"
                           "            pass")
    if matches:
        for match in matches:
            _temp_ = match["_temp_"][0].astNode
            __cond1__ = match["__cond1__"]
            __cond2__ = match["__cond2__"]
            if not (
                    __cond1__.has(_temp_) and __cond2__.has(_temp_) and (
                    __cond1__.numeric_logic_check(
                        1,
                        "32 <= temp") and __cond2__.numeric_logic_check(
                1,
                "temp <= 50") or __cond2__.numeric_logic_check(
                1,
                "32 <= temp") and __cond1__.numeric_logic_check(
                1,
                "temp <= 50"))):
                explain(
                    'The decisions used to filter the temperatures into the specified range of temperatures is not '
                    'correct.<br><br><i>(nest_filt_10.4)<i></br>')
                return True
    return False


# ##########################10.4 END############################


# ########################10.5 START###############################
def wrong_conversion_problem_10_5():
    matches = find_matches("for _item_ in ___:\n"
                           "    __expr__")
    if matches:
        for match in matches:
            _item_ = match["_item_"][0]
            __expr__ = match["__expr__"]
            matches02 = __expr__.find_matches("_item_*0.62", )
            if matches02:
                for match02 in matches02:
                    _item_02 = match02["_item_"][0]
                    if _item_02.id == _item_.id:
                        return False
        explain('The conversion from kilometers to miles is not correct.<br><br><i>(conv_10.5)<i></br>')
        return True
    return False


def wrong_filter_problem_atl1_10_5():
    """
    find pattern where expression is equal to _item_*0.62 and
    where the condition is not equivalent to _expr_ > 10
    Returns:
    """

    matches = find_matches("for _item_ in ___:\n"
                           "    if __cond__:\n"
                           "        _list_.append(__expr__)")
    if matches:
        for match in matches:
            _item_ = match["_item_"][0].astNode
            __cond__ = match["__cond__"]
            __expr__ = match["__expr__"]
            matches02 = __expr__.find_matches("_item_*0.62", )
            if matches02:
                for match02 in matches02:
                    _item_02 = match02["_item_"][0].astNode
                    if (_item_.id == _item_02.id and
                            __cond__.has(_item_) and
                            not __cond__.numeric_logic_check(0.1, "item > 16.1290322580645")):
                        explain('You are not correctly filtering out values from the list.<br><br><i>'
                                '(filt_alt1_10.5)<i></br>')
                        return True
    return False


def wrong_filter_problem_atl2_10_5():
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
            matches02 = __expr__.find_matches("_item_*0.62", )
            if matches02:
                for match02 in matches02:
                    _item_02 = match02["_item_"][0].astNode
                    if _item_.id == _item_02.id:
                        if not (__cond__.has(_miles_) and
                                __cond__.numeric_logic_check(1, "_item_ > 10")):
                            explain('You are not correctly filtering out values from the list.<br><br><i>'
                                    '(filt_alt2_10.5)<i></br>')
                            return True
    return False


def wrong_append_problem_atl1_10_5():
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
                new_code = "{}*0.62".format(_item_.id)
                matches02 = __expr__.find_matches(new_code, )
                if not matches02:
                    explain('You are not appending the correct values.<br><br><i>(app_alt1_10.5)<i></br>')
                    return True
    return False


def wrong_append_problem_atl2_10_5():
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
                explain('You are not appending the correct values<br><br><i>(app_alt2_10.5)<i></br>')
                return True
    return False


# ########################10.5 END###############################
def wrong_debug_10_6():
    """




    Returns:
    """
    matches = find_matches('quakes = earthquakes.get("depth","(None)","")\n'
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
    explain('This is not one of the two changes needed. Undo the change and try again.<br><br><i>(debug_10.6)<i></br>')
    return True


def wrong_debug_10_7():
    match = find_match("filtered_sentence_counts = []\n"
                       "book_sentence_counts = classics.get('sentences','(None)','')\n"
                       "for book in book_sentence_counts:\n"
                       "    if book >= 5000:\n"
                       "        filtered_sentence_counts.append(book)\n"
                       "plt.hist(filtered_sentence_counts)\n"
                       "plt.title('Distribution of Number of Sentences in Long Books')\n"
                       "plt.xlabel('Number of Sentences')\n"
                       "plt.ylabel('Number of Long Books')\n"
                       "plt.show()\n")

    if not match:
        explain('This is not the change needed. Undo the change and try again.<br><br><i>(debug_10.7)<i></br>')
        return True
    return False


# ########################.....###############################
def wrong_initialization_in_iteration():
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
                        explain(
                            'You only need to initialize <code>{0!s}</code> once. Remember that statements in an '
                            'iteration block happens multiple times'
                            '<br><br><i>(wrong_init_in_iter)<i></br>'.format(_assign_.id))
                        return True
    return False


def wrong_duplicate_var_in_add():
    match = find_match("_item_ + _item_")
    if match:
        explain('You are adding the same variable twice; you need two different variables in your addition.'
                '<br><br><i>(dup_var)<i></br>')
        return True
    return False


# ########################PLOTTING###############################
def plot_group_error(output=None):
    if output is None:
        output = get_output()
    if len(output) > 1:
        explain('You should only be printing/plotting one thing!<br><br><i>(print_one)<i></br>')
        return True
    elif len(output) == 0:
        explain('The algorithm is plotting an empty list. Check your logic.<br><br><i>(blank_plot)<i></br>')
        return True
    elif not isinstance(output[0], list):
        explain('You should be plotting, not printing!<br><br><i>(printing)<i></br>')
        return True
    elif len(output[0]) != 1:
        explain('You should only be plotting one thing!<br><br><i>(one_plot)<i></br>')
        return True


def all_labels_present():  # TODO: make sure it's before the show, maybe check for default values
    """
    plt.title("Distribution of Number of Sentences in Long Books")
    plt.xlabel("Number of Sentences")
    plt.ylabel("Number of Long Books")
    plt.show()
    Returns:
    """

    match = find_match("plt.title(___)\nplt.show()")
    match02 = find_match("plt.xlabel(___)\nplt.show()")
    match03 = find_match("plt.ylabel(___)\nplt.show()")

    if (not match) or (not match02) or (not match03):
        gently('Make sure you supply labels to all your axes and provide a title and then call show'
               '<br><br><i>(labels_present)<i></br>')
        return True
    return False


# TODO: Convert this to matching API
def hard_code_8_5():  # TODO: This one's weird
    match = find_matches("print(__num__)")
    if match:
        for m in match:
            __num__ = m["__num__"]
            if len(__num__.find_all("Num")) > 0:
                explain("Use iteration to calculate the sum.<br><br><i>(hard_code_8.5)<i></br>")
                return True
    return False
