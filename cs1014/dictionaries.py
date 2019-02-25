from pedal.mistakes.feedback_mod import *
from pedal.cait.cait_api import *
from pedal.mistakes.instructor_append import app_assign


# dict_acc_group
def dict_acc_group(all_keys, unused_keys, used_keys):
    print_dict_key(all_keys)
    var_instead_of_key(all_keys)
    parens_in_dict(all_keys)
    missing_key(used_keys)
    str_list(all_keys)
    dict_parens_brack()
    comma_dict_acc()
    var_key(all_keys)
    miss_dict_acc()
    comp_in_dict_acc()
    key_comp(all_keys)
    col_dict()
    wrong_keys(unused_keys)


# dict_list_group
def dict_list_group(all_keys):
    list_str_dict(all_keys)
    list_var_dict_acc()
    list_str_as_list_var(all_keys)
    fetch_acc_dict(all_keys)
    list_as_dict()
    iter_as_key(all_keys)
    iter_prop_dict_acc()

    append_and_sum()

    dict_out_of_loop(all_keys)
    dict_access_not_in_loop()
    no_dict_in_loop()
    app_assign()


# dict_decision
def dict_decision_group(all_keys, c_value, num_slices):
    func_filter(all_keys)
    filt_key(c_value, num_slices)
    compare_key(c_value)
    str_equality()
    fetch_acc_dict([c_value])


# dict_plot
def dict_plot_group():
    show_args()
    dict_plot()


# dict_chain
def dict_chain_group(key_sets):
    for key_set in key_sets:
        key_order(key_set)
        key_order_unchained(key_set)


# dict_hard_codes
def dict_hard_codes_group(print_vals, list_vals):
    hard_coding(print_vals)
    hard_coded_list(list_vals)


# dict_hard_codes
def hard_coding(val_list):
    message = ("Please show code that makes the computer extract "
               "the value from the dictionary.")
    code = "hard_code"
    tldr = "Printing raw value"
    # Pattern 1 possibility
    matches = find_matches("print(__exp__)")
    for match in matches:
        __exp__ = match["__exp__"]
        value = __exp__.value
        if value in val_list:
            return explain_r(message, code, tldr)

    # Pattern 2 possibility
    matches = find_matches("__exp__\n"
                           "print(_var_)")
    for match in matches:
        __exp__ = match["__exp__"]
        _var_ = match["_var_"]
        submatches = __exp__.find_matches("{} = __exp2__".format(_var_.id))
        for submatch in submatches:
            __exp2__ = submatch["__exp2__"]
            value = __exp2__.value
            if value in val_list:
                return explain_r(message, code, tldr)
    return False


# dict_acc_group
def print_dict_key(keys):
    message = ('You\'ve printed the dictionary key <code>"{}"</code> instead of using an extracted value and '
               'printing it. Use the Dictionary access syntax to print the value associated with a key')
    code = "dict_k_print"
    tldr = "Printing key, not value"
    matches = find_matches("print(__str__)")
    matches += find_matches("print([__str__])")

    for match in matches:
        __str__ = match["__str__"]
        if __str__.is_ast("Str") and __str__.value in keys:
            return explain_r(message.format(__str__.value), code, tldr)
    return False


# dict_acc_group
def var_instead_of_key(keys):
    message = ("It looks like you are trying to use (<code>{}</code>) as a dictionary key. "
               "Use the dictionary access syntax to get values from a dictionary")
    code = "var_as_k"
    tldr = "Using Variable instead of key"
    matches = find_matches("_var_")
    matches += find_matches("[_var_]")
    for match in matches:
        _var_ = match["_var_"]
        if _var_.id in keys:
            submatch = find_match("_dict_['{}']".format(_var_.id))
            if submatch is None:
                return explain_r(message.format(_var_.id), code, tldr)
    return False


# dict_acc_group
def parens_in_dict(keys):
    message = ('It seems like you are having trouble with dictionary syntax. The dictionary key <code>"{}"'
               "</code>should use brackets.")
    code = "par_dict"
    tldr = "Not Using Dictionary Brackets"
    matches = find_matches("_var_(__str__)")
    for match in matches:
        __str__ = match['__str__']
        if __str__.is_ast("Str") and __str__.value in keys:
            return explain_r(message.format(__str__.value), code, tldr)
    return False


