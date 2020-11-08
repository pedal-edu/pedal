"""
Representation of a student's submission to pedal. Almost certainly contains their code,
but may also contain other metadata.


TODO: Normalize the concept of evaluations ("<stdin>" or "evaluations").
get_program(filename='<stdin>') => submission.files['<stdin>']
get_evaluation()

"""

__all__ = ['Submission']


class Submission:
    """
    Simple class for holding information about the student's submission.

    Examples:
        A very simple example of creating a Submission with a single file::

            >>> Submission({'answer.py': "a = 0"})

    Attributes:
        files (`dict` mapping `str` to `str`): Dictionary of filenames mapped to their contents, emulating
            a file system.
        main_file (str): The entry point file that will be considered the main file.
        main_code (str): The actual code to run; if None, then defaults to the code of the main file.
            Useful for tools that want to change the currently active code (e.g., Source's sections) or
            run additional commands (e.g., Sandboxes' call).
        user (dict): Additional information about the user.
        assignment (dict): Additional information about the assignment.
        course (dict): Additional information about the course.
        execution (dict): Additional information about the results of executing the students' code.
    """

    def __init__(self, files=None, main_file='answer.py', main_code=None,
                 user=None, assignment=None, course=None, execution=None,
                 instructor_file='instructor_tests.py', load_error=None):
        if files is None:
            files = {}
        self.files = files
        self.main_file = main_file
        self.load_error = load_error
        if main_code is not None:
            self.main_code = main_code
        if self.main_file not in self.files:
            self.files[self.main_file] = self.main_code or ""
        self._original_main_code = self.main_code
        self.user = user
        self.assignment = assignment
        self.course = course
        self.execution = execution
        self.instructor_file = instructor_file
        self.line_offsets = {}
        self._lines_cache = {}

    def get_lines(self, filename=None):
        """
        Retrieves the lines of code from this submission.

        Returns:
            list[str]: The lines of code for this submission.
        """
        if filename is None:
            code = self.main_code
        else:
            code = self.files[filename]
        if code not in self._lines_cache:
            self._lines_cache[code] = code.split("\n")
        return self._lines_cache[code]

    def get_files_lines(self):
        """ Retrieves a dictionary of lists of strings representing the files'
        lines of code. """
        return {filename: self.get_lines(filename) for filename in self.files}

    def replace_main(self, code: str, file: str = None):
        """
        Substitutes the current main code and filename with the given arguments.
        Args:
            code (str): The new code to substitute in.
            file (str): An optional filename to use.
        """
        self.main_code = code
        if file is not None:
            self.main_file = file
        self.files[self.main_file] = code

    @property
    def main_code(self):
        return self.files.get(self.main_file, "")

    @main_code.setter
    def main_code(self, code):
        self.files[self.main_file] = code

    def set_line_offset(self, lineno, filename=None):
        """ Sets the line offset for the given filename. Defaults to main
        file."""
        if filename is None:
            filename = self.main_file
        self.line_offsets[filename] = lineno

    def clear_line_offsets(self):
        self.line_offsets.clear()

    def to_json(self):
        return dict(
            user=self.user,
            assignment=self.assignment,
            course=self.course,
            execution=self.execution,
            files=self.files.copy()
        )