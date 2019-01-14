class SandboxException(Exception):
    '''
    Generic base exception for sandbox errors.
    '''


class SandboxPreventModule(Exception):
    '''
    Caused by student attempting to load a module that they shouldn't.
    '''


class SandboxHasNoFunction(SandboxException):
    '''
    Caused by attempting to access a function that the student hasn't created.
    '''


class SandboxHasNoVariable(SandboxException):
    '''
    Caused by attempting to access a variable that the student hasn't created.
    '''


class SandboxNoMoreInputsException(Exception):
    '''
    Caused by the student calling `input` when the instructor hasn't provided
    enough inputs. Typically, the student has an infinite loop around their
    `input` function.
    '''
    
BuiltinKeyError = KeyError
class KeyError(BuiltinKeyError):
    '''
    A version of KeyError that replaces the built-in with one small
    modification: when printing an explanatory message, the message is not
    rendered as a tuple. Because that's stupid and the fact that it made it
    into CPython is just rude.
    
    See Also:
        https://github.com/python/cpython/blob/master/Objects/exceptions.c#L1556
    '''
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
    elif e.args:
        e.args = tuple([e.args[0] + message])
    return e

class SandboxTraceback:
    def __init__(self, exception, exc_info):
        self.exception = exception
        self.exc_info = exc_info
    
    def format_exception(self, _pre=""):
        if not self.exception:
            return ""
        cl, exc, tb = self.exc_info
        line_number = traceback.extract_tb(tb)[-1][1]
        while tb and self._is_relevant_tb_level(tb):
            tb = tb.tb_next
        length = self._count_relevant_tb_levels(tb)
        tb_e = traceback.TracebackException(cl, exc, tb,
                                            limit=length,
                                            capture_locals=False)
        lines = [x.replace(', in <module>', '', 1) for x in list(tb_e.format())]
        return _pre + "\nTraceback:\n" + ''.join(lines[1:])

    def _count_relevant_tb_levels(self, tb):
        length = 0
        while tb and not self._is_relevant_tb_level(tb):
            length += 1
            tb = tb.tb_next
        return length

    def _is_relevant_tb_level(self, tb):
        '''
        Determines if the give part of the traceback is relevant to the user.

        Returns:
            boolean: True means it is NOT relevant
        '''
        # Are in verbose mode?
        if self.full_traceback:
            return False
        filename, a_, b_, _ = traceback.extract_tb(tb, limit=1)[0]
        #print(filename, self.instructor_filename, __file__, a_, b_)
        # Is the error in this test file?
        if filename == __file__:
            return True
        if filename == self.instructor_filename:
            return True
        # Is the error related to a file in the parent directory?
        current_directory = os.path.dirname(os.path.realpath(__file__))
        parent_directory = os.path.dirname(current_directory)
        if filename.startswith(current_directory):
            return False
        # Is the error in a local file?
        if filename.startswith('.'):
            return False
        # Is the error in an absolute path?
        if not os.path.isabs(filename):
            return False
        # Okay, it's not a student related file
        return True