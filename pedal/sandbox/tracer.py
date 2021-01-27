import sys
import os

from unittest.mock import patch

try:
    import coverage
except ImportError:
    coverage = None

try:
    from bdb import Bdb, BdbQuit
except Exception:
    class Bdb:
        pass


    class BdbQuit:
        pass

_stdout = sys.stdout


class SandboxBasicTracer:
    """

    """
    def __init__(self):
        super().__init__()
        self.filename = "student.py"
        self.code = None

    def as_filename(self, filename, code):
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
    """

    """
    def __init__(self):
        super().__init__()
        if coverage is None:
            raise ImportError("The coverage package is not available.")
        self.n_missing = None
        self.n_statements = None
        self.pc_covered = None
        self.missing = set()
        self.lines = set()

    def __enter__(self):
        # Force coverage to accept the code
        self.original = coverage.python.get_python_source

        def _get_source_correctly(reading_filename):
            if reading_filename == self.filename:
                return self.code
            else:
                return self.original(reading_filename)

        self.p = patch('coverage.python.get_python_source', _get_source_correctly)
        self.p.start()
        #coverage.python.get_python_source = _get_source_correctly
        self.coverage = coverage.Coverage()
        self.coverage.start()

    def __exit__(self, exc_type, exc_val, traceback):
        self.coverage.stop()
        self.coverage.save()
        # Restore the get_python_source reader
        #coverage.python.get_python_source = self.original
        # Actually analyze the data, attach some data
        analysis = self.coverage._analyze(self.filename)
        #print(vars(self.coverage._analyze(self.filename)), file=_stdout)
        self.n_missing = analysis.numbers.n_missing
        self.n_statements = analysis.numbers.n_statements
        self.pc_covered = analysis.numbers.pc_covered
        self.missing = analysis.missing
        self.lines = analysis.statements - analysis.missing

        self.p.stop()
        self.original = None

    
    @property
    def percent_covered(self):
        """

        Returns:

        """
        return self.pc_covered


class SandboxNativeTracer(SandboxBasicTracer):
    """
    Tracks lines covered and function calls. Possibly other things? We could track variables, if that
    was something people wanted.

    TODO: Handle multiple submission files?
    """
    def __init__(self):
        super().__init__()
        self.calls = {}
        self.lines = []
        self.old_tracer = None
        self.step_index = 1

    def __enter__(self):
        self.old_tracer = sys.gettrace()
        sys.settrace(self.tracer)

    def __exit__(self, exc_type, exc_val, traceback):
        sys.settrace(self.old_tracer)

    def is_tracked_file(self, frame):
        left = os.path.basename(frame.f_code.co_filename)
        right = os.path.basename(self.filename)
        return left == right

    def tracer(self, frame, event, args):
        if event == 'line' and self.is_tracked_file(frame):
            line = frame.f_lineno
            self.lines.append(line)
            self.step_index += 1
        if event == 'call' and self.is_tracked_file(frame):
            called_function = frame.f_code.co_name
            if called_function != '<module>':
                if called_function not in self.calls:
                    self.calls[called_function] = []
                arguments = {name: frame.f_locals[name] for name in frame.f_code.co_varnames
                             if name in frame.f_locals}
                self.calls[called_function].append(arguments)
        return self.tracer


class SandboxCallTracer(SandboxBasicTracer, Bdb):
    """

    """
    def __init__(self):
        super().__init__()
        self.calls = {}

    def user_call(self, frame, argument_list):
        """

        Args:
            frame:
            argument_list:
        """
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


TRACER_STYLES = {
    'coverage': SandboxCoverageTracer,
    'calls': SandboxCallTracer,
    'none': SandboxBasicTracer,
    'native': SandboxNativeTracer
}
