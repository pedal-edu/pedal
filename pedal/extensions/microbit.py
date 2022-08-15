"""
Mock module for BBC Microbit API.

Image formats:
    list[list[int]] (or any kind of 2d sequence)
    list[list[str]]

    A single string with lines separated by colons.
    A single string with lines separated by newlines.
    A single string without separators.

    Brightness values can be integers or characters
    You can use "?" as a "don't care" symbol for string representations.
    Equivalent values:
        `0`, ` `, `_`, `⬛`
        `9`, `*`, `■`, `█`, `🟥`, `⬜`, `X`, `x`

    You can also specify via a dictionary:
        Points (x, y) => Brightness value


microbit.display.scroll - in addition to capturing the screen history, also capture the message history
microbit.display.show - and in general here too, capture any strings being show so they can be queries.

assert_microbit_displayed(image)
assert_microbit_displayed(image1, image2, ...)
assert_microbit_displaying(image)

assert_microbit_printed(text)
assert_microbit_printed_contains(text)

Lingering questions:
* How do we want to simulate inputs (e.g., pins, buttons, etc.)? Some kind of Jest-like API?

```python
# Pressing the button prints its letter
assert_microbit_printed(None)
user.press_button_a()
assert_microbit_printed('a')
user.press_button_b()
assert_microbit_printed('b')

# Simulating Flappy Bit?
assert_microbit_displayed("<bits indicating the bird is initially center>")
user.tilt_up()
```

# Infinite loops

A major issue is infinite loops.
* In some places, the loops are simply triggered by keyword arguments. For example, the `microbit.display.show` function
    can take a `loop` boolean to "loop forever". They also have a `wait` keyword to block until the animation is finished.
    Otherwise the animation happens in the background (asynchronously, I assume?).
* A major pattern is to have students do all their work within a `while True:` loop, or other kind of "infinite" loop.

The async story in Skulpt is questionable. I honestly have to go research what the current state is. I mean, heck,
the async story in JavaScript is a little questionable at times. But I think there is definitely some potential here,
even if we had to do gross things like use `exec` and stuff. So executing is not off the table, I'm pretty sure.

The harder question is how we meaningfully simulate it from the instructor code. I think a lot of this will come down
to what the instructor actually wants to do.

### While->Function

A simple strategy for handling the `while True` loop pattern is for the autograder to transform all `while True` loops
into function definitions with `if` statements inside. An example:

```python
# answer.py
from microbit.display import show
counter = 0
while True:
    show(counter)
    counter += 1

# Becomes answer.py (transformed)
from microbit.display import show
counter = 0
def _microbit_main_loop():
    global counter
    if True:
        show(counter)
        counter += 1

# Then the instructor code can be free to "use" the student code however they want
# instructor.py
from pedal import *

run()
assert_microbit_displayed(None)
call('_microbit_main_loop')     # Perhaps aliased to step_student() ?
assert_microbit_displaying(1, message="The first iteration of your loop should display the number `1`!")
call('_microbit_main_loop')
assert_microbit_displaying(2)
```

This `while->function` approach has several nightmares attached:
* How do we correctly identify between the main loop and other loops? What about inner infinite loops?
    * Heuristics could go pretty far; most of the time, won't code fit a known pattern?
* What about global variables that are modified?
    * We can track global variables and inject the `global` keyword into the function
* What about errors and such in the original code?
    * Pedal already handles this with the `source` module! It can at least have an "offset" in the code. But I'm
        thinking this may also require having "skipped" lines and/or "remapped" lines. The former would let you mark
        lines as not counting towards the total, and the latter would explicitly change existing lines.
    * Unfortunately, we don't *actually* have a way to "modify" code in Pedal. But that's easily changed, I've always
        considered writing such a module. And we can dig around for a suitable existing one if we want.

Let's do a longer example where we grade the circle light game but with button presses involved. In this version,
the A button makes it run around the edge (otherwise it will just sit there). The B button ends the game.

```python
# Start off with light in topleft
run()
assert_microbit_displaying("9" + "0"*24)
# Idling for 3 ticks should do nothing
for _ in range(3):
    step()
    assert_microbit_displaying("9" + "0"*24)
# Pressing A should make it do a circle
press_a()
step(times=16+1)   # Has to run around the perimeter, or 4*4 steps, plus one in case they need the help
assert_microbit_displayed(*EDGE_STRINGS)
# Make sure it returned to the starting point
assert_microbit_displaying("9" + "0"*24)
# Pressing B should end the loop
press_b()
step()
assert_microbit_loop_ended()
```

The `step` function finds the main game loop, and executes it. That function will return whether the loop body
was actually executed. That information is also stored in such a way that the `assert_microbit_loop_ended` function
can query it.

### While->For

A somewhat related concept is the idea of transforming the `while` loop into a `for` loop (or perhaps even an
`async for` loop?). That `for` loop can have a generator with our own tooling equipped.

```python
# answer.py
from microbit.display import show
counter = 0
while True:
    show(counter)
    counter += 1

# Becomes
from microbit.display import show
counter = 0
for _microbit_time in _microbit_main_for_loop(_instructor_code):
    show(counter)
    counter += 1

# Then we have...
# instructor.py
from pedal import *

def grade_loop_iteration(student):
    assert_microbit_displaying(1)
    yield
    assert_microbit_displaying(2)

run_async(grade_loop_iteration)
```

A major advantage over the function approach is that we are no longer beholden to the scope problems of function
definitions. But does this let us achieve our goal?

```python
def run_async():
    student_code = get_program()
    exec(student_code)
```

(Experimented with this in a scratch file. The answer is that it might work for the cpython version, but is incompatible
with the current version of the Skulpt execution model, I *think* (tried it from the student side, but not the instructor).
The basic issue is that exec uses its own separate dictionary that doesn't get updated until after the execution
finishes, I believe, so there's no way to get the "in-progress" student data? Might be solveable.

But the bigger issue with what I was trying there is that the instructor ends up having to stuff all their code in
a function that uses yield quite a bit. I'm not a huge fan of forcing the instructor to think that way?

### Async API?

A more complicated idea is to have blocking API calls for the API, that yield execution back to the instructor.

```python
# answer.py
from microbit.display import show
counter = 0
while True:
    show(counter)
    counter += 1

# instructor.py

run()     # Non-blocking version that executes in a separate thread?
await shown(1)
await shown(2)
```

So that `shown` function is obviously doing some interesting stuff:

```python
def shown(value, timeout=1000):
    '''
    Args:
        timeout (int): How long to wait before giving up on the value being displayed. A message will be shown
            to the students.
    '''
```
"""
from pedal.core.feedback import Feedback
from pedal.core.report import MAIN_REPORT
from pedal.sandbox.commands import get_module

