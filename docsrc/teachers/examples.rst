.. _examples:

Teacher Examples
================

This document goes over some common scenarios that you might have. Or more accurately right now, it's showing off
some random examples I grabbed from our courses.

Basic Arithmetic Question
-------------------------

Instructions:

    Using the + operator, print out the result of 7+3. Do not embed the result
    in your code. Let Python do the calculation for you.

Correct answer:

.. code-block:: python
    :caption: student.py

    print(7+3)

Instructor grading code:

.. code-block:: python
    :caption: grade_assignment.py

    from pedal import *

    # Make sure they don't embed the answer
    prevent_literal(10)
    # Make sure they DO use these integers
    ensure_literal(7)
    ensure_literal(3)
    # Make sure they print
    ensure_function_call('print')
    # Make sure they used addition operator
    ensure_operation("+")
    # Give message if they try to use strings instead of numbers
    prevent_ast("Str")
    # Check the actual output
    assert_output(student, "7")


Basic Function Call Question
----------------------------

Here's a random simple example grading script for a problem where students use the `round` function to convert a
dollar amount stored as a string literal without a dollar sign, and then print the result. It's trivial, but we
do use it in one of courses.

Instructions:

    The function `round` consumes a float number and returns it rounded to
    the nearest whole number. You are buying some food and want to know
    roughly how much it will cost. Use the round function to
    round $9.50 to the nearest whole number.

Student answer:

.. code-block:: python
    :caption: student.py

    print(round(9.5))

Instructor control script:

.. code-block:: python
    :caption: grade_assignment.py

    from pedal import *

    # Common mistake is that students put a $ in their code
    if "$" in get_program():
        explain("You should not use the dollar sign ($) anywhere in your code!",
                title="Do Not Use Dollar Sign"
                priority='syntax', label="used_dollar_sign")

    # They must call the round function
    ensure_function_call('round')
    # They must call the print function
    ensure_function_call('print')
    # They must have the float value 9.5 in their code
    ensure_literal(9.5)
    # They can only have one number in their code
    prevent_ast("Num", at_most=1)
    # They cannot have any strings embedded in their code.
    prevent_ast("Str")
    # Check that the output is correct
    assert_output(student, "10")

Student Defined Function
------------------------

Instructions:

    Create a function named `add_3` that takes in three integers and returns
    their sum. Make sure you unit test the function a suitable number of times!

Student Answer:

.. code-block:: python
    :caption: student.py

    def add_3(a, b, c):
        return a+b+c

    # You might use a different unittest style!
    assert add_3(1, 2, 3) == 6
    assert add_3(0, 0, 0) == 0
    assert add_3(-1, -1, 3) == 1

Instructor Control Script:

.. code-block:: python
    :caption: grade_assignment.py

    from pedal import *

    ensure_function('add_3', arity=3)
    # Or if you teach them to annotate their parameters/returns
    # ensure_function('add_3', parameters=[int,int,int], returns=int)
    # Did they write at least three tests?
    ensure_function_call('add_3', at_least=3)
    ensure_ast("Assert", at_least=3)
    # Use coverage module to check their code coverage
    ensure_coverage(.9)
    # Actually unit test their result
    unit_test("add_3", [
        ([1, 2, 3], 6),
        ([-5, 5, 2], 2),
        ([0, 0, 0], 0),
        ([7, 3, -10], 0)
    ])


Complex Question
----------------


Here's a much more sophisicated problem where they have to read open two files and mangle their contents to
make MadLibs.

.. code-block:: python
    :caption: grade_assignment.py

    suppress("analyzer", "Iterating over non-list")
    suppress("analyzer", "Iterating over empty list")

    words_file = open("words.txt")
    story_file = open("story.txt")
    words = [w.strip() for w in words_file]
    story = [l.strip() for l in story_file]
    correct_story = []
    for line in story:
        for w in words:
            line = line.replace(w, '____')
        correct_story.append(line)
    output = get_output()

    if find_match('___.strip()') or find_match('___.replace()'):
        gently("Remember! You cannot modify a string directly. Instead, you should assign the result back to the string variable.")

    prevent_ast("If", message="You do not need any <code>if</code> statements. The <code>replace</code> method works regardless of whether the text contains the string.")

    ensure_function_call("replace")
    assert_output(student, "\n".join(correct_story))
    ensure_ast("For", at_least=2)
    prevent_ast("For", at_most=5)
    prevent_function_call("read", message="You should not use the built-in <code>read</code> method.")
    prevent_function_call("readlines", message="You should not use the built-in <code>readlines</code> method.")

    # Note how we can mute and unscore a feedback function
    # Now we can use it as a check without producing feedback!
    stripping = ensure_function_call('strip', muted=True, unscored=True)
    rstripping = ensure_function_call('rstrip', muted=True, unscored=True)
    if not stripping and not rstripping:
        gently("Make sure you are stripping the new lines before you print!")


Medium Project
--------------

The following project had students write a function to compare two string dates and determine which one
was earlier. In order to do so, they had to complete a number of helper functions along the way.

