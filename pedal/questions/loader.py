"""
instructions: blah blah blah

settings:
    tifa:
        enabled: True
    unit testing:
        by function (bool): Whether to test each function entirely before moving onto the
            next one, or to first check that all functions have been defined, and then
            checking their parameters, etc. Defaults to True.
global:
    variables:
        name:
        type:
        value:
    inputs:
    prints:
functions:
    function: do_complicated_stuff
    signature: int, int -> float
    cases:
      - arguments: 5, 4
        inputs:
        returns: 27.3
        prints:
syntax:
    prevent:
        ___ + ___





        signature: int, int, list[int], (int->str), dict[str:list[int]] -> list[int]
"""

from pedal.toolkit.printing import *
from pedal.toolkit.utilities import *
from pedal.toolkit.functions import *

EXAMPLE_DATA = {
    'functions': [{
        'function': 'do_complicated_stuff',
        'signature': 'int, int, [int] -> list[int]',
        'cases': [
            {'arguments': "5, 4, 3", 'returns': "12"},
        ]
    }]
}

def load(data):
    if 'functions' in data:
        for function in data['functions']:
            pass


def load_file(filename):
    pass