BRIGHTNESS_VALUE = {
    0: 0, '0': 0, ' ': 0, '_': 0, '⬛': 0,
    1: 1, '1': 1,
    2: 2, '2': 2,
    3: 3, '3': 3,
    4: 4, '4': 4,
    5: 5, '5': 5,
    6: 6, '6': 6,
    7: 7, '7': 7,
    8: 8, '8': 8,
    9: 9, '9': 9, '*': 9, '■': 9, '█': 9, '🟥': 9, '⬜': 9, 'X': 9, 'x': 9,
}


class ImageFeedback(Feedback):
    def make_hint(self, differences, report):
        return "\n".join(
            f"{report.format.indent()}{x}, {y}: {report.format.python_expression(repr(actual))}"
            f" instead of {report.format.python_expression(repr(brightness))}"
            for x, y, brightness, actual in differences
        )


class image_not_displayed(ImageFeedback):
    category = Feedback.CATEGORIES.INSTRUCTOR
    title = "Image Not Displayed on Microbit"
    message_template = "The expected image was not displayed on the Microbit.{difference_hint}"

    def __init__(self, expected, max_differences, differences, report=MAIN_REPORT, **kwargs):
        fields = kwargs.setdefault('fields', {})
        fields['expected'] = expected
        fields['max_differences'] = max_differences
        fields['differences'] = differences
        if max_differences:
            fields['difference_hint'] = f"\nThe closest actual image shown had {len(differences)} differences.\n"
            if max_differences is True or len(differences) <= max_differences:
                fields['difference_hint'] += "The differences were at the following positions:\n" + self.make_hint(differences, report)
        else:
            fields['difference_hint'] = ""
        super().__init__(**kwargs)


