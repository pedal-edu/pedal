from textwrap import dedent

from pedal.assertions.feedbacks import assert_group
from pedal.assertions.runtime import *
from pedal.sandbox.commands import call, start_trace, get_sandbox, evaluate, CommandBlock, run
from tests.execution_helper import Execution, ExecutionTestCase, SUCCESS_MESSAGE
from pedal.extensions.microbit import assert_microbit_displayed, assert_microbit_displaying
import unittest


class TestAssertions(ExecutionTestCase):

    def test_assert_microbit_displayed_simple_2d_list_passes(self):
        with Execution(dedent("""
        from microbit.display import show
        # A 3x3 box with the bottom-left corner and center missing
        show([[0, 0, 0, 0, 0], [0, 9, 9, 9, 0], [0, 9, 0, 9, 0], [0, 0, 9, 9, 0], [0, 0, 0, 0, 0]])
        """)) as e:
            assert_microbit_displayed("     "
                                      " ███ "
                                      " █ █ "
                                      "  ██ "
                                      "     ", report_differences=True)
        self.assertIsNone(e.student.exception)
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_assert_microbit_displayed_simple_2d_list_fails(self):
        with Execution(dedent("""
        from microbit.display import show
        # A 3x3 box with the bottom-left corner and center missing
        show([[0, 0, 0, 0, 0], [0, 9, 9, 9, 0], [0, 9, 0, 9, 0], [0, 0, 9, 9, 0], [0, 0, 0, 0, 0]])
        """)) as e:
            assert_microbit_displayed("     "
                                      " ██  "
                                      " █ █ "
                                      " ███ "
                                      "     ", report_differences=True)
        self.assertIsNone(e.student.exception)
        self.assertFeedback(e, """Image Not Displayed on Microbit
The expected image was not displayed on the Microbit.
The closest actual image shown had 2 differences.
The differences were at the following positions:
    3, 1: 9 instead of 0
    1, 3: 0 instead of 9""")

    def test_assert_microbit_displaying_2d_list_passes(self):
        with Execution(dedent("""
        from microbit.display import show
        # A 3x3 box with the bottom-left corner and center missing
        show([[0, 0, 0, 0, 0], [0, 9, 9, 9, 0], [0, 9, 0, 9, 0], [0, 0, 9, 9, 0], [0, 0, 0, 0, 0]])
        """)) as e:
            assert_microbit_displaying("     "
                                       " ███ "
                                       " █ █ "
                                       "  ██ "
                                       "     ", True)
        self.assertIsNone(e.student.exception)
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_assert_microbit_displaying_2d_list_fails_current(self):
        with Execution(dedent("""
        from microbit.display import show
        # A 3x3 box with the bottom-left corner and center missing
        show([[0, 0, 0, 0, 0], [0, 9, 9, 9, 0], [0, 9, 0, 9, 0], [0, 0, 9, 9, 0], [0, 0, 0, 0, 0]])
        show([[0, 0, 0, 0, 0], [0, 9, 9, 9, 0], [0, 9, 9, 9, 0], [0, 0, 9, 9, 0], [0, 0, 0, 0, 0]])
        """)) as e:
            assert_microbit_displaying("     "
                                       " ███ "
                                       " █ █ "
                                       "  ██ "
                                       "     ", True)
        self.assertIsNone(e.student.exception)
        self.assertFeedback(e, """Image Not Displaying on Microbit
The expected image is not currently displaying on the Microbit.
The image actually shown had 1 differences.
The differences were at the following positions:
    2, 2: 9 instead of 0""")

    def test_assert_microbit_displayed_animation_touches_corners(self):
        with Execution(dedent("""
        from microbit.display import show
        # A 3x3 box with the bottom-left corner and center missing
        show([[0, 0, 0, 0, 9], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]])
        show([[9, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]])
        show([[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [9, 0, 0, 0, 0]])
        show([[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 9]])
        """)) as e:
            assert_microbit_displayed("    █:     :     :     :     ",
                                      "█    :     :     :     :     ",
                                      "     :     :     :     :█    ",
                                      "     :     :     :     :    █", report_differences=True)
        self.assertIsNone(e.student.exception)
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_assert_microbit_displayed_animation_touches_corners_fails(self):
        with Execution(dedent("""
        from microbit.display import show
        # A 3x3 box with the bottom-left corner and center missing
        show([[0, 0, 0, 0, 9], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]])
        show([[9, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]])
        show([[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [9, 0, 0, 0, 0]])
        show([[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 9]])
        """)) as e:
            assert_microbit_displayed("    █:     :     :     :     ",
                                      "█    :     :     :     :     ",
                                      "     :     :     :     :     ",
                                      "     :     :     :     :    █", report_differences=True)
        self.assertIsNone(e.student.exception)
        self.assertFeedback(e, """Image Not Displayed on Microbit
The expected image was not displayed on the Microbit.
The closest actual image shown had 1 differences.
The differences were at the following positions:
    4, 0: 0 instead of 9""")

    def test_assert_microbit_displayed_animation_touches_corners_loop(self):
        with Execution(dedent("""
        from microbit.display import show
        # A 3x3 box with the bottom-left corner and center missing
        STARTS = [(4, 0), (0, 0), (0, 4), (4, 4)]
        DIRECTIONS = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        current = [[0, 0, 0, 0, 0] for _ in range(5)]
        previous_x, previous_y = (0, 0)
        for (start_x, start_y), (dx, dy) in zip(STARTS, DIRECTIONS):
            for i in range(0, 5):
                current[previous_y][previous_x] = 0
                previous_x, previous_y = start_x + dx*i, start_y + dy*i
                current[previous_y][previous_x] = 9
                show(current)
        """)) as e:
            assert_microbit_displayed("    █:     :     :     :     ",
                                      " █   :     :     :     :     ",
                                      "█    :     :     :     :     ",
                                      "     :     :     :     :█    ",
                                      "     :     :     :     :    █", report_differences=True)
        self.assertIsNone(e.student.exception)
        self.assertFeedback(e, SUCCESS_MESSAGE)