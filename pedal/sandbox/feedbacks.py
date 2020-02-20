from pedal.core.commands import feedback
from pedal.core.report import MAIN_REPORT
from pedal.core.feedback import Feedback
from pedal.sandbox import TOOL_NAME


def runtime_error(message, exception, position, report=MAIN_REPORT):
    fields = {'message': message,
               'error': exception,
               'position': position,
               'traceback': None}
    # TODO: Finish
    return feedback("runtime_error", category=Feedback.CATEGORIES.RUNTIME, tool=TOOL_NAME,
                    message=message)
