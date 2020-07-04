"""
Generic runtime exception feedback class.
"""
from pedal.core.feedback import FeedbackResponse
from pedal.sandbox import TOOL_NAME


class runtime_error(FeedbackResponse):
    """ Used to create all runtime errors """
    tool = TOOL_NAME
    category = FeedbackResponse.CATEGORIES.RUNTIME
    kind = FeedbackResponse.KINDS.MISTAKE
    justification = "A runtime error occurred during execution of some code"

    def __init__(self, message, name, exception, location, **kwargs):
        fields = {'message': message,
                  'name': name,
                  'error': exception,
                  'location': location,
                  'traceback': None}
        super().__init__(label=name, fields=fields, **kwargs)
