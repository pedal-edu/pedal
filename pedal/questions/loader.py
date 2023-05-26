"""
instructions: blah blah blah

settings:
    tifa:
        enabled: True
    unit test by function (bool): Whether to test each function entirely before moving onto the
            next one, or to first check that all functions have been defined, and then
            checking their parameters, etc. Defaults to True.
    show case details (bool): Whether to show the specific args/inputs that caused a test case
            to fail.
rubric:
    functions:
        total: 100
        definition: 10
        signature: 10
        cases: 80
global:
    variables:
        name:
        type:
        value:
    inputs:
    prints:
# Sandbox, type checking
functions:
    documentation: "any" or "google"
    coverage: 100%
    tests: int
    name: do_complicated_stuff
    arity: int
    signature: int, int -> float
    signature: int, int, list[int], (int->str), dict[str:list[int]] -> list[int]
    parameters:
        name: banana
            exactly:
            regex:
            includes:
            within:
        type: int
    cases:
      - arguments (list): 5, 4
        inputs (list):
        returns (Any):
            equals: 27.3
            is:
            is not: _1
        name (str): Meaningful name for tracking purposes? Or possibly separate into label/id/code
        hint (str): Message to display to user
        prints:
            exactly:
            regex:
            startswith:
            endswith:
        plots:
# Cait
syntax:
    prevent:
        ___ + ___
# Override any of our default feedback messages
messages:
    FUNCTION_NOT_DEFINED: "Oops you missed a function"
"""
from pedal.core.commands import set_correct, give_partial, gently
from pedal.core.feedback_category import FeedbackCategory
from pedal.questions.constants import TOOL_NAME

from pedal.sandbox.commands import get_sandbox, get_student_data
from pedal.utilities.comparisons import equality_test
from pedal.assertions.static import ensure_function
from pedal.assertions.runtime import ensure_function_callable
from pedal.assertions.commands import unit_test

SETTING_SHOW_CASE_DETAILS = "show case details"
DEFAULT_SETTINGS = {
    SETTING_SHOW_CASE_DETAILS: True
}

EXAMPLE_DATA = {
    'functions': [{
        'name': 'do_complicated_stuff',
        'signature': 'int, int, [int] -> list[int]',
        'cases': [
            {'arguments': "5, 4, 3", 'returns': "12"},
        ]
    }]
}


def load_question(data):
    """

    :param data:
    :return:
    """
    settings = DEFAULT_SETTINGS.copy()
    settings.update(data.get('settings', {}))
    rubric = settings.get('rubric', {})
    if 'functions' in data:
        function_rubric = rubric.get('functions', {})
        for function in data['functions']:
            ensure_function(function['name'], arity=function.get('arity'),
                            parameters=function.get('parameters'),
                            returns=function.get('returns'),
                            score=function_rubric.get('definition', 10))
            ensure_function_callable(function['name'])
            unit_test(function, *function.get('cases', []))

def check_question(data):
    """

    Args:
        data:
    """
    results = list(load_question(data))
    if results:
        message, label = results[0]
        gently(message, label=label)


def check_pool(questions):
    """

    Args:
        questions:
    """
    pass


def load_file(filename):
    """

    Args:
        filename:
    """
    pass
