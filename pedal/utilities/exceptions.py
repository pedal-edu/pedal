"""
Utilities for handling exceptions across all of Pedal.
"""

import traceback
import os
import sys

BuiltinKeyError = KeyError

_backup_stdout = sys.stdout


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
        for field in ['__cause__', '__traceback__', '__context__']:
            if hasattr(original, field):
                setattr(self, field, getattr(original, field))
            else:
                setattr(self, field, None)
        self.message = message

    def __str__(self):
        return self.message


def improve_builtin_exceptions(exception):
    """
    Modify the given builtin exception to have a better interface.
    Currently used to make KeyError look like other exceptions.

    Args:
        exception (Exception): The existing exception to modify.

    Returns:
        Exception: A new exception, or the original one unchanged.
    """
    if isinstance(exception, BuiltinKeyError):
        return KeyError(exception, "key not found")
    return exception


def get_exception_name(exception: Exception) -> str:
    """
    Gets the name of the exception (e.g., IndexError gives ``"IndexError"``).
    """
    return exception.__class__.__name__


def add_context_to_error(e, message):
    """

    Args:
        e:
        message:

    Returns:

    """
    if isinstance(e, BuiltinKeyError):
        new_args = repr(e.args[0]) + message
        e = KeyError(e, new_args)
        e.args = tuple([new_args])
    elif isinstance(e, OSError):
        # TODO: Investigate OSError, since they have so many args.
        #       Might be weird.
        e.args = tuple([e.args[0] + message])
        return e
    elif hasattr(e, 'args') and e.args:
        e.args = tuple([e.args[0] + message])
    return e


class FakeFrame:
    """ Simplistic hack to make fake StackFrames for SyntaxErrors """
    def __init__(self, name, filename, lineno, line):
        self.name = name
        self.filename = filename
        self.lineno = lineno
        self._line = line

    @property
    def line(self):
        return self._line

    def __eq__(self, other):
        try:
            return self.filename == other.filename and self.lineno == other.lineno
        except:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class ExpandedTraceback:
    """
    Class for reformatting tracebacks to have more pertinent information.
    """

    def __init__(self, exception, exc_info, full_traceback,
                 hide_filenames, line_offsets, show_filenames,
                 original_code_lines, student_files):
        """
        Args:
            exception (Exception): The exception that was raised.
            exc_info (ExcInfo): The result of sys.exc_info() when the exception
                was raised.
            full_traceback (bool): Whether or not to provide the full traceback
                or just the parts relevant to students.
        """
        self.line_offsets = line_offsets
        self.exception = exception
        self.exc_info = exc_info
        self.full_traceback = full_traceback
        self.hide_filenames = hide_filenames
        self.show_filenames = show_filenames
        self.line_number = traceback.extract_tb(exc_info[2])[-1][1]
        self.original_code_lines = original_code_lines
        self.student_files = student_files

    def build_traceback(self):
        """
        Filter out unnecessary frames
        """
        if not self.exception:
            return []
        cl, exc, tb = self.exc_info
        while tb and self._is_relevant_tb_level(tb):
            tb = tb.tb_next
        length = self._count_relevant_tb_levels(tb)
        tb_e = traceback.TracebackException(cl, self.exception, tb, limit=length,
                                            capture_locals=False)
        for frame in tb_e.stack:
            self._fix_frame_line(frame)
        frames = list(tb_e.stack)
        # A SyntaxError has to be handled differently to actually get its output:
        # https://docs.python.org/3/library/traceback.html#traceback.print_exception
        if isinstance(self.exception, SyntaxError):
            fake_frame = FakeFrame("<module>", self.exception.filename,
                                   self.exception.lineno, None)
            self._fix_frame_line(fake_frame)
            # Skulpt compatibility hack, to prevent duplicate tracebacks
            if not frames or fake_frame != frames[-1]:
                frames.append(fake_frame)
        return frames

    def _fix_frame_line(self, frame):
        if frame.filename in self.line_offsets:
            original_lineno = frame.lineno
            frame.lineno += self.line_offsets[frame.filename]
            if original_lineno - 1 < len(self.original_code_lines):
                frame._line = self.original_code_lines[original_lineno - 1]
            else:
                frame._line = "# *line missing*"
        else:
            # print(frame.filename, self.student_files, frame.lineno)
            if frame.filename in self.student_files:
                if frame.lineno - 1 < len(self.original_code_lines):
                    frame._line = self.student_files[frame.filename][frame.lineno - 1]
                else:
                    # Not actually possible in CPython, but Skulpt gives weird
                    #   SyntaxErrors that are technically the "next" line.
                    frame._line = ""

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
        # Is the error in the student file?
        if filename in self.show_filenames:
            return False
        # Is the error in the instructor file?
        if filename in self.hide_filenames:
            return True
        # Is the error in this test directory?
        current_directory = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        if filename.startswith(current_directory):
            return True
        # Is the error related to a file in the parent directory?
        # parent_directory = os.path.dirname(current_directory)
        # TODO: Currently we don't refer to this?
        # Is the error in a local file?
        if filename.startswith('.'):
            return False
        # Is the error in an absolute path?
        if not os.path.isabs(filename):
            return False
        # Okay, it's not a student related file
        return True

    def format_traceback(self, traceback_stack, formatter):
        """
        Turn a stack of tracebacks into a message.

        Args:
            traceback_stack (list[Frame]): The actual traceback to format into
                a message.
            formatter (:py:class:`pedal.core.formatters.Formatter`): The
                formatter to use to make the message.

        Returns:
            str: The text of the message.
        """
        traceback_message = "\n".join([
            (f"Line {formatter.line(frame.lineno)}"
             f" of file {formatter.filename(frame.filename)}" +
             (f" in {formatter.frame(frame.name)}\n"
              if frame.name != "<module>" and frame.name is not None
              else "\n") +
             f"{formatter.python_code(frame.line)}\n")
            for frame in traceback_stack
        ])
        return formatter.traceback(traceback_message)
