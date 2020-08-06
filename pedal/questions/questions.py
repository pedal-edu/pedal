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
