from pedal.core.feedback import Feedback
from pedal.core.feedback_category import FeedbackCategory, FeedbackKind
from pedal.questions.constants import TOOL_NAME


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
