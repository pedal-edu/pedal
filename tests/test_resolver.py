import unittest
import os
import sys

from pedal.core.feedback import Feedback
from pedal.core.final_feedback import FinalFeedback

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pedal.core.commands import (clear_report, set_success, gently, explain, give_partial, suppress,
                                 contextualize_report, get_all_feedback, feedback)
from pedal.source import set_source, next_section, verify_section, verify, separate_into_sections
from pedal.tifa import tifa_analysis
from pedal.resolvers import simple, sectional
import pedal.sandbox.commands as commands
from tests.execution_helper import Execution, SUCCESS_TEXT, ExecutionTestCase, SUCCESS_MESSAGE


class TestResolver(ExecutionTestCase):

    def test_do_nothing(self):
        clear_report()
        final = simple.resolve()
        self.assertTrue(final.success)
        self.assertEqual(final.message, SUCCESS_TEXT)

    def test_gently(self):
        clear_report()
        gently('You should always create unit tests.')
        final = simple.resolve()
        self.assertFalse(final.success)
        self.assertEqual(final.message, 'You should always create unit tests.')

    def test_gently_order(self):
        clear_report()
        gently('A great and exciting message!')
        gently('A boring message that we should not show.')
        final = simple.resolve()
        self.assertFalse(final.success)
        self.assertEqual(final.message, 'A great and exciting message!')

    def test_set_success(self):
        clear_report()
        set_success()
        final = simple.resolve()
        self.assertTrue(final.success)
        self.assertEqual(final.message, 'Great work!')

    def test_gently_and_set_success(self):
        clear_report()
        gently("What have you done?")
        set_success()
        final = simple.resolve()
        self.assertFalse(final.success)
        self.assertEqual(final.message, 'What have you done?')

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
        self.assertEqual(SUCCESS_MESSAGE, final.title+"\n"+final.message)

    def test_partials(self):
        with Execution('0') as e:
            gently("You were incorrect.")
            give_partial(.1, message="You had a zero in your code.")
            give_partial(.1, message="You looped correctly.")
        self.assertFeedback(e, "Instructor Feedback\nYou were incorrect.")
        self.assertEqual(.2, e.final.score)
        self.assertFalse(e.final.success)

        with Execution('0') as e:
            give_partial(.1, message="You had a zero in your code.")
            give_partial(.1, message="You looped correctly.")
            gently("Okay but you still only wrote 0.")
        self.assertEqual(e.final.message, "Okay but you still only wrote 0.")
        self.assertEqual(e.final.score, .2)
        self.assertFalse(e.final.success)

        with Execution('0') as e:
            give_partial(.1, message="You had a zero in your code.")
            give_partial(.1, message="You looped correctly.")
            set_success()
        self.assertEqual(e.final.message, "Great work!")
        self.assertEqual(e.final.score, 1.2)
        self.assertTrue(e.final.success)

    def test_analyzer_suppression(self):
        clear_report()
        contextualize_report('1+"Hello"')
        verify()
        tifa_analysis()
        commands.run()
        suppress("analyzer")
        final = simple.resolve()
        self.assertEqual("runtime", final.category)
        self.assertEqual("Type Error", final.title)

    def test_runtime_suppression(self):
        clear_report()
        contextualize_report('import json\njson.loads("0")+"1"')
        verify()
        tifa_analysis()
        commands.run()
        suppress("Runtime")
        final = simple.resolve()
        self.assertEqual(Feedback.CATEGORIES.COMPLETE, final.category)
        self.assertEqual(SUCCESS_TEXT, final.message)

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
        self.assertEqual(SUCCESS_MESSAGE, final.title+"\n"+final.message)

    def test_empty(self):
        clear_report()
        contextualize_report('    ')
        verify()
        tifa_analysis()
        commands.run()
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
        commands.run()
        gently("I have a gentle opinion, but you don't want to hear it.")
        final = simple.resolve()
        print(final.label)
        self.assertEqual(Feedback.CATEGORIES.RUNTIME, final.category)

        # Runtime < Explain
        clear_report()
        contextualize_report('import json\njson.loads("0")+"1"')
        verify()
        tifa_analysis()
        commands.run()
        explain("LISTEN TO ME")
        final = simple.resolve()
        self.assertEqual(Feedback.CATEGORIES.INSTRUCTOR, final.category)

    def test_input(self):
        with Execution('input("Type something:")') as e:
            pass
        self.assertNotEqual(Feedback.CATEGORIES.RUNTIME, e.final.category)
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_input_with_conversion(self):
        with Execution('float(input("Type something:"))') as e:
            pass
        self.assertNotEqual(Feedback.CATEGORIES.RUNTIME, e.final.category)
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_sectional_error(self):
        clear_report()
        contextualize_report('a=0\n##### Part 1\nprint("A")\n##### Part 2\nsyntax error')
        separate_into_sections(independent=True)
        # Part 0
        verify()
        commands.clear_sandbox()
        commands.run()
        # Part 1
        next_section()
        verify()
        commands.clear_sandbox()
        commands.run()
        give_partial(.2)
        # Part 2
        next_section()
        verify()
        commands.clear_sandbox()
        commands.run()
        give_partial(.2)
        # Resolve everything
        finals = sectional.resolve()
        self.assertEqual("""# Global
FeedbackSourceSection
Feedback separated into groups
# 1
Complete
Great work!
# 2
Syntax Error
Bad syntax on line 5

The traceback was:
Line 5 of file answer.py
    syntax error


Suggestion: Check line 5, the line before it, and the line after it.""",
                         "\n".join(f"# {g.section_number if g is not None else 'Global'}\n{f.title}\n{f.message}"
                                   for g, f in finals.items()))

    def test_sectional_success(self):
        clear_report()
        contextualize_report('a=0\n##### Part 1\nprint("A")\n##### Part 2\nprint("B")')
        separate_into_sections(independent=True)
        # Part 0
        verify()
        commands.clear_sandbox()
        commands.run()
        # Part 1
        next_section()
        verify()
        commands.clear_sandbox()
        commands.run()
        give_partial(.2)
        # Part 2
        next_section()
        verify()
        commands.clear_sandbox()
        commands.run()
        give_partial(.2)
        # Resolve everything
        finals = sectional.resolve()
        self.assertEqual("""# Global
FeedbackSourceSection
Feedback separated into groups
# 1
Complete
Great work!
# 2
Complete
Great work!""",
                         "\n".join(f"# {g.section_number if g is not None else 'Global'}\n{f.title}\n{f.message}"
                                   for g, f in finals.items()))

    def test_attribute_error(self):
        with Execution('"".unsafe()', run_tifa=False) as e:
            pass
        self.assertEqual("Attribute Error", e.final.title)

    def test_combining_scores_complex(self):
        clear_report()
        contextualize_report('a=0\nprint(a)')
        # These are added
        feedback(activate=True, valence=1, score="+4%", category='instructor')
        # These are skipped
        feedback(activate=False, valence=1, score="+5%", category='instructor')
        # These are skipped
        feedback(activate=True, valence=-1, score="+8%", category='instructor')
        # These are added
        feedback(activate=False, valence=-1, score="+7%", category='instructor')
        # Calculate final result
        final = simple.resolve()
        self.assertEqual(.11, final.score)


if __name__ == '__main__':
    unittest.main(buffer=False)
