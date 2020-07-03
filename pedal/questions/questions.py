from pedal.core.feedback import AtomicFeedbackFunction
from pedal.core.feedback_category import FeedbackCategory, FeedbackKind
from pedal.core.report import MAIN_REPORT
from pedal.questions.graders import QuestionGrader
from pedal.core.commands import feedback
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
            show_question(self.instructions, self.report)


@AtomicFeedbackFunction('show_question')
def show_question(instructions, report=MAIN_REPORT):
    """

    Args:
        instructions:
        report:
    """
    fields = {'instructions': instructions}
    feedback(show_question.__name__, tool=TOOL_NAME, category=FeedbackCategory.INSTRUCTIONS,
             kind=FeedbackKind.INSTRUCTIONAL, justification='Question was asked but not answered.',
             priority='instructions', valence=0, title='Show Question', message=instructions,
             text=instructions, fields=fields, report=report)
