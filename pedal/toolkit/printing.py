from pedal.report.imperative import gently
from pedal.toolkit.utilities import find_function_calls, is_top_level


def ensure_prints(count):
    prints = find_function_calls('print')
    if not prints:
        gently("You are not using the print function!<br><br><i>(no_print)<i>")
        return False
    elif len(prints) > count:
        gently("You are printing too many times!<br><br><i>(multiple_print)<i>")
        return False
    elif len(prints) < count:
        gently("You are not printing enough things!<br><br><i>(too_few_print)<i>")
        return False
    else:
        for a_print in prints:
            if not is_top_level(a_print):
                gently("You have a print function that is not at the top level. That is incorrect for this problem!"
                       "<br><br><i>(not_top_level_print)<i>")
                return False
    return prints