class image_not_displaying(ImageFeedback):
    category = Feedback.CATEGORIES.INSTRUCTOR
    title = "Image Not Displaying on Microbit"
    message_template = "The expected image is not currently displaying on the Microbit.{difference_hint}"

    def __init__(self, expected, max_differences, differences, report=MAIN_REPORT, **kwargs):
        fields = kwargs.setdefault('fields', {})
        fields['expected'] = expected
        fields['max_differences'] = max_differences
        fields['differences'] = differences
        if max_differences:
            fields['difference_hint'] = f"\nThe image actually shown had {len(differences)} differences.\n"
            if max_differences is True or len(differences) <= max_differences:
                fields['difference_hint'] += "The differences were at the following positions:\n" + self.make_hint(differences, report)
        else:
            fields['difference_hint'] = ""
        super().__init__(**kwargs)


def match_image_dict(target, candidate, **kwargs):
    return False


def match_image_str(target, candidate, **kwargs):
    if ':' in target:
        lines = target.split(':')
    elif '\n' in target:
        lines = target.split('\n')
    else:
        lines = [target[run:run+5] for run in range(0, len(target), 5)]
    differences = []
    for y, (target_line, candidate_line) in enumerate(zip(lines, candidate)):
        for x, (target_b, candidate_b) in enumerate(zip(target_line, candidate_line)):
            brightness = BRIGHTNESS_VALUE.get(target_b, '?')
            if brightness != '?' and brightness != candidate_b:
                differences.append((x, y, brightness, candidate_b))
    return differences


def match_image_2d(target, candidate, **kwargs):
    return False


def match_image(target, candidate, **kwargs):
    if isinstance(target, dict):
        return match_image_dict(target, candidate, **kwargs)
    if isinstance(target, str):
        return match_image_str(target, candidate, **kwargs)
    # Assume 2D sequence
    return match_image_2d(target, candidate, **kwargs)


def assert_microbit_displayed(image, *additional_images, report_differences=5, report=MAIN_REPORT, **kwargs):
    """

    Args:
        image: Either a 2d sequence of integers/strings, a single string of several possible formats, or a dictionary
            mapping positions to values.
        differences: How many differences to report. If `True`, then all pixels that are not equivalent will be
            reported. If an integer, then if the number of differences is less than or equal to that number, they
            will be reported. If `False`, then no differences are shown.
        report:

    Returns:

    """
    microbit = get_module('microbit', report=report)
    smallest_difference = None
    all_images = [image, *additional_images]
    all_history = iter(microbit.display.history)
    for image in all_images:
        for old_image in all_history:
            differences = match_image(image, old_image, **kwargs)
            if not differences:
                break
            if smallest_difference is None or len(smallest_difference) > len(differences):
                smallest_difference = differences
        else:
            return image_not_displayed(image, report_differences, smallest_difference)
    else:
        return False


def assert_microbit_displaying(image, report_differences=5, report=MAIN_REPORT, **kwargs):
    """

    Args:
        image: Either a 2d sequence of integers/strings, a single string of several possible formats, or a dictionary
            mapping positions to values.
        differences: How many differences to report. If `True`, then all pixels that are not equivalent will be
            reported. If an integer, then if the number of differences is less than or equal to that number, they
            will be reported. If `False`, then no differences are shown.
        report:

    Returns:

    """
    microbit = get_module('microbit', report=report)
    differences = match_image(image, microbit.display.current.image, **kwargs)
    if not differences:
        return None
    return image_not_displaying(image, report_differences, differences)