"""
The file containing the Substitution class.
"""


class Substitution:
    """
    A Substitution is a class that mocks part of the Submission class in order
    to pretend to be a different source code file. This allows Source to do a
    fancy bit of swapping around, making the code and filename appear to be
    different.
    """
    def __init__(self, code: str, filename: str):
        self.code = code
        self.filename = filename
        self.lines = code.split("\n")
