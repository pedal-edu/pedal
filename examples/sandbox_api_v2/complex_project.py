'''
Instructor control script for Project 5- Text Adventure Beta

@author: acbart
@requires: pedal
@title: Project 5- Text Adventure- Control Script
@version: 4/4/2019 10:29am
'''
__version__ = 1

from pedal.assertions.organizers import phase, postcondition, precondition
from pedal.assertions.setup import resolve_all
from pedal.assertions.runtime import *
from pedal.assertions.static import *
from pedal.sandbox.commands import evaluate, call, run
from pedal.toolkit.functions import *
from pedal.sandbox.mocked import disabled_builtin, MockPedal, BlockedModule
from pedal.cait import parse_program
from cisc108.assertions import _validate_type
import os
import sys

# Start with some sanity checks

student = run()

assert_ran()
ensure_import('cisc108')

# Is there a World record? Is it a dictionary?
# Is there an INTRODUCTION? Is it a string?
# All functions defined? Documented? Covered?

# make_world() -> dict
# describe(world) -> str
# get_options(world) -> list[str]
# update(world, command) -> str
# describe_ending(world) -> str
# choose(list[str]) -> str

# WIN_PATH
# LOSE_PATH
# Can we play through the given paths and win/lose/quit them?

FUNCTION_VALUE = 2

def assertType(data, name, score=None, message=None, report=MAIN_REPORT,
                contextualize=True):
    _setup_assertions(report)
    WorldType = student.data[name]
    reason = _validate_type(data._actual_value, WorldType, "The value")
    if reason == None:
        report.give_partial(score)
        return True
    context = _build_context([data], "was", "to be a {}.\n".format(name), False)
    failure = AssertionException("{}".format(data._actual_value))
    report['assertions']['collected'].append(failure)
    context = context.format(data._actual_value, WorldType)
    report.attach('Instructor Test', category='student', tool='Assertions',
                  mistake={'message': "Student code failed instructor test.<br>\n" +
                                      context + reason})
    return False

with phase("records", score=1/10):
    assert_has_variable(student, "World")
    # I expected the variable "World" to be a dict
    assert_is_instance(student['World'], dict)

with phase("introduction", score=1/10):
    assert_has_variable(student, "INTRODUCTION")
    assert_is_instance(student['INTRODUCTION'], str)
    assert_true(student['INTRODUCTION'])

with phase("make_world", before="make_world_components"):
    ensure_signature('make_world', 0, returns='World')
    assert_has_function(student, 'make_world')
    call('make_world', target='initial_world')
    assert_is_instance(student["initial_world"], student["World"])

with phase("make_world_components", after="win_and_lose_paths"):
    student.start_grouping_context()
    call('make_world', target="initial_world")
    assert_in("status", student['initial_world'])
    assert_equal(evaluate("initial_world['status']", target='status'),
                 'playing')
    student.stop_grouping_context()

with phase("make_world_components", after="win_and_lose_paths"):
    initial_world = student.call('make_world', target='world')

@phase("make_world_components", after="win_and_lose_paths")
def grade_make_world_map():
    initial_world = student.call('make_world', target='world')
    # Map
    assertIn('locations', initial_world)
    assertIsInstance(initial_world['locations'], dict)
    x = initial_world['locations'].keys()
    assertGreaterEqual(initial_world['locations'], 1,
                  message="I expected there to be more than one location in your world.")
    # Confirm locations
    for name, location in initial_world['locations'].items():
        assertIsInstance(name, str)
        assertIsInstance(location, dict)
        # Neighbors
        assertIn('neighbors', location)
        assertIsInstance(location['neighbors'], list)
        # About
        assertIn('about', location)
        assertIsInstance(location['about'], str)
        # Stuff
        assertIn('stuff', location)
        assertIsInstance(location['stuff'], list)

@phase("make_world_components", after="win_and_lose_paths")
def grade_make_world_player():
    initial_world = student.call('make_world')
    # Player
    assertIn('you', initial_world)
    assertType(initial_world['you'], 'Player')
    # Location
    assertIn('at', initial_world['you'])
    assertIsInstance(initial_world['you']['at'], str)
    # Inventory
    assertIn('inventory', initial_world['you'])
    assertIsInstance(initial_world['you']['inventory'], list)

@phase("make_world_done", after='make_world')
def grade_make_world_finished():
    give_partial(FUNCTION_VALUE)

