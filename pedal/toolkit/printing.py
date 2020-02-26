from pedal.core.commands import gently
from pedal.toolkit.utilities import find_function_calls, is_top_level


def ensure_prints(count):
    """

    Args:
        count:

    Returns:

    """
    prints = find_function_calls('print')
    if not prints:
        gently("You are not using the print function!", label="no_print", title="Missing Print")
        return False
    elif len(prints) > count:
        gently("You are printing too many times!", label="multiple_print", title="Too Many Prints")
        return False
    elif len(prints) < count:
        gently("You are not printing enough things!", label="too_few_print", title="Too Few Prints")
        return False
    else:
        for a_print in prints:
            if not is_top_level(a_print):
                gently("You have a print function that is not at the top level. That is incorrect for this problem!",
                       label="not_top_level_print", title="Non-Top Level Print")
                return False
    return prints
