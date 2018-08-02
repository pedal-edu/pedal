from pedal.cait.cait_api import *
from pedal.report.imperative import *


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

    :return:
    """

    std_ast = parse_program()
    loops = std_ast.find_all("For")
    for loop in loops:
        ifs = loop.find_all("If")
        if len(ifs) > 0:
            return False
    explain("The arrangement of decision and iteration is not correct for the filter pattern.<br><br><i>"
            "(missing_if_in_for)<i></br>")
    return True


def append_not_in_if():
    """
    Name: append_not_in_if
    Pattern:
    missing
    if ... :
       ___.append(___)

    Feedback: Only items satisfying some condition should be appended to the list.

    :return:
    """
    std_ast = parse_program()
    ifs = std_ast.find_all("If")
    for if_block in ifs:
        calls = if_block.find_all("Call")
        for node in calls:
            if node.func.attr == "append":
                return False
    explain("Only items satisfying some condition should be appended to the list.<br><br><i>(app_not_in_if)<i></br>")
    return True
