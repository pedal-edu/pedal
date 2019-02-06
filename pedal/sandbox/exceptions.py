import traceback
import os
import sys

class SandboxException(Exception):
    """
    Generic base exception for sandbox errors.
    """


class SandboxPreventModule(Exception):
    """
    Caused by student attempting to load a module that they shouldn't.
    """


class SandboxHasNoFunction(SandboxException):
    """
    Caused by attempting to access a function that the student hasn't created.
    """


class SandboxHasNoVariable(SandboxException):
    """
    Caused by attempting to access a variable that the student hasn't created.
    """


class SandboxNoMoreInputsException(Exception):
    """
    Caused by the student calling `input` when the instructor hasn't provided
    enough inputs. Typically, the student has an infinite loop around their
    `input` function.
    """


BuiltinKeyError = KeyError


class KeyError(BuiltinKeyError):
    """
    A version of KeyError that replaces the built-in with one small
    modification: when printing an explanatory message, the message is not
    rendered as a tuple. Because that's stupid and the fact that it made it
    into CPython is just rude.
    
    See Also:
        https://github.com/python/cpython/blob/master/Objects/exceptions.c#L1556
    """
    __module__ = "builtins"

    def __init__(self, original, message):
        self.__cause__ = original.__cause__
        self.__traceback__ = original.__traceback__
        self.__context__ = original.__context__
        self.message = message

    def __str__(self):
        return self.message


def _add_context_to_error(e, message):
    if isinstance(e, BuiltinKeyError):
        new_args = repr(e.args[0]) + message
        e = KeyError(e, new_args)
    if isinstance(e, OSError):
        # TODO: Can't seem to modify the OSError, since they have so many args.
        return e
    elif e.args:
        e.args = tuple([e.args[0] + message])
    return e
x=sys.stdout
class SandboxTraceback:
    """
    Class for reformatting tracebacks to have more pertinent information.
    """

    def __init__(self, exception, exc_info, full_traceback,
                 instructor_filename, line_offset, student_filename):
        """
        Args:
            exception (Exception): The exception that was raised.
            exc_info (ExcInfo): The result of sys.exc_info() when the exception
                was raised.
            full_traceback (bool): Whether or not to provide the full traceback
                or just the parts relevant to students.
            instructor_filename (str): The name of the instructor file, which
                can be used to avoid reporting instructor code in the
                traceback.
        """
        self.line_offset = line_offset
        self.exception = exception
        self.exc_info = exc_info
        self.full_traceback = full_traceback
        self.instructor_filename = instructor_filename
        self.student_filename = student_filename
        self.line_number = traceback.extract_tb(exc_info[2])[-1][1]

    def _clean_traceback_line(self, line):
        return line.replace(', in <module>', '', 1)

    def format_exception(self, preamble=""):
        if not self.exception:
            return ""
        cl, exc, tb = self.exc_info
        while tb and self._is_relevant_tb_level(tb):
            tb = tb.tb_next
        length = self._count_relevant_tb_levels(tb)
        tb_e = traceback.TracebackException(cl, exc, tb, limit=length,
                                            capture_locals=False)
        #print(list(), file=x)
        for frame in tb_e.stack:
            #print(frame, file=x)
            if frame.filename == self.student_filename:
                #frame.lineno += self.line_number
                frame.lineno += self.line_offset
        lines = [self._clean_traceback_line(line)
                 for line in tb_e.format()]
        lines[0] = "Traceback:\n"
        return preamble + ''.join(lines)

    def _count_relevant_tb_levels(self, tb):
        length = 0
        while tb and not self._is_relevant_tb_level(tb):
            length += 1
            tb = tb.tb_next
        return length

    def _is_relevant_tb_level(self, tb):
        """
        Determines if the give part of the traceback is relevant to the user.

        Returns:
            boolean: True means it is NOT relevant
        """
        # Are in verbose mode?
        if self.full_traceback:
            return False
        filename, a_, b_, _ = traceback.extract_tb(tb, limit=1)[0]
        # Is the error in the instructor file?
        if filename == self.instructor_filename:
            return True
        # Is the error in this test directory?
        current_directory = os.path.dirname(os.path.realpath(__file__))
        if filename.startswith(current_directory):
            return True
        # Is the error related to a file in the parent directory?
        parent_directory = os.path.dirname(current_directory)
        # Currently we don't refer to this?
        # Is the error in a local file?
        if filename.startswith('.'):
            return False
        # Is the error in an absolute path?
        if not os.path.isabs(filename):
            return False
        # Okay, it's not a student related file
        return True
