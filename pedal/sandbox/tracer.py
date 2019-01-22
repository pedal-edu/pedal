import sys
import os

try:
    import coverage
except ImportError:
    coverage = None

try:
    from bdb import Bdb, BdbQuit
except ImportError:
    class Bdb:
        pass


    class BdbQuit:
        pass


class SandboxBasicTracer:
    def __init__(self):
        super().__init__()
        self.filename = "student.py"

    def _as_filename(self, filename, code):
        if os.path.isabs(filename):
            self.filename = filename
        else:
            self.filename = os.path.abspath(filename)
        self.code = code
        return self

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, traceback):
        pass


class SandboxCoverageTracer(SandboxBasicTracer):
    def __init__(self):
        super().__init__()
        if coverage is None:
            raise ImportError("The coverage package is not available.")
        self.n_missing = None
        self.n_statements = None
        self.pc_covered = None
        self.missing = set()
        self.lines = set()
        # self.s = sys.stdout

    def __enter__(self):
        # Force coverage to accept the code
        self.original = coverage.python.get_python_source

        def _get_source_correctly(reading_filename):
            print(reading_filename, file=self.s)
            if reading_filename == self.filename:
                return self.code
            else:
                return self.original(reading_filename)

        coverage.python.get_python_source = _get_source_correctly
        self.coverage = coverage.Coverage()
        self.coverage.start()

    def __exit__(self, exc_type, exc_val, traceback):
        self.coverage.stop()
        self.coverage.save()
        # Restore the get_python_source reader
        coverage.python.get_python_source = self.original
        self.original = None
        # Actually analyze the data, attach some data
        analysis = self.coverage._analyze(self.filename)
        # print(vars(self.coverage._analyze(self.filename)), file=self.s)
        self.n_missing = analysis.numbers.n_missing
        self.n_statements = analysis.numbers.n_statements
        self.pc_covered = analysis.numbers.pc_covered
        self.missing = analysis.missing
        self.lines = analysis.statements - analysis.missing
    
    @property
    def percent_covered(self):
        return self.pc_covered


class SandboxCallTracer(SandboxBasicTracer, Bdb):
    def __init__(self):
        super().__init__()
        self.calls = {}

    def user_call(self, frame, argument_list):
        code = frame.f_code
        name = code.co_name
        if name not in self.calls:
            self.calls[name] = []
        self.calls[name].append(code)

    def __enter__(self):
        self.reset()
        self._old_trace = sys.gettrace()
        sys.settrace(self.trace_dispatch)

    def __exit__(self, exc_type, exc_val, traceback):
        sys.settrace(self._old_trace)
        self.quitting = True
        # Return true to suppress exception (if it is a BdbQuit)
        return isinstance(exc_type, BdbQuit)
