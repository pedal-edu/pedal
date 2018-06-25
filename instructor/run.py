import ast

try:
    import threading
except Exception as e:
    threading = None

def _threaded_execution(code):
    pass

def _regular_execution(code):
    pass

def run(code, threaded=False):
    if threaded and threading is not None:
        return _threaded_execution(code)
    else:
        return _regular_execution(code)