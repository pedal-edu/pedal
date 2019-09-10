from pedal.cait.cait_api import find_match, find_matches
from pedal.report.imperative import gently_r, explain_r


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
    message = ("The arrangement of decision and iteration is not correct for the filter pattern. "
               "You need to evaluate the decision for each element of the list.")
    code = "missing_if_in_for"
    tldr = "Missing if In For"
    matches = find_matches("for _item_ in ___:\n"
                           "    if __expr__:\n"
                           "        pass")
    if not matches:
        return explain_r(message, code, label=tldr)
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
    message = "Only items satisfying some condition should be appended to the list."
    code = "app_not_in_if"
    tldr = "Append not in if"
    match = find_match("if ___:\n"
                       "    ___.append(___)")
    if not match:
        return explain_r(message, code, label=tldr)
    return False
