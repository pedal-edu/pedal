"""
Unifying collection of all the commands in ``pedal.assertions``.
"""
from pedal.core.scoring import Score, combine_scores
from pedal.sandbox.commands import call
from pedal.assertions.static import *
from pedal.assertions.runtime import *


def unit_test(function, *tests, else_message=None, score=None, partial_credit=False, **kwargs):
    """
    Helper function for quickly unit testing.

    * Specify exact score for each test case, individually | list[str]
    * Specify exact score for each test case, with single value | str
    * Specify total score for all test cases, no partial credit | False, using `score`
    * Specify total score for all test cases, divide by # of cases passed | True, using `score`

    Args:
        function ():
        *tests ():
        else_message (str): The message to present as a positive if the
             tests all pass.
        score (str): The score to give overall/per test case, depending on
            partial_credit.
        partial_credit (bool or str or list[str]): Whether or not to give credit for
            each unit test as a percentage of the whole (True), or to only give
            points for passing all the tests (False). Defaults to False.
            If a list is passed, those scores will be used per test case.
        **kwargs ():

    Returns:

    """
    if isinstance(partial_credit, bool):
        if partial_credit:
            # Specify total score for all test cases, divide by # of cases passed | True, using `score`
            if score:
                each_score = [str(Score.parse(score) / len(tests)) for test in tests]
            else:
                each_score = [None for test in tests]
        else:
            # Specify total score for all test cases, no partial credit | False, using `score`
            each_score = [None for test in tests]
    elif isinstance(partial_credit, (int, str, float)):
        # Specify exact score for each test case, with single value | str
        each_score = [partial_credit for test in tests]
    else:
        # Specify exact score for each test case, individually | list[str]
        each_score = partial_credit
    with assert_group(function, else_message=else_message, **kwargs) as group_result:
        for test_index, test in enumerate(tests):
            args, expected = test
            assert_equal(call(function, *args), expected, score=each_score[test_index], **kwargs)
    if partial_credit is False:
        group_result.score = score
    else:
        group_result.valence = group_result.POSITIVE_VALENCE
        group_result.score = combine_scores([success.score for success in group_result.successes],
                                            [failure.score for failure in group_result.failures] +
                                            [error.score for error in group_result.errors])
    return not group_result
