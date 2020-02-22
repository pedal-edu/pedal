import unittest
import os
import sys

from pedal.core.feedback import Feedback

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pedal.core.commands import (clear_report, set_success, gently, explain, give_partial, suppress,
                                 contextualize_report, get_all_feedback)
from pedal.source import set_source, next_section, verify_section, verify, separate_into_sections
from pedal.tifa import tifa_analysis
from pedal.resolvers import simple, sectional
import pedal.sandbox.compatibility as compatibility
from tests.execution_helper import Execution


class TestCode(unittest.TestCase):

    def test_gently(self):
        clear_report()
        final = simple.resolve()
        self.assertFalse(final.success)
        self.assertEqual(final.message, "No errors reported.")

        gently('You should always create unit tests.')
        final = simple.resolve()
        self.assertFalse(final.success)
        self.assertEqual(final.message, 'You should always create unit tests.')

        gently('A boring message that we should not show.')
        final = simple.resolve()
        self.assertFalse(final.success)
        self.assertEqual(final.message, 'You should always create unit tests.')

        set_success()
        final = simple.resolve()
        self.assertTrue(final.success)
        self.assertEqual(final.message, 'You should always create unit tests.')

    def test_explain(self):
        # Tifa < Explain
        with Execution('1+""') as e:
            explain("You cannot add those.")
        self.assertEqual(e.final.message, "You cannot add those.")
        # Tifa > Gently
        with Execution('1+""') as e:
            gently("You cannot add those.")
        self.assertEqual(e.final.title, "Incompatible types")

    def test_hidden_error(self):
        clear_report()
        contextualize_report('import pedal')
        verify()
        tifa_analysis()
        final = simple.resolve()
        self.assertNotEqual("No errors reported.", final.message)

    def test_unmessaged_tifa(self):
        clear_report()
        contextualize_report('import random\nrandom')
        verify()
        tifa_analysis()
        final = simple.resolve()
        print(final)
        self.assertEqual("No errors reported.", final.message)

    def test_partials(self):
        with Execution('0') as e:
            give_partial(.1, "You had a zero in your code.")
            give_partial(.1, "You looped correctly.")
        self.assertEqual(e.final.message, "No errors reported.")
        self.assertEqual(e.final.score, .2)
        self.assertFalse(e.final.success)

        with Execution('0') as e:
            give_partial(.1, "You had a zero in your code.")
            give_partial(.1, "You looped correctly.")
            gently("Okay but you still only wrote 0.")
        self.assertEqual(e.final.message, "Okay but you still only wrote 0.")
        self.assertEqual(e.final.score, .2)
        self.assertFalse(e.final.success)

        with Execution('0') as e:
            give_partial(.1, "You had a zero in your code.")
            give_partial(.1, "You looped correctly.")
            set_success()
        self.assertEqual(e.final.message, "Great work!")
        self.assertEqual(e.final.score, 1.2)
        self.assertTrue(e.final.success)

    def test_analyzer_suppression(self):
        clear_report()
        contextualize_report('1+"Hello"')
        verify()
        tifa_analysis()
        compatibility.run_student(raise_exceptions=True)
        suppress("analyzer")
        final = simple.resolve()
        self.assertEqual("runtime", final.category)
        self.assertEqual("TypeError", final.title)

    def test_runtime_suppression(self):
        clear_report()
        contextualize_report('import json\njson.loads("0")+"1"')
        verify()
        tifa_analysis()
        compatibility.run_student(raise_exceptions=True)
        suppress("Runtime")
        final = simple.resolve()
        self.assertEqual(Feedback.CATEGORIES.COMPLETE, final.category)
        self.assertEqual("No errors reported.", final.message)

    def test_premade_exceptions(self):
        try:
            a
        except Exception as e:
            ne = e
        clear_report()
        contextualize_report('a=0\na')
        verify()
        compatibility.raise_exception(ne)
        final = simple.resolve()
        self.assertEqual(final.message, "<pre>name 'a' is not defined</pre>\n" +
                         "A name error almost always means that you have used a variable before it has a value.  Often "
                         "this may be a simple typo, so check the spelling carefully.  <br><b>Suggestion: </b>Check the"
                         " right hand side of assignment statements and your function calls, this is the most likely "
                         "place for a NameError to be found. It really helps to step through your code, one line at a "
                         "time, mentally keeping track of your variables.")

    def test_suppress_premade(self):
        try:
            a
        except Exception as e:
            ne = e
        clear_report()
        contextualize_report('import json\njson.loads("0")+"1"')
        verify()
        tifa_analysis()
        compatibility.raise_exception(ne)
        suppress("Runtime")
        final = simple.resolve()
        self.assertEqual(Feedback.CATEGORIES.COMPLETE, final.category)
        self.assertEqual("No Errors", final.title)
        self.assertEqual("No errors reported.", final.message)

    def test_success(self):
        clear_report()
        contextualize_report('a=0\na')
        verify()
        tifa_analysis()
        set_success()
        final = simple.resolve()
        self.assertEqual(Feedback.CATEGORIES.COMPLETE, final.category)
        self.assertEqual("Complete", final.title)
        self.assertEqual("Great work!", final.message)

    def test_success_suppression(self):
        clear_report()
        contextualize_report('a=0\na')
        verify()
        tifa_analysis()
        set_success()
        suppress(label='set_success')
        final = simple.resolve()
        self.assertEqual(Feedback.CATEGORIES.COMPLETE, final.category)
        self.assertEqual("No Errors", final.title)
        self.assertEqual("No errors reported.", final.message)

    def test_empty(self):
        clear_report()
        contextualize_report('    ')
        verify()
        tifa_analysis()
        compatibility.run_student(raise_exceptions=True)
        final = simple.resolve()
        self.assertEqual(Feedback.CATEGORIES.SYNTAX, final.category)
        self.assertEqual("No Source Code", final.title)
        self.assertEqual("Source code file is blank.", final.message)

    def test_gently_vs_runtime(self):
        # Runtime > Gently
        clear_report()
        contextualize_report('import json\njson.loads("0")+"1"')
        verify()
        tifa_analysis()
        compatibility.run_student(raise_exceptions=True)
        gently("I have a gentle opinion, but you don't want to hear it.")
        final = simple.resolve()
        self.assertEqual(Feedback.CATEGORIES.RUNTIME, final.category)

        # Runtime < Explain
        clear_report()
        contextualize_report('import json\njson.loads("0")+"1"')
        verify()
        tifa_analysis()
        compatibility.run_student(raise_exceptions=True)
        explain("LISTEN TO ME")
        final = simple.resolve()
        self.assertEqual(Feedback.CATEGORIES.INSTRUCTOR, final.category)

    def test_input(self):
        with Execution('input("Type something:")') as e:
            pass
        self.assertNotEqual(Feedback.CATEGORIES.RUNTIME, e.final.category)
        self.assertEqual("No Errors", e.final.title)

        with Execution('float(input("Type something:"))') as e:
            pass
        self.assertNotEqual(Feedback.CATEGORIES.RUNTIME, e.final.category)
        self.assertEqual("No Errors", e.final.title)

    def test_sectional_error(self):
        clear_report()
        contextualize_report('a=0\n##### Part 1\nprint("A")\n##### Part 2\nsyntax error')
        separate_into_sections()
        verify()
        next_section()
        if verify_section():
            compatibility.run_student(raise_exceptions=True)
            give_partial(.2)
        next_section()
        if verify_section():
            compatibility.run_student(raise_exceptions=True)
            give_partial(.3)
        (success, score, hc, messages) = sectional.resolve()
        self.assertEqual(success, False)
        self.assertEqual(score, .2)
        self.assertEqual(len(messages), 1)

    def test_sectional_success(self):
        clear_report()
        contextualize_report('a=0\n##### Part 1\nprint("A")\n##### Part 2\nprint("B")')
        separate_into_sections()
        next_section()
        if verify_section():
            compatibility.run_student(raise_exceptions=True)
            give_partial(.2)
        next_section()
        if verify_section():
            compatibility.run_student(raise_exceptions=True)
            give_partial(.3)
            set_success()
        (success, score, hc, messages) = sectional.resolve()
        self.assertEqual(success, True)
        self.assertEqual(score, .5)
        self.assertEqual(len(messages), 1)

    def test_attribute_error(self):
        with Execution('"".unsafe()') as e:
            pass
        self.assertEqual("AttributeError", e.final.title)


if __name__ == '__main__':
    unittest.main(buffer=False)
