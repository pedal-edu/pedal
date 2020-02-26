from pedal.core.report import MAIN_REPORT
from pedal.questions.graders import QuestionGrader


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


def show_question(instructions, report=MAIN_REPORT):
    """

    Args:
        instructions:
        report:
    """
    report.attach('Question', category='Instructions', tool='Questions',
                  group=report.group, priority='instructions', hint=instructions)
