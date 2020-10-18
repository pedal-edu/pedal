"""
Generic runtime exception feedback class.
"""
from pedal.core.location import Location
from pedal.core.report import MAIN_REPORT
from pedal.sandbox.data import format_contexts
from pedal.utilities.exceptions import KeyError, get_exception_name
from pedal.core.feedback import FeedbackResponse
from pedal.sandbox import TOOL_NAME
from pedal.utilities.text import add_indefinite_article

RUNTIME_ERROR_MESSAGE_HEADER = (
    "{exception_name} occurred:\n\n"
    "{exception_message}\n\n"
    "{context_message}\n"
    "The traceback was:\n{traceback_message}\n"
)


class runtime_error(FeedbackResponse):
    """
    Used to create all runtime errors.

    Attributes:
        exception (Exception): The original exception.
        exception_name (str): The original name of the exception.
        exception_message (str): the original error message from the exception.
        traceback (:py:class:`~pedal.utilities.exceptions.ExpandedTraceback`):
            An enhanced version of the builtin Traceback object. Has a number
            of additional fields.
        traceback_message (str): A nicely formatted version of the traceback.
        context (list[:py:class:`~pedal.sandbox.data.SandboxContext`]): The
            history of inputs, outputs, executed code, and other information
            from when this runtime error occurred. Usually just a single
            element, but sometimes longer if created in a grouping context.
            If the code was run from a file, then the filename is given.

    """
    tool = TOOL_NAME
    category = FeedbackResponse.CATEGORIES.RUNTIME
    kind = FeedbackResponse.KINDS.MISTAKE
    justification = "A runtime error occurred during execution of some code."
    version = '1.1.0'
    message_template = RUNTIME_ERROR_MESSAGE_HEADER

    def __init__(self, exception, context, traceback, location, **kwargs):
        report = kwargs.get('report', MAIN_REPORT)
        exception_name = get_exception_name(exception)
        exception_name_proper = add_indefinite_article(exception_name)
        exception_message = str(exception).capitalize()
        if type(exception) not in EXCEPTION_FF_MAP:
            title = exception_name
        else:
            title = EXCEPTION_FF_MAP[type(exception)].title
        location = Location(location)
        traceback_stack = traceback.build_traceback()
        traceback_message = traceback.format_traceback(traceback_stack,
                                                       report.format)
        context_message = format_contexts(context, report.format)
        fields = {'exception': exception,
                  'exception_name': exception_name_proper,
                  'exception_message': report.format.exception(exception_message),
                  'location': location,
                  'traceback': traceback,
                  'traceback_stack': traceback_stack,
                  'traceback_message': traceback_message,
                  'context': context,
                  'context_message': context_message}
        super().__init__(fields=fields, title=title,
                         location=location, **kwargs)


class type_error(runtime_error):
    """ Type Error """
    title = "Type Error"
    message_template = (RUNTIME_ERROR_MESSAGE_HEADER + "\n" +
                        "Type errors occur when you use an operator or "
                        "function on the wrong type of value. For example, "
                        "using `+` to add to a list (instead of `.append`), or "
                        "dividing a string by a number.\n\n"
                        "Suggestion: To fix a type error, you should trace "
                        "through your code. Make sure each expression has the "
                        "type you expect it to have.")


class name_error(runtime_error):
    """ Runtime NameError """
    title = "Name Error"
    message_template = (RUNTIME_ERROR_MESSAGE_HEADER + "\n" +
                        "A name error means you have used a variable that has "
                        "no value.  You may have a typo, so check the "
                        "spelling. Or, you may have forgotten to initialize a "
                        "variable.\n\n"
                        "Suggestion: Trace your code and make sure each "
                        "variable was set before it was read.")


class value_error(runtime_error):
    """ Runtime ValueError """
    title = "Value Error"
    message_template = (RUNTIME_ERROR_MESSAGE_HEADER + "\n" +
                        "A ValueError occurs when you pass the wrong type of "
                        "value to a function. For example, you try to convert "
                        "a string without numbers to an integer (like "
                        "`int('Five')`).\n\n"
                        "Suggestion: Read the error message to see which "
                        "function had the issue. Check what type the function "
                        "expects. Then trace your code to make sure you pass "
                        "in that type.")