.. code-block:: python
    :caption: grade_assignment.py

    """
    Instructor control script for Project- Dates and Times

    @author: acbart
    @requires: pedal
    @title: Project- Dates and Times- Control Script
    @version: 9/6/2020 12:38pm
    """

    __version__ = 1

    from pedal import *
    from curriculum_sneks import ensure_functions_return, prevent_printing_functions
    from curriculum_sneks.tests import ensure_cisc108_tests


    prevent_import('re', message="Using Regular Expressions would be a good idea."
                                 " But no, you may not use them here.",
                   label="imported_re", title="No Regular Expressions")
    prevent_import('datetime', message="No using the built-in `datetime` module!",
                   label="imported_datetime", title="No Datetime Module")
    prevent_import('arrow', message="No using the fancy `arrow` module!",
                   label="imported_arrow", title="No Arrow Module")
    prevent_import('pandas', message="Wow, okay, no super can't use `pandas`.",
                   label="imported_pandas", title="No Pandas")
    ensure_import('cisc108')

    prevent_ast('Try', message=" I noticed you used a Try/Except block. It's great that"
                               " you found another way, but we'd appreciate it if you"
                               " used this project to practice IF statements and string"
                               " indexing.",
                label="used_try", title="Do Not Use Try/Except")

    prevent_printing_functions()
    ensure_functions_return()

    if ensure_coverage(.8, priority='lowest'):
        compliment("Good unit test coverage so far",
                   label="good_coverage_so_far")

    ensure_function('parse_date_month', parameters=[str], returns=int)
    ensure_function_call('parse_date_month', at_least=4,
                         message="Write at least 4 unit tests for `parse_date_month` please.")
    if unit_test('parse_date_month',
                  (["1/1/2020"], 1),
                  (["5/12/2020"], 5),
                  (["10/9/1998"], 10),
                  (["11/30/2010"], 11),
                  (["10/30/15"], 10),
                  (["01/2/05"], 1),
                  (["12/31/9999"], 12),
                  #(["1/32/2013"], 1),
                  (["13/32/2013"], -1),
                  (["13/1/2013"], -1),
                  (["Newark, DE"], -1),
                  (["0/0/0000"], -1),
                 ):
        compliment("Finished parse_date_month!", label="done_parse_date_month")


    ensure_function('parse_date_day', parameters=[str], returns=int)
    ensure_function_call('parse_date_day', at_least=4,
                         message="Write at least 4 unit tests for `parse_date_day` please.")
    if unit_test('parse_date_day',
                  (["1/1/2020"], 1),
                  (["5/12/2020"], 12),
                  (["10/9/1998"], 9),
                  (["11/30/2010"], 30),
                  (["10/31/15"], 31),
                  (["01/2/05"], 2),
                  (["12/31/9999"], 31),
                  (["13/32/2013"], -1),
                  (["1/32/2013"], -1),
                  (["0/0/0000"], -1),
                  ):
        compliment("Finished parse_date_day!", label="done_parse_date_day")

    ensure_function('parse_date_year', parameters=[str], returns=int)
    ensure_function_call('parse_date_year', at_least=4,
                         message="Write at least 4 unit tests for `parse_date_year` please.")
    if unit_test('parse_date_year',
                  (["1/1/2020"], 2020),
                  (["5/12/2021"], 2021),
                  (["10/9/1998"], 1998),
                  (["11/30/2010"], 2010),
                  (["10/31/15"], 2015),
                  (["01/2/05"], 2005),
                  (["12/31/9999"], 9999),
                  (["13/32/013"], -1),
                  (["1/32/3"], -1),
                  (["0/0/"], -1),
                  ):
        compliment("Finished parse_date_year!", label="done_parse_date_year")

    ensure_function('is_date', parameters=[str], returns=bool)
    ensure_function_call('is_date', at_least=4,
                         message="Write at least 4 unit tests for `is_date` please.")
    if unit_test('is_date',
                  (["1/1/2020"], True),
                  (["5/12/2020"], True),
                  (["10/9/1998"], True),
                  (["11/30/2010"], True),
                  (["10/31/15"], True),
                  (["01/2/05"], True),
                  (["12/31/9999"], True),
                  (["13/32/2013"], False),
                  (["13/2/2013"], False),
                  (["1/2/201"], False),
                  (["1/2/3"], False),
                  (["1/32/2013"], False),
                  (["0/0/0000"], False),
                  ):
        compliment("Finished is_date!", label="done_is_date")

    ensure_function('earlier', parameters=[str, str], returns=str)
    ensure_function_call('earlier', at_least=4,
                         message="Write at least 4 unit tests for `earlier` please.")
    if unit_test('earlier',
                  # Same
                  (["1/1/2020", "1/1/2020"], "equal"),
                  (["5/12/2020", "05/12/2020"], "equal"),
                  (["10/9/1998", "10/9/1998"], "equal"),
                  (["11/30/2010", "11/30/10"], "equal"),
                  # Simple cases
                  (["11/30/2010", "11/31/2010"], "11/30/2010"),
                  (["11/30/2010", "11/29/2010"], "11/29/2010"),
                  (["10/3/2020", "10/4/2020"], "10/3/2020"),
                  (["10/3/2020", "10/2/2020"], "10/2/2020"),
                  # Complex failures
                  (["10/3/2020", "10/20/2020"], "10/3/2020"),
                  (["2/2/2020", "10/10/2020"], "2/2/2020"),
                  (["10/2/2020", "10/10/2020"], "10/2/2020"),
                  (["12/1/2019", "1/1/2020"], "12/1/2019"),
                  # Errors
                  (["1/2/3", "1/32/2013"], "error"),
                  (["1/32/2013", "1/2/3000"], "error"),
                  (["1/2/3000", "1/32/2013"], "error")
                  ):
        compliment("Finished earlier!", label="done_earlier")


    ensure_documented_functions()
    ensure_cisc108_tests(4)

Large Project
-------------

The following code is a long example of a real project that we've created using Pedal.
This is Pedal version 2, however the version 3 code will look different.

.. warning:: This is out of date for Pedal version 3!

.. code-block:: python
    :caption: grade_assignment.py

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