@phase("describe", after='make_world_done')
def grade_describe():
    assertGenerally(match_signature('describe', 1))
    assertHasFunction(student, 'describe', args=['World'], returns='str')
    initial_world = student.call('make_world', target='world')
    message = student.call('describe', initial_world._actual_value, keep_context=True,
                           target='message', context='message = describe(world)')
    assertIsInstance(message, str)
    give_partial(FUNCTION_VALUE)

@phase("get_choices", after='make_world_done')
def grade_get_choices():
    assertGenerally(match_signature('get_choices', 1))
    assertHasFunction(student, 'get_choices', args=['World'], returns='list[str]')
    initial_world = student.call('make_world', target='world')
    options = student.call('get_choices', initial_world._actual_value, keep_context=True,
                           target='commands', context='commands = get_choices(world)')
    assertIsInstance(options, list)
    assertGreater(options, 0,
                  message="I expected there to be more than one command.")
    assertIsInstance(options[0], str)
    assertIn('Quit', options)
    give_partial(FUNCTION_VALUE)

@phase("choose", after='get_choices')
def grade_choose():
    assertGenerally(match_signature('choose', 1))
    assertHasFunction(student, 'choose', args=['list[str]'], returns='str')
    assertEqual(student.call('choose', ['Quit', 'Run', 'Fight'],
                             inputs=['Walk', 'Skip', 'Fight']),
                'Fight')
    assertEqual(student.call('choose', ['Quit', 'Run', 'Fight'],
                             inputs=['Quit']),
                'Quit')
    assertEqual(student.call('choose', ['Open', 'Close', 'Sleep'],
                             inputs=['Walk', 'Walk', 'Sleep']),
                'Sleep')
    give_partial(FUNCTION_VALUE)

@phase("update", after='get_choices')
def grade_update():
    assertGenerally(match_signature('update', 2))
    assertHasFunction(student, 'update', args=['World', 'str'], returns='str')
    initial_world = student.call('make_world', target='world')
    options = student.call('get_choices', initial_world._actual_value, keep_context=True,
                           target='commands', context='commands = get_choices(world)')
    message = student.call('update', initial_world._actual_value, options._actual_value[0], keep_context=True,
                           target='message', context='message = update(world, commands[0])')
    assertIsInstance(message, str)
    give_partial(FUNCTION_VALUE)

@phase("describe_ending", after='update')
def grade_describe_ending():
    assertGenerally(match_signature('describe_ending', 1))
    assertHasFunction(student, 'describe_ending', args=['World'], returns='str')
    initial_world = student.call('make_world', target='world')
    message = student.call('update', initial_world._actual_value, 'Quit', keep_context=True,
                           target='message', context='message = update(world, "Quit")')
    message = student.call('describe_ending', initial_world._actual_value, keep_context=True,
                           target='message', context='message = describe_ending(world)')
    assertIsInstance(message, str)
    give_partial(FUNCTION_VALUE)

def test_path(path, outcome, path_name):
    world = student.call('make_world', target='world', keep_context=True)
    for command in path:
        assertIn('status', world)
        assertEqual(world['status'], 'playing')
        assertIsInstance(command, str)
        message = student.call('describe', world._actual_value, keep_context=True,
                           target='message', context='message = describe(world)')
        assertIsInstance(message, str)
        options = student.call('get_choices', world._actual_value, keep_context=True,
                           target='commands', context='commands = get_choices(world)')
        assertIsInstance(options, list)
        assertIn(command, options)
        message = student.call('update', world._actual_value, command, keep_context=True,
                           target='message', context='message = update(world, {})'.format(repr(command)))
        assertIsInstance(message, str)
    assertEqual(world['status'].value, outcome,
        message="I tried your {path_name} path, but your world's status ended as '{outcome}' instead of '{expected}'.".format(path_name=path_name, outcome=world['status'].value, expected=outcome))

@phase("win_and_lose_paths", after=['make_world', 'get_choices',
                                    'describe', 'choose', 'update',
                                    'describe_ending'])
def grade_win_and_lose_paths():
    assertHas(student, "WIN_PATH", types=list)
    assertHas(student, "LOSE_PATH", types=list)
    student.run("# I am going to try your WIN_PATH", context=None)
    test_path(student.data['WIN_PATH'], 'winning', 'WIN_PATH')
    student.run("# I am going to try your LOSE_PATH", context=None)
    test_path(student.data['LOSE_PATH'], 'losing', 'LOSE_PATH')
    compliment("I was able to play your game!")
    give_partial(FUNCTION_VALUE*2)


@phase('conclusion', after='make_world_components')
def finish_grading():
    # 2
    assertGenerally(all_documented(), score=5)

if sanity:
    resolve_all(set_success=True)
