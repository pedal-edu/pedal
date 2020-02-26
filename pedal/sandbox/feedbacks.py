from pedal.core.commands import feedback
from pedal.core.report import MAIN_REPORT
from pedal.core.feedback import Feedback, CompositeFeedbackFunction
from pedal.sandbox import TOOL_NAME

@CompositeFeedbackFunction()
def runtime_error(message, name, exception, position, text=None, muted=False, group=None, report=MAIN_REPORT):
    """

    Args:
        message:
        name:
        exception:
        position:
        text:
        muted:
        group:
        report:

    Returns:

    """
    fields = {'message': message,
              'name': name,
              'error': exception,
              'position': position,
              'traceback': None}
    # TODO: Finish
    return feedback(name, tool=TOOL_NAME, category=Feedback.CATEGORIES.RUNTIME, kind=Feedback.KINDS.MISTAKE,
                    justification="A runtime error occurred during execution of some code", title=name,
                    message=message, text=text or message, fields=fields, locations=position, muted=muted,
                    version='0.0.1', group=group, report=report)
