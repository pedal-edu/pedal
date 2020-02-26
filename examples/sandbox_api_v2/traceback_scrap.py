from pprint import pprint
import ast
import re
import types
import sys
import io
import os
from unittest.mock import patch, mock_open, MagicMock
import traceback

from pedal.core import MAIN_REPORT
from pedal.sandbox import mocked
from pedal.sandbox.timeout import timeout
from pedal.sandbox.messages import EXTENDED_ERROR_EXPLANATION
    
class Sandbox:
    '''
    '''
    
    # Hooks for pre/post execution. If set to be callable functions, they will
    # be executed before and after execution (regardless of its success)
    pre_execution = None
    post_execution = None
    instructor_filename = "instructor_tests.py"
    
    def start_coverage(self, code=None, filename=None):
        """

        Args:
            code:
            filename:

        Returns:

        """
        if code is None:
            code = self.report['source']['code']
        if filename is None:
            filename = self.report['source']['filename']
        import coverage
        self.mocked_modules['coverage'] = coverage
        original = coverage.python.get_python_source
        self._coverage_code = code
        dir_path = os.getcwd()
        self._coverage_file = os.path.join(dir_path, filename)
        def get_python_source(reading_filename):
            """

            Args:
                reading_filename:

            Returns:

            """
            if reading_filename == self._coverage_file:
                return code
            else:
                return original(reading_filename)
        coverage.python.get_python_source = get_python_source
        self.mocked_modules['coverage.python'] = coverage.python
        self.cov = coverage.Coverage()
        self.cov.start()
    
    def stop_coverage(self):
        """

        Returns:

        """
        self.cov.stop()
        self.cov.save()
        
        #from pprint import pprint
        #pprint(self.cov.data._lines[self._coverage_file])
        #pprint(self.cov.data.line_counts(self._coverage_file))
        
        return self.cov.report()
        #print(self.cov.report())
    
    
        
    
    
    
    
    def check_code(self, code):
        """

        Args:
            code:

        Returns:

        """
        self.run(code, _as_filename=self.instructor_filename)
        if self.exception is not None:
            name = str(self.exception.__class__)[8:-2]
            self.report.attach(name, category='Runtime', tool='Sandbox',
                               section=self.report['source']['section'],
                               mistakes={'message': self.format_exception(), 
                                         'error': self.exception})
            return False, ""
        self.report.attach("Unit Test Failure", category='Runtime',
                           tool='Sandbox',
                           section=self.report['source']['section'],
                           mistakes={'message': defns+message})
    
    def tests(self, function, test_runs, points, compliment, test_output=False, defns=""):
        """

        Args:
            function:
            test_runs:
            points:
            compliment:
            test_output:
            defns:

        Returns:

        """
        all_passed = True
        results = []
        for test in test_runs:
            if isinstance(test, tuple):
                args = test[0]
                if len(test) > 1:
                    kwargs = {}
            else:
                args, kwargs = test, {}
            if test_output:
                kwargs['_test_output'] = test_output
            if defns is not None:
                kwargs['_pre'] = defns
            result = self.test(function, *args, **kwargs)
            all_passed = all_passed and result[0]
            results.append(result)
        if all_passed:
            if compliment is not None:
                self.report.compliment(compliment)
                self.report.give_partial(points)
            return True
        else:
            for passed, message in results:
                if passed:
                    self.report.attach("Unit Test Passing", category='Runtime',
                                       priority='positive', tool='Sandbox',
                                       section=self.report['source']['section'],
                                       mistakes={'message': message})
                else:
                    self.report.attach("Unit Test Failure", category='Runtime',
                                       tool='Sandbox',
                                       section=self.report['source']['section'],
                                       mistakes={'message': message})
            return False
    
    def test(self, function, expected, *args, **kwargs):
        """

        Args:
            function:
            expected:
            *args:
            **kwargs:

        Returns:

        """
        if function not in self.data and '.' not in function:
            # TODO: Hackish, allow methods through for now
            message = "I could not find a top-level definition of {function}!\n"
            message = message.format(function=function)
            self.report.attach("Function not found", category='Runtime', 
                               tool='Sandbox',
                               section=self.report['source']['section'],
                               mistakes={'message': message})
            return False, message
        _delta = kwargs.pop('_delta', 0.001)
        _exact_strings = kwargs.pop('_exact_strings', False)
        _hidden = kwargs.pop('_hidden', False)
        _test_output = kwargs.pop('_test_output', False)
        _pre = kwargs.pop('_pre', '')
        self.set_output(None)
        actual = self.call(function, *args, **kwargs,
                           _as_filename=self.instructor_filename)
        if self.exception is not None:
            name = str(self.exception.__class__)[8:-2]
            self.report.attach(name, category='Runtime', tool='Sandbox',
                               section=self.report['source']['section'],
                               mistakes={'message': self.format_exception(_pre), 
                                         'error': self.exception})
            return False, ""
        if _test_output:
            actual = self.output
            actual_str = "\n".join(actual)
            if isinstance(expected, list):
                expected_str = "\n".join(expected)
            else:
                expected_str = str(expected)
        else:
            actual_str = repr(actual)
            expected_str = repr(expected)
        message = None
        if equality_test(actual, expected, _exact_strings, _delta, _test_output):
            if not _hidden:
                message = "Unit test passed:\n"
                message += "<pre>{}</pre>\n".format(_pre) if _pre else ""
                message += "<pre>>{example}</pre>\n".format(example=self.example)
                message += "<pre>"+actual_str+"</pre>\n"
            return True, message
        if not _hidden:
            message = "Instructor unit test failure!\n"
            message += "\nBefore anything else, I ran:<pre>>{}</pre>\n".format(_pre) if _pre else ""
            message += "I ran:\n<pre>>{example}</pre>\n".format(example=self.example)
            message += "I got:\n<pre>"+actual_str+"</pre>\n"
            message += (("But I expected{p}:\n<pre>"+expected_str+"</pre>\n")
                        .format(p=" it to print" if _test_output else ""))
        else:
            message = "Hidden instructor unit test failure!\n"
        return False, message
    
    def raise_any_exceptions(self):
        """

        """
        if self.exception is not None:
            name = str(self.exception.__class__)[8:-2]
            self.report.attach(name, category='Runtime', tool='Sandbox',
                               section=self.report['source']['section'],
                               mistakes={'message': self.format_exception(), 
                                         'error': self.exception})

        
class _KeyError(KeyError):
    def __str__(self):
        return BaseException.__str__(self)
        
def _append_to_error(e, message):
    if e.args:
        e.args = (e.args[0]+message,)
    return e
        
def _raise_improved_error(e, code):
    if isinstance(e, KeyError):
        return _copy_key_error(e, code)
    else:
        return _append_to_error(e, code)

def _copy_key_error(e, code):
    new_args = (repr(e.args[0])+code,)
    new_except = _KeyError(*new_args)
    new_except.__cause__ = e.__cause__
    new_except.__traceback__ = e.__traceback__
    new_except.__context__  = e.__context__ 
    return new_except
    
    


if __name__ == "__main__":
    code = """
import matplotlib.pyplot as plt
print(plt.secret)
"""
    (student_locals, output) = run(code)
    for name, value in student_locals.items():
        if name == "__builtins__":
            print(name, ":", "Many things:", len(value))
        else:
            print(name, ":", value)
    