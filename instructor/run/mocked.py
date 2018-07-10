'''
Mocked functions that can be used to prevent malicious or accidental `eval`
behavior.
'''
import re
import types

_original_builtins = {}

def _disabled_compile(source, filename, mode, flags=0, dont_inherit=False):
    '''
    A version of the built-in `compile` method that fails with a runtime
    error.
    '''
    raise RuntimeError("You are not allowed to call 'compile'.")

def _disabled_eval(object, globals=globals(), locals=locals()):
    '''
    A version of the built-in `eval` method that fails with a runtime
    error.
    '''
    raise RuntimeError("You are not allowed to call 'eval'.")

# -------------------------------------------------------------
def _disabled_exec(object, globals=globals(), locals=locals()):
    '''
    A version of the built-in `exec` method that fails with a runtime
    error.
    '''
    raise RuntimeError("You are not allowed to call 'exec'.")

# -------------------------------------------------------------
def _disabled_globals():
    '''
    A version of the built-in `globals` method that fails with a runtime
    error.
    '''
    raise RuntimeError("You are not allowed to call 'globals'.")

_OPEN_FORBIDDEN_NAMES = re.compile(r"(^[./])|(\.py$)")
_OPEN_FORBIDDEN_MODES = re.compile(r"[wa+]")
def _restricted_open(name, mode='r', buffering=-1):
    if _OPEN_FORBIDDEN_NAMES.search(name):
        raise RuntimeError("The filename you passed to 'open' is restricted.")
    elif _OPEN_FORBIDDEN_MODES.search(mode):
        raise RuntimeError("You are not allowed to 'open' files for writing.")
    else:
        return _original_builtins['open'](name, mode, buffering)

_sys_modules = {}

