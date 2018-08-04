from pedal.cait.cait_api import *
from pedal.report.imperative import *
import pedal.mistakes.instructor_append as append_api
from pedal.toolkit.utilities import *
from pedal.sandbox.compatibility import *


# ################8.2 Start#######################
def wrong_list_length_8_2():
    matches = find_matches("_list_ = __expr__")
    if matches:
        for match in matches:
            __expr__ = match.exp_table.get("__expr__")
            if __expr__.ast_name == "List" and len(__expr__.elts) < 3:
                explain('You must have at least three pieces<br><br><i>(list length_8.2)<i></br>')
                return True
    return False


def missing_list_initialization_8_2():
    matches = find_matches("shopping_cart = __expr__")
    if matches:
        for match in matches:
            __expr__ = match.exp_table.get("__expr__")
            if __expr__.ast_name == "List":
                return False
    explain(
        'You must set the variable <code>shopping_cart</code> to a list containing the prices of items in the'
        ' shopping cart.<br><br><i>(missing_list_init_8.2)<i></br>')
    return True


def wrong_list_is_constant_8_2():
    matches = find_matches("shopping_cart = __expr__")
    if matches:
        for match in matches:
            __expr__ = match.exp_table.get("__expr__")
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
    for_matches = find_matches("for ___ in ___:"
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
    init_matches = find_matches("sum_length = ___")
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
            _item_ = match.symbol_table.get("_item_")[0]
            if _item_.id == "___":
                explain('You must fill in the empty slot in the iteration.<br><br><i>(target_empty_8.4)<i></br>')
                return True
    return False


def missing_addition_slot_empty_8_4():
    matches = find_matches("sum_pages + _item_")
    if matches:
        for match in matches:
            _item_ = match.symbol_table.get("_item_")[0]
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
            _item1_ = match.symbol_table.get("_item1_")[0]
            _item2_ = match.symbol_table.get("_item2_")[0]
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

    :return:
    """
    match = find_match("_list_ = [20473, 27630, 17849, 19032, 16378]")
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
    :return:
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
    :return:
    """
    match = find_match("for _item_ in ___:\n"
                       "    ___ = ___ + _item_")
    if match:
        explain('This problem asks for the number of items in the list not the total of all the values in the list.'
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
    match = find_match("for _item_ in ___:\n"
                       "    ___ = ___ + 1")
    if match:
        explain('This problem asks for the total of all the values in the list not the number of items in '
               'the list.<br><br><i>(not_sum)<i></br>')
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
    :return:
    """
    matches = find_matches("___ + _item_")
    if matches:
        for match in matches:
            _item_ = match.symbol_table.get("_item_")[0]
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
    :return:
    """
    match = find_matches("for ___ in _list_ :\n"
                         "    ___ = ___ + _list_")
    if match:
        explain('Addition can only be done with a single value at a time, not with an entire list at one'
                ' time.<br><br><i>(sum_list)<i></br>')
        return True
    return False


def missing_no_print():
    prints = find_match('print(___)')
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
    :return:
    """
    match = find_matches("for ___ in ___:\n"
                         "    _sum_ = _sum_ + 1")
    if not match:
        explain('Count the total number of items in the list using iteration.<br><br><i>(miss_count_list)<i></br>')
        return True
    return False


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
    :return:
    """
    match = find_matches("for _item_ in ___:\n"
                         "    _sum_ = _sum_ + _item_")
    if not match:
        explain('Sum the total of all list elements using iteration.<br><br><i>(miss_sum_list)<i></br>')
        return True
    return False


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
    :return:
    """
    matches01 = find_matches("for ___ in ___:\n"
                             "    _sum_ = _sum_ + ___")
    if matches01:
        matches02 = find_matches("_sum_ = 0")
        for match01 in matches01:
            _sum_ = match01.symbol_table.get("_sum_")[0]
            if not matches02:
                break
            lineno_01 = match01.match_lineno
            for match02 in matches02:
                lineno_02 = match02.match_lineno
                new_matching = match01.new_merged_map(match02)
                valid = len(new_matching.conflict_keys) == 0
                if not valid:
                    continue
                if lineno_02 > lineno_01:
                    matches02 = False
                    break
        if not matches02:
            explain('The addition on the first iteration step is not correct because either the variable '
                    '<code>{0!s}</code> has not been initialized to an appropriate initial value or it has not been'
                    ' placed in an appropriate location<br><br><i>(miss_zero_init)<i></br>'.format(_sum_.id))
            return True
    return False


def wrong_printing_list():
    match = find_match("for ___ in ___:\n"
                       "    print(___)")
    if match:
        explain('You should be printing a single value.<br><br><i>(list_print)<i></br>')
        return True
    return False


# TODO: This might be reason to rethink letting instructor symbols map to multiple items
def missing_average():
    matches_missing = find_matches("for ___ in ___:\n"
                                   "    pass\n"
                                   "_average_ = _total_/_count_")
    matches = []
    if matches_missing:
        for match in matches_missing:
            _total_ = match.symbol_table.get("_total_")[0]
            _count_ = match.symbol_table.get("_count_")[0]
            _average_ = match.symbol_table.get("_average_")[0]
            if _total_.id != _count_.id != _average_.id and _total_.id != _average_.id:
                matches.append(match)

    if not len(matches) > 0:
        explain('An average value is not computed.<br><br><i>(no_avg)<i></br>')
        return True
    return False


def warning_average_in_iteration():
    matches = find_matches("for ___ in ___:\n"
                           "    _average_ = _total_/_count_\n")
    if matches:
        for match in matches:
            _total_ = match.symbol_table.get("_total_")[0]
            _count_ = match.symbol_table.get("_count_")[0]
            _average_ = match.symbol_table.get("_average_")[0]
            if _total_.id != _count_.id != _average_.id and _total_.id != _average_.id:
                explain('An average value is best computed after the properties name <code>{0!s}</code>(total)'
                        ' and <code>{1!s}</code> are completely known rather than recomputing the average on'
                        ' each iteration.<br><br><i>(avg_in_iter)<i></br>'.format(_total_.id, _count_.id))
                return True
    return False


def wrong_average_denominator():
    matches = find_matches("for ___ in ___:\n"
                           "    _count_ = _count_ + 1\n"
                           "_average_ = _total_/_value_")
    if matches:
        for match in matches:
            _count_ = match.symbol_table.get("_count_")[0]
            _value_ = match.symbol_table.get("_value_")[0]
            if _count_.id != _value_.id:
                explain('The average is not calculated correctly.<br><br><i>(avg_denom)<i></br>')
                return True
    return False


def wrong_average_numerator():
    matches = find_matches("for _item_ in ___:\n"
                           "    _total_ = _total_ + _item_\n"
                           "_average_ = _value_/_count_")
    if matches:
        for match in matches:
            _total_ = match.symbol_table.get("_total_")[0]
            _value_ = match.symbol_table.get("_value_")[0]
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
            _list_ = match.symbol_table.get("_list_")[0]
            __expr__ = match.exp_table.get("__expr__")
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
            _item_ = match.symbol_table.get("_item_")[0]
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
    :return:
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


# TODO: Continue converting from here
# ##########################9.2 START############################
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
            _item_ = match.symbol_table.get("_item_")[0]
            if _item_.id != "rainfall_count":
                explain(
                    'The adding of another day with rainfall to the total count of days with rainfall '
                    '(<code>rainfall_count</code>) is not correct.<br><br><i>(accu_9.2)<i></br>')
                return True
    return False


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


# TODO: Implement Numeric Logic Check!
def wrong_iteration_body_9_2():
    std_ast = parse_program()
    loops = std_ast.find_all('For')
    correct_if = False
    for loop in loops:
        if_blocks = loop.find_all('If')
        for if_block in if_blocks:
            test = if_block.test
            if test.numeric_logic_check(1, 'var > 0'):
                correct_if = True
                break
        if correct_if:
            break
    if not correct_if:
        explain('The test (if) to determine if a given amount of rainfall is greater than (>) zero is not in the '
                'correct place.<br><br><i>(iter_body_9.2)<i></br>')
    return not correct_if


def wrong_decision_body_9_2():
    std_ast = parse_program()
    if_blocks = std_ast.find_all('If')
    assignment_in_if = False
    for if_block in if_blocks:
        test = if_block.test
        if test.numeric_logic_check(1, 'var > 0'):
            assignments = if_block.find_all('Assign')
            for assignment in assignments:
                if assignment.target.id == 'rainfall_count':
                    if assignment.value.ast_name == 'BinOp':
                        binop = assignment.value
                        if binop.has(1) and binop.has(assignment.target):
                            assignment_in_if = True
                            break
        if assignment_in_if:
            break
    if not assignment_in_if:
        explain('The increase by 1 in the number of days having rainfall (<code>rainfall_count</code>) is not in the '
                'correct place.<br><br><i>(dec_body_9.2)<i></br>')


def wrong_print_9_2():
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
        explain('The output of the total number of days with rainfall is not in the correct place. The total number of '
                'days should be output only once after the total number of days has been computed.<br><br><i>'
                '(print_9.2)<i></br>')
    return wrong_print_placement
# ##########################9.2 END############################


# ##########################9.6 START############################
def wrong_comparison_9_6():
    std_ast = parse_program()
    if_blocks = std_ast.find_all('If')
    if_error = False
    for if_block in if_blocks:
        if not if_block.has(80):
            if_error = True
            break
        elif not if_block.test.numeric_logic_check(1, 'var > 80'):
            if_error = True
            break
    if if_error:
        explain('In this problem you should be finding temperatures above 80 degrees.<br><br><i>(comp_9.6)<i></br>')
    return if_error
# ##########################9.6 END############################


# ##########################10.2 START############################
def wrong_conversion_10_2():
    std_ast = parse_program()
    loops = std_ast.find_all('For')
    has_conversion = False
    conversion_var = ''
    for loop in loops:
        binops = loop.find_all('BinOp')
        iter_prop = loop.target
        conversion_var = iter_prop.id
        for binop in binops:
            if binop.has(iter_prop) and binop.has(0.04) and binop.op == 'Mult':
                conversion_var = iter_prop.id
                has_conversion = True
                break
    if conversion_var != '' and not has_conversion:
        explain('The conversion of <code>{0!s}</code> to inches is not correct.<br><br><i>'
                '(conv_10.2)<i></br>'.format(conversion_var))
# ##########################10.2 END############################


# ##########################10.3 START############################
def wrong_filter_condition_10_3():
    std_ast = parse_program()
    loops = std_ast.find_all('For')
    correct_if = False
    for loop in loops:
        if_blocks = loop.find_all('If')
        for if_block in if_blocks:
            test = if_block.test
            if test.numeric_logic_check(1, 'var > 0') or test.numeric_logic_check(1, 'var != 0'):
                correct_if = True
                break
    if not correct_if:
        explain('The condition used to filter the year when artists died is not correct.<br><br><i>(filt_10.3)<i></br>')
    return not correct_if
# ##########################10.3 END############################


# ##########################10.4 START############################
def wrong_and_filter_condition_10_4():
    std_ast = parse_program()
    loops = std_ast.find_all('For')
    correct_if = False
    for loop in loops:
        if_blocks = loop.find_all('If')
        for if_block in if_blocks:
            test = if_block.test
            if test.numeric_logic_check(1, '32 <= temp && temp <= 50'):
                correct_if = True
                break
    if not correct_if:
        explain('The condition used to filter the temperatures into the specified range of temperatures is not correct.'
                '<br><br><i>(filt_and_10.4)<i></br>')
    return not correct_if


def wrong_nested_filter_condition_10_4():
    std_ast = parse_program()
    loops = std_ast.find_all('For')
    correct_if = False
    for loop in loops:
        if_blocks = loop.find_all('If')
        for if_block in if_blocks:
            test1 = if_block.test
            if_blocks2 = if_block.find_all('If')
            for if_block2 in if_blocks2:
                test2 = if_block2.test
                if test1.numeric_logic_check(1, '32 <= temp') and test2.numeric_logic_check(1, 'temp <= 50'):
                    correct_if = True
                    break
                elif test2.numeric_logic_check(1, '32 <= temp') and test1.numeric_logic_check(1, 'temp <= 50'):
                    correct_if = True
                    break
    if not correct_if:
        explain('The decisions used to filter the temperatures into the specified range of temperatures is not correct.'
                '<br><br><i>(nest_filt_10.4)<i></br>')
    return not correct_if
# ##########################10.4 END############################


# ########################10.5 START###############################
def wrong_conversion_problem_10_5():
    std_ast = parse_program()
    loops = std_ast.find_all('For')
    is_wrong_conversion = False
    for loop in loops:
        iter_prop = loop.target
        binops = loop.find_all('BinOp')
        for binop in binops:
            if not (binop.op == 'Mult' and binop.has(iter_prop) and binop.has(0.62)):
                is_wrong_conversion = True
                break
        if is_wrong_conversion:
            break
    if is_wrong_conversion:
        log('wrong_conversion_problem_10_5')
        explain('The conversion from kilometers to miles is not correct.<br><br><i>(conv_10.5)<i></br>')


def wrong_filter_problem_atl1_10_5():
    std_ast = parse_program()
    loops = std_ast.find_all('For')
    # correct_filter = False
    for loop in loops:
        iter_prop = loop.target
        if_blocks = loop.find_all('If')
        for if_block in if_blocks:
            cond = if_block.test
            append_list = append_api.find_append_in(if_block)
            for append in append_list:
                expr = append.args[0]
                # this check seems unnecessary
                if expr.ast_name == 'BinOp' and expr.op == 'Mult' and expr.has(0.62) and expr.has(iter_prop):
                    if not cond.numeric_logic_check(0.1, 'var * 0.62 > 10'):
                        log('wrong_filter_problem_atl1_10_5')
                        explain('You are not correctly filtering out values from the list.<br><br><i>'
                                '(filt_alt1_10.5)<i></br>')


def wrong_filter_problem_atl2_10_5():
    std_ast = parse_program()
    loops = std_ast.find_all('For')
    # correct_filter = False
    for loop in loops:
        iter_prop = loop.target
        assignments = loop.find_all('Assign')
        if_blocks = loop.find_all('If')
        for assignment in assignments:
            for if_block in if_blocks:
                if if_block.lineno > assignment.lineno:
                    miles = assignment.target
                    expr = assignment.value
                    cond = if_block.test
                    append_list = append_api.find_append_in(if_block)
                    for append in append_list:
                        if append.has(miles):
                            if expr.ast_name == 'BinOp' and expr.op == 'Mult' and\
                                    expr.has(0.62) and expr.has(iter_prop):
                                if not cond.numeric_logic_check(0.1, 'var > 10'):
                                    explain('You are not correctly filtering out values from the list.<br><br><i>(filt_'
                                            'alt2_10.5)<i></br>')


def wrong_append_problem_atl1_10_5():
    std_ast = parse_program()
    loops = std_ast.find_all('For')
    # correct_filter = False
    for loop in loops:
        iter_prop = loop.target
        if_blocks = loop.find_all('If')
        for if_block in if_blocks:
            cond = if_block.test
            append_list = append_api.find_append_in(if_block)
            for append in append_list:
                expr = append.args[0]
                # this is an approximation of what's written in the code because we don't have tree matching
                cond_binops = cond.find_all('BinOp')
                if len(cond_binops) == 1:
                    if not (expr.ast_name == 'BinOp' and expr.op == 'Mult' and
                            expr.has(0.62) and expr.has(iter_prop)):
                        # if not cond.numeric_logic_check(0.1, 'var * 0.62 > 10'):  # in theory should check this
                        explain('You are not appending the correct values.<br><br><i>(app_alt1_10.5)<i></br>')


def wrong_append_problem_atl2_10_5():
    std_ast = parse_program()
    loops = std_ast.find_all('For')
    # correct_filter = False
    for loop in loops:
        iter_prop = loop.target
        assignments = loop.find_all('Assign')
        if_blocks = loop.find_all('If')
        for assignment in assignments:
            for if_block in if_blocks:
                if if_block.lineno > assignment.lineno:
                    miles = assignment.target
                    expr = assignment.value
                    cond = if_block.test
                    append_list = append_api.find_append_in(if_block)
                    for append in append_list:
                        append_var = append.args[0]
                        if expr.ast_name == 'BinOp' and expr.op == 'Mult' and\
                                expr.has(0.62) and expr.has(iter_prop):
                            if cond.numeric_logic_check(0.1, 'var > 10'):
                                if append_var.ast_name == 'Name' and append_var.id != miles.id:
                                    explain('You are not appending the correct values<br><br><i>'
                                            '(app_alt2_10.5)<i></br>')


# ########################10.5 END###############################
def wrong_debug_10_6():
    std_ast = parse_program()
    # cheating because using length of 1
    loops = std_ast.find_all('For')
    bad_change = False
    if len(loops) != 1:
        bad_change = True
    else:
        append_calls = append_api.find_append_in(loops[0])
        if len(append_calls) is not None:
            bad_change = True
    if not bad_change:
        # item = loops[0].target
        list1 = loops[0].iter
        list2 = append_calls[0].func.value.id
        if list1.id != 'quakes' or list2.id != 'quakes_in_miles':
            bad_change = True
    if bad_change:
        explain('This is not one of the two changes needed. Undo the change and try again.<br><br><i>'
                '(debug_10.6)<i></br>')


def wrong_debug_10_7():
    std_ast = parse_program()
    if_blocks = std_ast.find_all('If')
    if len(if_blocks) > 1 or if_blocks[0].test.left.id != 'book':
        explain('This is not the change needed. Undo the change and try again.<br><br><i>(debug_10.7)<i></br>')


# ########################.....###############################
def wrong_initialization_in_iteration():
    std_ast = parse_program()
    loops = std_ast.find_all('For')
    init_in_loop = False
    target = None
    for loop in loops:
        assignments = loop.find_all('Assign')
        for assignment in assignments:
            target = assignment.target
            value = assignment.value
            names = value.find_all('Name')
            if len(names) == 0:
                init_in_loop = True
                break
        if init_in_loop:
            break
    if init_in_loop:
        explain('You only need to initialize <code>{0!s}</code> once. Remember that statements in an iteration block '
                'happens multiple times'.format(target.id))


def wrong_duplicate_var_in_add():
    std_ast = parse_program()
    binops = std_ast.find_all('BinOp')
    for binop in binops:
        left = binop.left
        right = binop.right
        if left.ast_name == 'Name' and right.ast_name == 'Name':
            if left.id == right.id:
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
    x_labels = len(find_function_calls('xlabel'))
    y_labels = len(find_function_calls('ylabel'))
    titles = len(find_function_calls('title'))
    if x_labels < 1 or y_labels < 1 or titles < 1:
        explain('Make sure you supply labels to all your axes and provide a title<br><br><i>(labels_present)<i></br>')
        return False
    return True
