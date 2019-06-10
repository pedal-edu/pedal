from pedal.report.imperative import gently_r
from pedal.toolkit.utilities import find_function_calls, is_top_level


def ensure_prints(count):
    prints = find_function_calls('print')
    if not prints:
        gently_r("You are not using the print function!", "no_print", label="Missing Print")
        return False
    elif len(prints) > count:
        gently_r("You are printing too many times!", "multiple_print", label="Too Many Prints")
        return False
    elif len(prints) < count:
        gently_r("You are not printing enough things!", "too_few_print", label="Too Few Prints")
        return False
    else:
        for a_print in prints:
            if not is_top_level(a_print):
                gently_r("You have a print function that is not at the top level. That is incorrect for this problem!",
                         "not_top_level_print", label="Non-Top Level Print")
                return False
    return prints
