"""
Environments are a collection of defaults, setups, and overrides that make
Pedal adapt better to a given autograding platform (e.g., BlockPy, WebCAT,
GradeScope). They are meant to streamline common configuration.
"""

__all__ = ['Environment']

from pedal.core.report import MAIN_REPORT
from pedal.core.submission import Submission


class Environment:
    """
    Abstract Environment class, meant to be subclassed by the environment to
    help simplify configuration. Technically doesn't need to do anything.
    Creating an instance of an environment will automatically clear out the
    existing contents of the report.

    Args:
        main_file (str): The filename of the main file.
        main_code (str): The actual code of the main file.
        files (dict[str, str]): A list of filenames mapped to their contents.
    """
    def __init__(self, files=None, main_file='answer.py', main_code=None,
                 user=None, assignment=None, course=None, execution=None,
                 instructor_file='instructor.py', report=MAIN_REPORT):
        self.report = report
        report.clear()
        # Setup any code given as the submission.
        if isinstance(files, Submission):
            self.submission = files
        else:
            load_error = None
            if files is None:
                if main_code is None:
                    if main_file is None:
                        raise ValueError("files, main_code, and main_file cannot all be None.")
                    else:
                        main_code = self.load_main(main_file)
                        if isinstance(main_code, Exception):
                            load_error = main_code
                            main_code = ""
                files = {main_file: main_code}
            else:
                if main_file is not None:
                    if main_code is None:
                        main_code = files[main_file]
                    if main_file not in files:
                        files[main_file] = main_code
            self.submission = Submission(files, main_file, main_code,
                                         user, assignment, course, execution,
                                         instructor_file, load_error=load_error)
        # Contextualize report
        self.report.contextualize(self.submission)
        self.fields = {}

    def load_main(self, main_file):
        with open(main_file) as opened:
            return opened.read()

    def __iter__(self):
        return self.fields.items()

    def __getattr__(self, key):
        try:
            return self.fields[key]
        except KeyError:
            raise AttributeError(key)
