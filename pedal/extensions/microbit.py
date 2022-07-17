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


def assert_microbit_displayed(image, report_differences=5, report=MAIN_REPORT, **kwargs):
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
    for old_image in microbit.display.history:
        differences = match_image(image, old_image, **kwargs)
        if not differences:
            return None
        if smallest_difference is None or len(smallest_difference) > len(differences):
            smallest_difference = differences
    else:
        return image_not_displayed(image, report_differences, smallest_difference)


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