# dict_list_group
def list_as_dict():
    message = ("A list of Dictionaries like <code>{}</code> is not itself a dictionary. "
               "To access key-value pairs of the dictionaries in the list, "
               "you need to access each dictionary in the list one at a time.")
    code = "list_dict"
    tldr = "List is not a dictionary"
    matches = find_matches("_list_[__exp__]")
    for match in matches:
        _list_ = match['_list_']
        if _list_.was_type("ListType") and str(_list_.get_data_state().type.subtype) == "DictType":
            return explain_r(message.format(_list_.id), code, tldr)
    return False


# dict_list_group
def dict_out_of_loop(keys):
    message = ("Remember that a list of dictionaries, like <code>{}</code>, "
               "is still a list of individual items. Each dictionary needs to be accessed with "
               "the appropriate key-value pair one at a time.")
    code = "dict_out_loop"
    tldr = "Dictionary Access Outside of Loop"
    matches = find_matches("__exp__\n"
                           "for ___ in _var_:\n"
                           "    pass")
    matches += find_matches("for ___ in _var_:\n"
                            "    pass\n"
                            "__exp__\n")
    for match in matches:
        __exp__ = match['__exp__']
        _var_ = match['_var_']
        submatches = __exp__.find_matches("{var}[__str__]".format(var=_var_.id))
        for submatch in submatches:
            __str__ = submatch['__str__']
            if __str__.is_ast("Str") and __str__.value in keys:
                return explain_r(message.format(_var_.id), code, tldr)
    return False


# dict_acc_group
def wrong_keys(unused_keys):
    message = 'This problem does not require the key <code>"{}"</code>.\n'
    code = "unused_key"
    tldr = "Unnecessary Key Usage"

    matches = find_matches("_var_[__str__]")
    for match in matches:
        __str__ = match["__str__"]
        if __str__.is_ast("Str") and __str__.value in unused_keys:
            return explain_r(message.format(__str__.value), code, tldr)
    return False


# dict_list_group
def dict_access_not_in_loop():
    message = ("You haven't used the dictionary access syntax in a for loop. "
               "Remember that a list of dictionaries is still a list of individual items. "
               "Each dictionary needs to be accessed with the appropriate key-value pair one at a time.")
    code = "dict_acc_loop"
    tldr = "Dictionary access not in loop"

    matches = find_matches("for ___ in ___:\n"
                           "    __exp__")
    for match in matches:
        submatches = match["__exp__"].find_matches("_var_[__str__]")
        if not submatches:
            return explain_r(message, code, tldr)
    return False


def hard_coded_list(val_list):
    message = ("In later abstractions, it's not possible to view the values of a specific key in a list."
               "You should use a dictionary key-value pair to access values in the list of dictionaries.")
    code = "hard_list"
    tldr = "Don't use raw list"
    matches = find_matches("[__exp__]")
    for match in matches:
        __exp__ = match['__exp__'].parent
        if __exp__.ast_name == "List":
            try:
                vals = sum([x.value for x in __exp__.elts])
                if sum(val_list) == vals:
                    return explain_r(message, code, tldr)
            except TypeError:
                pass  # This should be the only error
    return False


# dict_list_group
def iter_as_key(keys):
    message = ("It looks like you are using the iteration variable <code>{}"
               "</code> to access a value of a specific key in a dictionary. "
               "To access a key-value from a list of dictionaries, use <code>")
    code = "iter_key"
    tldr = "Iteration variable is not key"
    matches = find_matches("for _var_ in ___:\n"
                           "    pass")
    for match in matches:
        _var_ = match['_var_']
        submatches = find_matches("_var2_[__str__]")
        missing = True
        for submatch in submatches:
            __str__ = submatch["__str__"]
            if __str__.is_ast("Str") and __str__.value == _var_.id:
                missing = False
                break
        if missing and _var_.id in keys:
            return explain_r(message.format(_var_.id), code, tldr)
    return False


# dict_list_group
def list_str_as_list_var(keys):
    message = ("The list variable in an iteration can only take lists. "
               "To grab individual values in a list of dictionaries, "
               "you need to use the appropriate key for each dictionary.")
    code = "list_var_dict"
    tldr = "List variable cannot filter"
    matches = find_matches("for ___ in [__str__]:\n"
                           "    pass")
    for match in matches:
        __str__ = match["__str__"]
        if __str__.is_ast("Str") and __str__.value in keys:
            return explain_r(message, code, tldr)
    return False


