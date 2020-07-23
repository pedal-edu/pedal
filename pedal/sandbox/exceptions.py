"""
Exceptions related to Sandbox execution; note that these are not meant for
students, they indicate system errors.
"""


class SandboxException(Exception):
    """
    Generic base exception for sandbox errors.
    """


class SandboxStudentCodeException(SandboxException):
    """
    Caused by an error in student code
    """
    def __init__(self, actual):
        self.actual = actual


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
