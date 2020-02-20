from pedal.cait.cait_api import parse_program
from pedal.core.commands import explain, feedback
from pedal.core.feedback import AtomicFeedbackFunction, CompositeFeedbackFunction, Feedback
from pedal.toolkit.utilities import ensure_literal


@AtomicFeedbackFunction(title="Opened Without Arguments",
                        message_template=("You have called the <code>open</code> function "
                                          "without any arguments. It needs a filename.").format)
def open_without_arguments():
    return feedback(open_without_arguments.__name__, "toolkit", Feedback.CATEGORIES.INSTRUCTOR,
                    message=open_without_arguments.message_template())


@CompositeFeedbackFunction()
def files_not_handled_correctly(*filenames, muted=False):
    """
    Statically detect if files have been opened and closed correctly.
    This is only useful in the case of very simplistic file handling.
    """
    if filenames and isinstance(filenames[0], int):
        num_filenames = filenames[0]
        actual_filenames = False
    else:
        num_filenames = len(filenames)
        actual_filenames = True
    ast = parse_program()
    calls = ast.find_all("Call")
    called_open = []
    closed = []
    for a_call in calls:
        if a_call.func.ast_name == 'Name':
            if a_call.func.id == 'open':
                if not a_call.args:
                    open_without_arguments(muted)
                    return True
                called_open.append(a_call)
            elif a_call.func.id == 'close':
                explain("You have attempted to call <code>close</code> as a "
                        "function, but it is actually a method of the "
                        "file object.", 'verifier')
                return True
        elif a_call.func.ast_name == 'Attribute':
            if a_call.func.attr == 'open':
                explain("You have attempted to call <code>open</code> as a "
                        "method, but it is actually a built-in function.")
                return True
            elif a_call.func.attr == 'close':
                closed.append(a_call)
    if len(called_open) < num_filenames:
        explain("You have not opened all the files you were supposed to.")
        return True
    elif len(called_open) > num_filenames:
        explain("You have opened more files than you were supposed to.")
        return True
    withs = ast.find_all("With")
    if len(withs) + len(closed) < num_filenames:
        explain("You have not closed all the files you were supposed to.")
        return True
    elif len(withs) + len(closed) > num_filenames:
        explain("You have closed more files than you were supposed to.")
        return True
    if actual_filenames:
        return ensure_literal(*filenames)
    return False