# dict_list_group
def append_and_sum():
    message = ("It looks like you're trying to build a list and "
               "then calculate a value. While this will get you a "
               "correct answer, you can calculate the value directly instead of first building a list.")
    code = "app_sum"
    tldr = "Unnecessary append and sum"
    matches = find_match("for ___ in ___:\n"
                         "    _var_.append()\n"
                         "for ___ in _var_:\n"
                         "    ___ = ___ + ___")
    if matches:
        return explain_r(message, code, tldr)
    return False


# dict_list_group
def iter_prop_dict_acc():
    message = ("Improper usage of iteration variable."
               "The for statement gives the iteration variable a value, "
               "in this case, a dictionary. That dictionary can only be accessed in the body of the iteration.")
    code = "iter_dict_acc"
    tldr = "Iteration variable only initializes"
    match = find_match("for _var_[__str__] in ___:\n"
                       "    pass")
    if match:
        return explain_r(message, code, tldr)
    return False


# dict_list_group
def list_str_dict(keys):
    message = ("When using dictionaries with iteration, the list cannot just be a key "
               'value like <code>"{}"</code>, it must be the list of dictionaries.')
    code = "list_str"
    tldr = "List variable is string"
    matches = find_matches("for ___ in __str__:\n"
                           "    pass")
    for match in matches:
        __str__ = match['__str__']
        if __str__.is_ast("Str") and __str__.value in keys:
            return explain_r(message.format(__str__.value), code, tldr)
    return False


# dict_acc_group
def missing_key(keys):
    message = "You seem to be missing the following dictionary keys:<ul>{}</ul>"
    code = "miss_key"
    tldr = "Missing necessary keys"
    key_list = ""
    for key in keys:
        matches = find_matches("\"{}\"".format(key))
        if not matches:
            key_list += '<li><code>"' + key + '"</code></li>'
    if key_list != "":
        return explain_r(message.format(key_list), code, tldr)
    return False


def blank_key(keys):
    message = "You seem to be missing the following dictionary keys:<ul>{}</ul>"
    code = "blank_key"
    tldr = "Missing Key"
    key_list = ""

    for key in keys:
        if not find_match("_var_['{}']".format(key)):
            key_list += '<li><code>"' + key + '"</code></li>'

    if key_list != "":
        return explain_r(message.format(key_list), code, tldr)


# dict_acc_group
def dict_parens_brack():
    message = ("It looks like you are trying to dictionary access <code>{}</code>. "
               "The dictionary access syntax does not require parenthesis.")
    code = "dict_parbrack"
    tldr = "Improper dictionary access"
    matches = find_matches("_var_([__str1__][__str2__])")
    matches += find_matches("_var_([__str1__])")
    for match in matches:
        _var_ = match['_var_']
        __str1__ = match["__str1__"]
        __str2__ = __str1__
        try:
            __str2__ = match["__str2__"]
        except KeyError:
            pass
        if __str1__.is_ast("Str") and __str2__.is_ast("Str") and data_state(_var_.id):
            return explain_r(message.format(_var_.id), code, tldr)
    return False


# dict_acc_group
def comma_dict_acc():
    message = ("It looks like you are trying to dictionary access <code>{}</code>. "
               "Unlike with initializing dictionaries, keys don't need to be separated with commas "
               "when accessing dictionary contents.")
    code = "comma_dict"
    tldr = "Improper dictionary access"
    matches = find_matches("__exp__,[__str2__]")
    for match in matches:
        submatch = match['__exp__'].find_match("_dict_[__str1__]")
        if submatch:
            return explain_r(message.format(submatch['_dict_'].id), code, tldr)
    return False


# dict_list_group
def no_dict_in_loop():
    message = "When working with a list of dictionaries, you need to use a dictionary access in your iteration."
    code = "no_dict_loop"
    tldr = "Missing dictionary access loop"

    matches = find_matches("for _item_ in _list_:\n"
                           "    __expr__")
    for match in matches:
        submatches = match['__expr__'].find_matches("_item_[__str__]")
        for submatch in submatches:
            if submatch["__str__"].is_ast("Str"):
                return False
    return explain_r(message, code, tldr)


