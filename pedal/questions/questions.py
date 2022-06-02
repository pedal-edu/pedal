"""

######### Version 1

# Ends up executing all the questions' bodies
with Pool("P1") as pool:
    with Question("QA", "Create a for loop"):
        ensure_ast("For")
    with Question("QB", "Create an if statement"):
        ensure_ast("If")
pool.choose().ask()

######### Version 2

pool = Pool("P1", [question_A, question_B])

@pool.Question("Q", "Create a for loop")
def question_A():
    ensure_ast("For")

@pool.Question("QB", "Create an if statement")
def question_B():
    ensure_ast("If")

pool.choose().ask()

######### Version 3

with Pool("P1") as pool:
    if pool.asked_question("QA", "Create a for loop"):
        ensure_ast("For")
    if pool.asked_question("QB", "Create an if statement"):
        ensure_ast("If")

"""
from pedal.core.feedback import FeedbackGroup
from pedal.core.feedback_category import FeedbackCategory, FeedbackKind
from pedal.core.report import MAIN_REPORT
from pedal.questions.graders import QuestionGrader
from pedal.questions.constants import TOOL_NAME
from pedal.questions.feedbacks import show_question
from pedal.questions.pool import Pool


class QuestionGroup(FeedbackGroup):
    category = FeedbackCategory.INSTRUCTIONS
    kind = FeedbackKind.INSTRUCTIONAL
    justification = 'Question was asked but not answered.'
    title = 'Question Group'
    priority = 'instructions'
    tool = TOOL_NAME
    valence = 0
    muted = True

    def __init__(self, name, report, try_all=True, **kwargs):
        super().__init__(delay_condition=True, **kwargs)
        self.name = name
        self.all_feedback = []
        self.try_all= try_all

    def _get_child_feedback(self, feedback, active):
        self.all_feedback.append(feedback)

    def __enter__(self):
        self.report.start_group(self)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Go through all my collected assertions
        # Count failures, errors, successes
        # If there are any non-successes, then produce a summary table.
        #   Otherwise produce a success within this group
        # Mute and unscore any feedbacks (use their scores though)
        self.report.stop_group(self)
        self._handle_condition()
        return False


class Question:
    """

    """
    def __init__(self, name, instructions, *tests, seed=None, report=MAIN_REPORT, try_all=True):
        self.name = name
        self.instructions = instructions
        self.tests = tests
        self.seed = seed
        self.report = report
        self.answered = False
        self.try_all = try_all
        self.question_group = QuestionGroup(self.name, self.try_all)

    def __enter__(self):
        Pool.add_question_via_context(self)
        self.question_group.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.question_group.__exit__(exc_type, exc_value, traceback)

    def answer(self):
        """

        """
        self.answered = True

    def ask(self):
        """

        """
        all_tests = []
        for test in self.tests:
            # Unpack one layer of nesting
            if isinstance(test, list):
                all_tests.extend(test)
            else:
                all_tests.append(test)
        results = []
        with self.question_group:
            for test in all_tests:
                if isinstance(test, QuestionGrader):
                    results.append(test._test(self))
                else:
                    results.append(test(self))
        answered = False
        if all(r is not False for r in results) and not any(self.question_group.all_feedback):
            answered = True
        if self.answered:
            answered = True
        if not answered:
            show_question(self.instructions, report=self.report)


