
__all__ = ['Submission']


class Submission:
    """
    Simple class for holding information about the student's submission.

    Examples:
        A very simple example of creating a Submission with a single file::

            >>> Submission([{'answer.py': "a = 0"}]

    Attributes:
        files (`dict` mapping `str` to `str`): Dictionary of filenames mapped to their contents, emulating
            a file system.
        main_file (str): The entry point file that will be considered the main file.

        user (Any): Additional information about the user.
        assignment (Any): Additional information about the assignment.
        course (Any): Additional information about the course.
    """

    def __init__(self, files=None, main_file='answer.py', user=None, assignment=None, course=None):
        self.files = files
        self.main_file = main_file
        self.user = user
        self.assignment = assignment
        self.course = course
