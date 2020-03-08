'''
Instructor control script for Project 5- Text Adventure Beta

@author: acbart
@requires: pedal
@title: Project 5- Text Adventure- Control Script
@version: 4/4/2019 10:29am
'''
__version__ = 1

from pedal.resolvers.simple import resolve
from pedal import (explain, contextualize_report, set_success, give_partial,
                   compliment)
from pedal.sandbox import run
from pedal.assertions.organizers import phase, postcondition, precondition
from pedal.assertions.setup import resolve_all, set_assertion_mode
from pedal.assertions.assertions import *
from pedal.toolkit.imports import *
from pedal.toolkit.utilities import *
from pedal.toolkit.functions import *
from pedal.toolkit.signatures import function_signature
from pedal.sandbox.mocked import disabled_builtin, MockPedal, BlockedModule
from pedal.cait import parse_program
import os
import sys

from pedal.environments import setup_pedal

set_assertion_mode(True)

ast, student, resolver = setup_pedal(skip_tifa=True)

# Start with some sanity checks

sanity = student.exception is None

assertGenerally(not ensure_imports('cisc108'))

# Is there a triple quoted top-level string that starts with Records:?
# All functions defined? Documented? Covered?

# render_introduction() -> string
# create_world() -> dict
# render(world) -> str
# get_options(world) -> list[str]
# update(world, command) -> str
# render_ending(world) -> str
# choose(list[str]) -> str

# WIN_PATH
# LOSE_PATH
# Can we play through the given paths and win/lose/quit them?

FUNCTION_VALUE = 2

@phase("records")
def grade_records():
    body = parse_program().body
    for statement in body:
        if statement.ast_name == "Expr":
            if statement.value.ast_name == "Str":
                contents = statement.value.s
                for line in contents.split("\n"):
                    if line.strip().lower().startswith("records:"):
                        give_partial(FUNCTION_VALUE)
                        return True
    explain("You have not created a Records definition at the top level.")
    return False

@phase("render_introduction")
def grade_render_introduction():
    assertGenerally(match_signature('render_introduction', 0))
    assertHasFunction(student, 'render_introduction', args=[], returns='str')
    introduction = student.call('render_introduction')
    assertIsInstance(introduction, str)
    give_partial(FUNCTION_VALUE)
    
@phase("create_world", before='create_world_components')
def grade_create_world():
    assertGenerally(match_signature('create_world', 0))
    assertHasFunction(student, 'create_world', args=[], returns='World')
    initial_world = student.call('create_world')
    assertIsInstance(initial_world, dict)
    
@phase("create_world_components", after="create_world")
def grade_create_world_status():
    initial_world = student.call('create_world')
    assertIn('status', initial_world)
    assertEqual(initial_world['status'], 'playing')

@phase("create_world_components", after="create_world")
def grade_create_world_map():
    initial_world = student.call('create_world', target='world')
    # Map
    assertIn('map', initial_world)
    assertIsInstance(initial_world['map'], dict)
    x = initial_world['map'].keys()
    assertGreaterEqual(initial_world['map'], 1,
                  message="I expected there to be more than one location in your world.")
    # Confirm locations
    for name, location in initial_world['map'].items():
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

@phase("create_world_components", after="create_world")
def grade_create_world_player():
    initial_world = student.call('create_world')
    # Player
    assertIn('player', initial_world)
    assertIsInstance(initial_world['player'], dict)
    # Location
    assertIn('location', initial_world['player'])
    assertIsInstance(initial_world['player']['location'], str)
    # Inventory
    assertIn('location', initial_world['player'])
    assertIsInstance(initial_world['player']['inventory'], list)

@phase("create_world_done", after='create_world_components')
def grade_create_world_finished():
    give_partial(FUNCTION_VALUE)
    
@phase("render", after='create_world_done')
def grade_render():
    assertGenerally(match_signature('render', 1))
    assertHasFunction(student, 'render', args=['World'], returns='str')
    initial_world = student.call('create_world', target='world')
    message = student.call('render', initial_world, keep_context=True,
                           target='message', context='message = render(world)')
    assertIsInstance(message, str)
    give_partial(FUNCTION_VALUE)

@phase("get_options", after='create_world_done')
def grade_get_options():
    assertGenerally(match_signature('get_options', 1))
    assertHasFunction(student, 'get_options', args=['World'], returns='list[str]')
    initial_world = student.call('create_world', target='world')
    options = student.call('get_options', initial_world, keep_context=True,
                           target='options', context='options = get_options(world)')
    assertIsInstance(options, list)
    assertGreater(options, 0,
                  message="I expected there to be more than one option.")
    assertIsInstance(options[0], str)
    assertIn('Quit', options)
    give_partial(FUNCTION_VALUE)
    
@phase("choose", after='get_options')
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

@phase("update", after='get_options')
def grade_update():
    assertGenerally(match_signature('update', 2))
    assertHasFunction(student, 'update', args=['World', 'str'], returns='str')
    initial_world = student.call('create_world', target='world')
    options = student.call('get_options', initial_world, keep_context=True,
                           target='options', context='options = get_options(world)')
    message = student.call('update', initial_world, options[0], keep_context=True,
                           target='message', context='message = update(world, options[0])')
    assertIsInstance(message, str)
    give_partial(FUNCTION_VALUE)
    
@phase("render_ending", after='update')
def grade_render_ending():
    assertGenerally(match_signature('render_ending', 1))
    assertHasFunction(student, 'render_ending', args=['World'], returns='str')
    initial_world = student.call('create_world', target='world')
    message = student.call('update', initial_world, 'Quit', keep_context=True,
                           target='message', context='message = update(world, "Quit")')
    message = student.call('render_ending', initial_world, keep_context=True,
                           target='message', context='message = render_ending(world)')
    assertIsInstance(message, str)
    give_partial(FUNCTION_VALUE)

def test_path(path, outcome, path_name):
    world = student.call('create_world', target='world', keep_context=True)
    for command in path:
        assertIn('status', world)
        assertEqual(world['status'], 'playing')
        assertIsInstance(command, str)
        message = student.call('render', world, keep_context=True,
                           target='message', context='message = render(world)')
        assertIsInstance(message, str)
        options = student.call('get_options', world, keep_context=True,
                           target='options', context='options = get_options(world)')
        assertIsInstance(options, list)
        assertIn(command, options)
        message = student.call('update', world, command, keep_context=True,
                           target='message', context='message = update(world, {})'.format(command))
        assertIsInstance(message, str)
    assertEqual(world['status'].value, outcome,
        message="I tried your {path_name} path, but your world's status ended as '{outcome}' instead of '{expected}'.".format(path_name=path_name, outcome=world['status'].value, expected=outcome))

@phase("win_and_lose_paths", after=['create_world', 'get_options',
                                    'render', 'choose', 'update',
                                    'render_ending', 'render_introduction'])
def grade_win_and_lose_paths():
    assertHas(student, "WIN_PATH", types=list)
    assertHas(student, "LOSE_PATH", types=list)
    student.call('render_introduction')
    student.run("# I am going to try your WIN_PATH", context=None)
    test_path(student.data['WIN_PATH'], 'won', 'WIN_PATH')
    student.call('render_introduction')
    student.run("# I am going to try your LOSE_PATH", context=None)
    test_path(student.data['LOSE_PATH'], 'lost', 'LOSE_PATH')
    compliment("I was able to play your game!")
    give_partial(FUNCTION_VALUE*2)
    

@phase('conclusion', after='win_and_lose_paths')
def finish_grading():
    # 2
    assertGenerally(all_documented(), score=5)

if sanity:
    resolve_all(set_successful=True)

resolver()