# dict_decision
def func_filter(keys):
    message = "Please do not modify the function call to retrieve the data."
    code = "func_filt"
    tldr = "Attempting to filter using fetch"
    matches = find_matches("_var_._func_(__str__)")
    for match in matches:
        __str__ = match["__str__"]
        if __str__.value in keys:  # TODO: Relies on .value returning id for Name nodes
            return explain_r(message, code, tldr)
    return False


# dict_acc_group
def str_list(keys):
    message = ('If you are trying to use a string such as <code>"{}"</code> as a dictionary key, '
               'it needs to be prefaced with a dictionary')
    code = "str_list"
    tldr = "String list used instead of Dictionary"

    for key in keys:
        if find_match("['{}']".format(key)):
            return explain_r(message.format(key), code, tldr)
    return False


# dict_list_group
def list_var_dict_acc():
    message = ("The for statement only specifies a list target, in this case, a list of dictionaries. "
               "It does not operate on the entire list. Keys should be used on the individual dictionaries of the list.")
    code = "l_var_dacc"
    tldr = "List variable cannot be dictionary accessed"

    matches = find_matches("for ___ in _var_[__str__]:\n"
                           "    pass")
    if matches:
        return explain_r(message, code, tldr)
    return False


# dict_acc_group
def key_comp(keys):
    message = ('The strings <code>"{}"</code> and <code>"{}"</code> are keys. '
               'Dictionary keys do not need to be compared to anything as they '
               'are not filtering data. Dictionary keys are only used to access existing data.')
    code = "key_comp"
    tldr = "Comparing Keys"

    matches = find_matches("for _var_ in ___:\n"
                           "    if _var_[__str1__] == __str2__:\n"
                           "        pass")
    for match in matches:
        __str1__ = match["__str1__"]
        __str2__ = match["__str2__"]
        if __str1__.is_ast("Str") and __str1__.value in keys and __str2__.is_ast("Str") and __str2__.value in keys:
            return explain_r(message.format(__str1__.value, __str2__.value), code, tldr)
    return False


# dict_acc_group
def col_dict():
    message = "When using multiple keys, each key should have it's own set of brackets."
    code = "col_dict"
    tldr = "Improper Dictionary Access"

    matches = find_matches("_var_[__str1__: __str2__]")
    if matches:
        return explain_r(message, code, tldr)
    return False


# dict_acc_group
def var_key(keys):
    message = ("It looks like you are trying to use <code>{}</code> as a key. Dictionary keys are string values. "
               "Variable names don't have a meaning to a computer.")
    code = "var_key"
    tldr = "Variables are not keys"

    matches = find_matches("_var_[_key_]")
    for match in matches:
        _key_ = match['_key_']
        if _key_.id in keys:
            return explain_r(message.format(_key_.id), code, tldr)
    return False


# dict_plot
def key_order(keys):
    message = "It looks like you aren't using the correct keys, or the correct key order. Double check your data map."
    code = "key_order_c"
    tldr = "Worng key order"

    construct = None
    find_chain = "_var_"
    for a_slice in range(len(keys)):
        find_chain += "[__str{}__]".format(a_slice)
    if find_match(find_chain):
        construct = "_var_"
        for key in keys:
            construct += "['{}']".format(key)

    if construct:
        matches = find_matches(construct)
        if not matches:
            return explain_r(message, code, tldr)
    return False


# dict_plot
def key_order_unchained(keys):
    message = "It looks like you aren't using the correct keys, or the correct key order. Double check your data map."
    code = "key_order_u"
    tldr = "Wrong key order"

    construct = None
    find_chain = ""
    for a_slice in range(len(keys)):
        find_chain += "_var{a2}_ = _var{a1}_[__str{a1}__]\n".format(a2=a_slice+1, a1=a_slice)
    if find_match(find_chain):
        construct = ""
        count = 0
        for key in keys:
            construct += "_var{a2}_ = _var{a1}_['{key}']\n".format(a2=count+1, a1=count, key=key)
            count += 1

    if construct:
        matches = find_matches(construct)
        if not matches:
            return explain_r(message, code, tldr)
    return False