class attribute_error(runtime_error):
    """ Runtime AttributeError """
    title = "Attribute Error"
    message_template = (RUNTIME_ERROR_MESSAGE_HEADER + "\n" +
                        "An AttributeError means you used an attribute or "
                        "method that does not exist. For example, you wrote "
                        "`text.delete()` even though there is no `delete` "
                        "method.\n\n"
                        "Suggestion: Make sure that you spelled the method or "
                        "attribute correctly. Then, trace your code to check "
                        "that the dot's left expression is the correct type.")


class index_error(runtime_error):
    """ Runtime IndexError """
    title = "Index Error"
    message_template = (RUNTIME_ERROR_MESSAGE_HEADER + "\n" +
                        "An IndexError means that you indexed past the end of "
                        "a string or a list.  For example, if you access index "
                        "5 in a list with 3 items.\n\n"
                        "Suggestion: Remember that the first position in a "
                        "list or string is 0. Often, you will be off by just "
                        "one index position, so check your math. Also, make "
                        "sure the list or string has the right value.")


class zero_division_error(runtime_error):
    """ Runtime ZeroDivisionError """
    title = "Division by Zero Error"
    message_template = (RUNTIME_ERROR_MESSAGE_HEADER + "\n" +
                        "A ZeroDivisionError means you divided by 0. The "
                        "denominator (the right side of a division expression) "
                        "cannot be 0.\n\n"
                        "Suggestion: Check that you are dividing by the "
                        "correct value. Or, you might need to add an `if` "
                        "statement to handle the zero case.")


class indentation_error(runtime_error):
    """ Syntax IndentationError """
    title = "Indentation Error"
    message_template = (RUNTIME_ERROR_MESSAGE_HEADER + "\n" +
                        "An IndentationError means you have not indented your "
                        "code correctly. You have too many or too few spaces.\n\n"
                        "Suggestion: Check the line number, and the lines "
                        "before and after. Check the body of each function "
                        "definition, `if` statement, and `for` loop. Remember, "
                        "all the statements INSIDE of a body have the same "
                        "indentation.")


class import_error(runtime_error):
    """ Runtime ImportError """
    title = "Import Error"
    message_template = (RUNTIME_ERROR_MESSAGE_HEADER + "\n" +
                        "An ImportError means you tried to import a module "
                        "that does not exist. You might have a typo or a file "
                        "might be in the wrong location.\n\n"
                        "Suggestion: Check the spelling and capitalization of "
                        "the module's name. If you are importing a file, then "
                        "check that it is in the correct folder.")


class io_error(runtime_error):
    """ Runtime IOError """
    title = "Input/Output Error"
    message_template = (RUNTIME_ERROR_MESSAGE_HEADER + "\n" +
                        "An IOError means you tried to open a file that was "
                        "not available.\n\n"
                        "Suggestion: Make sure that the file is in the "
                        "correct folder. Then, make sure you spelled the "
                        "filename correctly.")


class key_error(runtime_error):
    """ Runtime KeyError """
    title = "Key Error"
    message_template = (RUNTIME_ERROR_MESSAGE_HEADER + "\n" +
                        "A KeyError means you accessed a non-existent key in "
                        "a dictionary.\n\n"
                        "Suggestion: First, check that you spelled the key "
                        "correctly. Make sure the key has the right type and "
                        "value. Then, check that the dictionary actually has "
                        "that key.")


class memory_error(runtime_error):
    """ Runtime MemoryError """
    title = "Memory Error"
    message_template = (RUNTIME_ERROR_MESSAGE_HEADER + "\n" +
                        "A MemoryError means your program ran out of mental "
                        "space.\n\n"
                        "Suggestion: You might have an infinite loop. Or, you "
                        "might not be filtering your data enough.")


class timeout_error(runtime_error):
    """ Runtime TimeoutError """
    title = "Timeout Error"
    message_template = (RUNTIME_ERROR_MESSAGE_HEADER + "\n" +
                        "A TimeoutError means your program took too long to "
                        "run.\n\n"
                        "Suggestion: Check that you do not have an infinite "
                        "loop.")


EXCEPTION_FF_MAP = {
    TypeError: type_error,
    NameError: name_error,
    ValueError: value_error,
    AttributeError: attribute_error,
    IndexError: index_error,
    ZeroDivisionError: zero_division_error,
    IndentationError: indentation_error,
    ImportError: import_error,
    IOError: io_error,
    KeyError: key_error,
    MemoryError: memory_error,
    TimeoutError: timeout_error,
}
