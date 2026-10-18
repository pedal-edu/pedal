"""
This module allows us to interfere with default importing and opening
behavior in Pedal's instructor control scripts.

Similar behavior is provided in the student namespace through pedal.sandbox.mocked
but on a more dramatic scale.
"""
from __future__ import annotations
import sys
from typing import Optional
import io
import types
from unittest.mock import patch

try:
    __builtins__
except NameError:
    _default_builtins = {'open': open,
                         '__import__': __import__}
else:
    if isinstance(__builtins__, types.ModuleType):
        _default_builtins = __builtins__.__dict__
    else:
        _default_builtins = __builtins__

ORIGINAL_BUILTINS = {
    'open': _default_builtins['open'],
    '__import__': _default_builtins['__import__']
}

def create_open_function(extra_files: dict[str, str]):
    def _patched_open(name, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True,
                         opener=None):
        if name in extra_files:
            if 'r' in mode:
                return io.StringIO(extra_files[name])
            else:
                raise IOError(f"File {name} is not available for writing.")
        else:
            return ORIGINAL_BUILTINS[name](name, mode, buffering, encoding, errors, newline, closefd, opener)

    return _patched_open

def create_import_function(extra_files: dict[str, str]):
    def _patched_import(module_name, globals=None, locals=None, fromlist=(), level=0):
        filename = module_name.replace(".", "/") + ".py"
        if filename in extra_files:
            module = types.ModuleType(module_name)
            exec(extra_files[filename], module.__dict__)
            return module
        return ORIGINAL_BUILTINS['__import__'](module_name, globals, locals, fromlist, level)

    return _patched_import

def make_instructor_data(extra_files: Optional[dict[str, str]] = None):
    if extra_files is None or not extra_files:
        return {}

    _patched_open = create_open_function(extra_files)
    _patched_import = create_import_function(extra_files)

    instructor_data = {"__builtins__": _default_builtins.copy()}
    instructor_data['__builtins__']['open'] = _patched_open
    instructor_data['__builtins__']['__import__'] = _patched_import

    return instructor_data

