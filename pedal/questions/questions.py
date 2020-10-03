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


from pedal.core.feedback import Feedback
from pedal.core.feedback_category import FeedbackCategory, FeedbackKind
from pedal.core.report import MAIN_REPORT
from pedal.questions.graders import QuestionGrader
from pedal.questions.constants import TOOL_NAME


class Question:
    """

    """
    def __init__(self, name, instructions, tests, seed=None, report=MAIN_REPORT):
        self.name = name
        self.instructions = instructions
        self.tests = tests
        self.seed = seed
        self.report = report
        self.answered = False

    def answer(self):
        """

        """
        self.answered = True

    def ask(self):
        """

        """
        if isinstance(self.tests, QuestionGrader):
            self.tests._test(self)
        else:
            for test in self.tests:
                test(self)
        if not self.answered:
            show_question(self.instructions, report=self.report)


class show_question(Feedback):
    """

    Args:
        instructions:
        report:
    """
    category = FeedbackCategory.INSTRUCTIONS
    kind = FeedbackKind.INSTRUCTIONAL
    justification = 'Question was asked but not answered.'
    title = 'Show Question'
    priority = 'instructions'
    tool = TOOL_NAME
    valence = 0

    def __init__(self, instructions, **kwargs):
        super().__init__(message=instructions, **kwargs)
