"""
A module that exposes a useful method (`timeout`) that can execute a
function asynchronously and terminiate if it exceeds a given `duration`.
"""

import sys
import time

try:
    import threading
except BaseException:
    threading = None
try:
    import ctypes
except BaseException:
    ctypes = None


class InterruptableThread(threading.Thread):
    '''
    A thread that can be interrupted.
    '''

    def __init__(self, func, args, kwargs):
        threading.Thread.__init__(self)
        self.func, self.args, self.kwargs = func, args, kwargs
        self.daemon = True
        self.result = None
        self.exc_info = (None, None, None)

    def run(self):
        '''
        Begin thread execution, calling the `func` that was originally
        passed in.
        '''
        try:
            self.result = self.func(*self.args, **self.kwargs)
        except Exception:
            self.exc_info = sys.exc_info()

    @staticmethod
    def _async_raise(thread_id, exception):
        '''
        Static method to raise an error asychronously using the ctypes module.
        '''
        # Cache the function for convenience
        RaiseAsyncException = ctypes.pythonapi.PyThreadState_SetAsyncExc

        states_modified = RaiseAsyncException(ctypes.c_long(thread_id),
                                              ctypes.py_object(exception))
        if states_modified == 0:
            raise ValueError("nonexistent thread id")
        elif states_modified > 1:
            RaiseAsyncException(thread_id, 0)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    def raise_exception(self, exception):
        '''
        Trigger a thread ending exception!
        '''
        assert self.isAlive(), "thread must be started"
        for thread_id, thread in threading._active.items():
            if thread is self:
                InterruptableThread._async_raise(thread_id, exception)
                return

    def terminate(self):
        self.raise_exception(SystemExit)


def timeout(duration, func, *args, **kwargs):
    """
    Executes a function and kills it (throwing an exception) if it runs for
    longer than the specified duration, in seconds.
    """

    # If libraries are not available, then we execute normally
    if None in (threading, ctypes):
        return func(*args, **kwargs)

    target_thread = InterruptableThread(func, args, kwargs)
    target_thread.start()
    target_thread.join(duration)

    if target_thread.isAlive():
        target_thread.terminate()
        raise TimeoutError('Your code took too long to run '
                           '(it was given {} seconds); '
                           'maybe you have an infinite loop?'.format(duration))
    else:
        if target_thread.exc_info[0] is not None:
            ei = target_thread.exc_info
            # Python 2 had the three-argument raise statement; thanks to PEP
            # 3109 for showing how to convert that to valid Python 3 statements.
            e = ei[0](ei[1])
            e.__traceback__ = ei[2]
            raise e


# =========================================================================


class _TimeoutData:
    """
    Port of Craig Estep's AdaptiveTimeout JUnit rule from the VTCS student
    library.
    """

    # -------------------------------------------------------------
    def __init__(self, ceiling):
        self.ceiling = ceiling  # sec
        self.maximum = ceiling * 2  # sec
        self.minimum = 0.25  # sec
        self.threshold = 0.6
        self.rampup = 1.4
        self.rampdown = 0.5
        self.start = self.end = 0
        self.non_terminating_methods = 0

    # -------------------------------------------------------------

    def before_test(self):
        """
        Call this before a test case runs in order to reset the timer.
        """
        self.start = time.time()

    # -------------------------------------------------------------

    def after_test(self):
        """
        Call this after a test case runs. This will examine how long it took
        the test to execute, and if it required an amount of time greater than
        the current ceiling, it will adaptively adjust the allowed time for
        the next test.
        """
        self.end = time.time()
        diff = self.end - self.start

        if diff > self.ceiling:
            self.non_terminating_methods += 1

        if self.non_terminating_methods >= 2:
            if self.ceiling * self.rampdown < self.minimum:
                self.ceiling = self.minimum
            else:
                self.ceiling = (self.ceiling * self.rampdown)
        elif diff > self.ceiling * self.threshold:
            if self.ceiling * self.rampup > self.maximum:
                self.ceiling = self.maximum
            else:
                self.ceiling = (self.ceiling * self.rampup)
