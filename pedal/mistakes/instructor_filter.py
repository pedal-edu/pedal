from pedal.cait.cait_api import find_match, find_matches
from pedal.report.imperative import explain


def filter_group():
    missing_if_in_for()
    append_not_in_if()


def missing_if_in_for():
    """
    Name: missing_if_in_for
    Pattern:
    missing
    for <item> in ___ :
        if ...<item> ... :

    Feedback: The arrangement of decision and iteration is not correct for the filter pattern.
    Returns:

    """
    matches = find_matches("for _item_ in ___:\n"
                           "    if __expr__:\n"
                           "        pass")
    if not matches:
        explain("The arrangement of decision and iteration is not correct for the filter pattern.<br><br><i>"
                "(missing_if_in_for)<i></br></br>")
        return True
    return False


def append_not_in_if():
    """
    Name: append_not_in_if
    Pattern:
    missing
    if ... :
       ___.append(___)

    Feedback: Only items satisfying some condition should be appended to the list.

    Returns:
    """
    match = find_match("if ___:\n"
                       "    ___.append(___)")
    if not match:
        explain(
            "Only items satisfying some condition should be appended to the list.<br><br><i>(app_not_in_if)<i></br>")
        return True
    return False