# dict_decision
def filt_key(c_value, num_slices):
    message = ('It looks like you\'re using <code>"{c_value}"</code> as a dictionary key to filter data. '
               "Dictionary keys don't filter data, they only access data that's already there. "
               "You should be comparing data retrieved from the dictionary to <code>'{c_value}'</code>")
    code = "filt_key"
    tldr = "Attempting filter as Key"

    construct = "_var_"
    for a_slice in range(num_slices):
        construct += "[__str{}__]".format(a_slice)
        matches = find_matches(construct)
        for match in matches:
            for num in range(a_slice + 1):
                value = match["__str{}__".format(num)]
                if value.is_ast("Str") and value.value == c_value:
                    return explain_r(message.format(c_value=value), code, tldr)
    return False


# dict_acc_group
def miss_dict_acc():
    message = ("You are missing something that looks like a dictionary access. "
               "In this unit, you should be using dictionary access")
    code = "miss_acc"
    tldr = "Missing Dictionary Access"

    if not find_matches("_var_[__str1__]"):
        return explain_r(message, code, tldr)
    return False


# dict_decision
def compare_key(c_value):
    message = ('In this problem, <code>"{}"</code> is not a key, '
               'but something you should compare against.'.format(c_value))
    code = "comp_key"
    tldr = "Using filter value as key"

    matches = find_matches("__exp0__ == __exp1__")
    for match in matches:
        for num in range(2):
            __exp__ = match["__exp{}__".format(num)]
            submatches = __exp__.find_matches("[__str__]")
            for submatch in submatches:
                __str__ = submatch["__str__"]
                if __str__.is_ast("Str") and __str__.value == c_value:
                    return explain_r(message, code, tldr)
    return False


# dict_decision
def str_equality():
    message = ('You are comparing two different string values, "{}" and "{}". While dictionary keys are strings, '
               "they are only interpreted by the computer as keys when used with the dictionary access syntax")
    code = "str_eq"
    tldr = "Comparing equality of raw strings"

    matches = find_matches("__str1__ == __str2__")
    for match in matches:
        __str1__ = match["__str1__"]
        __str2__ = match["__str2__"]
        if __str1__.is_ast("Str") and __str2__.is_ast("Str"):
            return explain_r(message.format(__str1__.value, __str2__.value), code, tldr)
    return False


# dict_list_group and dict_decision_group
def fetch_acc_dict(values):
    message = ("The code to fetch the list of dictionaries, <code>{}.{}</code>, cannot be used to select data. "
               "Selection of data should be done with an if statement")
    code = "fetch_acc"
    tldr = "Malformed Dictionary List Fetch"

    matches = find_matches("_var_._func_[__str__]")
    for match in matches:
        _var_ = match["_var_"].id
        _func_ = match["_func_"].id
        __str__ = match["__str__"]
        if __str__.is_ast("Str") and __str__.value in values:
            return explain_r(message.format(_var_, _func_), code, tldr)
    return False


# dict_plot
def show_args():
    # TODO: Add this to plotting mistakes?
    message = ("The <code>plt.show</code> function only tells the computer to display the plot. "
               "If you want to modify the plot, use other available plotting functions.")
    code = "show_args"
    tldr = "Show takes no arguments"

    matches = find_matches("plt.show(__exp__)")
    if matches:
        return explain_r(message, code, tldr)
    return False


# dict_plot
def dict_plot():
    message = ("The list <code>{}</code> is a list of dictionaries. <code>plt.plot</code> only accepts a list"
               " of numbers. You need to extract the numbers from the list of dictionaries first.")
    code = "dict_plot"
    tldr = "Plotting list of Dictionaries"

    matches = find_matches("plt._func_(_var_)")
    for match in matches:
        _var_ = match["_var_"]
        var_type = str(_var_.get_data_state().type)
        subtype = str(_var_.get_data_state().type.subtype)
        if var_type == "ListType" and subtype == "DictType":
            return explain_r(message.format(_var_.id), code, tldr)
    return False


# dict_acc_group
def comp_in_dict_acc():
    message = ("You are using a boolean expression in a dictionary access. Remember that the dictionary "
               "access takes a key and provides a value. The comparison should be made with the value, not the key.")
    code = "comp_acc"
    tldr = "Comparison in key access"

    matches = find_matches("_var_[__exp__][__exp2__ == __exp3__]")
    if matches:
        return explain_r(message, code, tldr)
    return False
