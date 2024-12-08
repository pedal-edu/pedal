from textwrap import dedent

from pedal.assertions.feedbacks import assert_group
from pedal.assertions.runtime import *
from pedal.core.commands import suppress
from pedal.sandbox.commands import call, start_trace, get_sandbox, evaluate, CommandBlock, run
from tests.execution_helper import Execution, ExecutionTestCase, SUCCESS_MESSAGE
from pedal.sandbox.library.drafter_library import MockDrafter
import unittest


class TestDrafter(ExecutionTestCase):

    def test_basic_mocking(self):
        with Execution(dedent("""
        from drafter import *
        from dataclasses import dataclass
        @dataclass
        class State:
            pass
        @route
        def index(state: State) -> Page:
            return Page(state, ["Hello World!"])
        start_server(State())
        """)) as e:
            suppress("algorithmic")
            pass # assert_route("index")
        self.assertIsNone(e.student.exception)
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_style_mocking(self):
        with Execution(dedent("""
        from drafter import *
        from dataclasses import dataclass
        from bakery import assert_equal
        @dataclass
        class State:
            pass
        @route
        def index(state: State) -> Page:
            return Page(state, [
                "Hello World!",
                bold("This is bold"),
                Span("This is a span"),
                bold(Span("This is a bolded span")),
                
            ])
        start_server(State())
        
        assert_equal(index(State()), Page(State(), [
            "Hello World!",
            "This is made up",
            "This is bold",
            "This is a span",
            "This is a bolded span"
        ]))
        """)) as e:
            suppress("algorithmic")
        self.assertIsNone(e.student.exception)
        self.assertFeedback(e, SUCCESS_MESSAGE)