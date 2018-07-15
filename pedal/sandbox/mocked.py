'''
Mocked functions that can be used to prevent malicious or accidental `eval`
behavior.
'''
import re
import types

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
    
try:
    __builtins__
except NameError:
    _default_builtins = {'globals': globals,
                        'locals': locals,
                        'open': open,
                        'input': input}
else:
    if type(__builtins__) is types.ModuleType:
        _default_builtins = __builtins__.__dict__
    else:
        _default_builtins = __builtins__

_original_builtins = {
    'globals': _default_builtins['globals'],
    'locals': _default_builtins['locals'],
    'open': _default_builtins['open'],
    'input': _default_builtins['input'],
    'exec': _default_builtins.get('exec', _disabled_exec),
    'eval': _default_builtins.get('eval', _disabled_eval),
    'compile': _default_builtins.get('compile', _disabled_compile),
}

_sys_modules = {}

def _override_builtins(namespace, custom_builtins):
    '''
    Add the custom builtins to the `namespace` (and the original `__builtins__`)
    suitable for `exec`.
    '''
    # Obtain the dictionary of built-in methods, which might not exist in
    # some python versions (e.g., Skulpt)

    # Create a shallow copy of the dictionary of built-in methods. Then,
    # we'll take specific ones that are unsafe and replace them.
    namespace["__builtins__"] = _default_builtins.copy()
    for name, function in custom_builtins.items():
        namespace["__builtins__"][name] = function
