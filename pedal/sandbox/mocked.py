"""
Mocked functions that can be used to prevent malicious or accidental `eval`
behavior.
"""
import re
import sys
import types
from io import StringIO

from pedal.core.report import Report
from pedal.sandbox.exceptions import (SandboxNoMoreInputsException,
                                      SandboxPreventModule)
from pedal.utilities.system import IS_PYTHON_36


def do_nothing(*args, **kwargs):
    """ A function that does absolutely nothing. """


def _disabled_compile(source, filename, mode, flags=0, dont_inherit=False):
    """
    A version of the built-in `compile` method that fails with a runtime
    error.
    """
    raise RuntimeError("You are not allowed to call 'compile'.")


def _disabled_eval(object, globals=globals(), locals=None):
    """
    A version of the built-in `eval` method that fails with a runtime
    error.
    """
    raise RuntimeError("You are not allowed to call 'eval'.")


# -------------------------------------------------------------


def _disabled_exec(object, globals=globals(), locals=None):
    """
    A version of the built-in `exec` method that fails with a runtime
    error.
    """
    raise RuntimeError("You are not allowed to call 'exec'.")


# -------------------------------------------------------------


def _disabled_globals():
    """
    A version of the built-in `globals` method that fails with a runtime
    error.
    """
    raise RuntimeError("You are not allowed to call 'globals'.")


class FunctionNotAllowed(Exception):
    """ Exception created when a function that is not allowed is used. """


def disabled_builtin(name):
    """

    Args:
        name:

    Returns:

    """
    def _disabled_version(*args, **kwargs):
        raise FunctionNotAllowed("You are not allowed to call '{}'.".format(name))
    return _disabled_version


# TODO: This needs to be a field in the Sandbox object's data
_OPEN_FORBIDDEN_NAMES = re.compile(r"(^[./])|(\.py$)")
_OPEN_FORBIDDEN_MODES = re.compile(r"[wa+]")

# TODO: Allow the user to give a function instead of a REGEX
# TODO: We need to mock the whole OS library, honestly, not just `open`
def create_open_function(report: Report, forbidden_names=_OPEN_FORBIDDEN_NAMES, forbidden_modes=_OPEN_FORBIDDEN_MODES):
    """
    Creates a new version of the `open` built-in that will avoid looking at certain filenames,
    and will also respect the given Report's Submission's Files.

    Args:
        report:

    Returns:

    """
    def _restricted_open(name, mode='r', buffering=-1):
        if forbidden_names.search(name):
            raise RuntimeError("The filename you passed to 'open' is restricted.")
        elif forbidden_modes.search(mode):
            raise RuntimeError("You are not allowed to 'open' files for writing.")
        elif report.submission and name in report.submission.files:
            return StringIO(report.submission.files[name])
        else:
            return ORIGINAL_BUILTINS['open'](name, mode, buffering)
    return _restricted_open

# TODO: Allow this to be flexible


def create_import_function(report: Report, sandbox):
    """
    Creates a new version of the `__import__` function (which is used by the import keyword)
    that will not let students import Pedal or its submodules.

    Args:
        report:

    Returns:

    """
    def _restricted_import(module_name, globals=None, locals=None, fromlist=(), level=0):
        filename = module_name.replace(".", "/")+".py"
        if module_name == 'pedal' or module_name.startswith('pedal.'):
            raise RuntimeError("You cannot import pedal!")
        elif report.submission and filename in report.submission.files:
            if module_name not in sys.modules:
                contents = report.submission.files[filename]
                return sandbox._import(contents, module_name, filename, sandbox.threaded)
        return ORIGINAL_BUILTINS['__import__'](module_name, globals, locals, fromlist, level)
    return _restricted_import


try:
    __builtins__
except NameError:
    _default_builtins = {'globals': globals,
                         'locals': locals,
                         'open': open,
                         'input': input,
                         '__import__': __import__}
else:
    if isinstance(__builtins__, types.ModuleType):
        _default_builtins = __builtins__.__dict__
    else:
        _default_builtins = __builtins__

ORIGINAL_BUILTINS = {
    'globals': _default_builtins['globals'],
    'locals': _default_builtins['locals'],
    'open': _default_builtins['open'],
    'input': _default_builtins['input'],
    'print': _default_builtins.get('print'),
    'exec': _default_builtins.get('exec', _disabled_exec),
    'eval': _default_builtins.get('eval', _disabled_eval),
    'compile': _default_builtins.get('compile', _disabled_compile),
    'exit': disabled_builtin('exit'),
    '__import__': _default_builtins['__import__']
}


def make_inputs(input_list, repeat=None):
    """
    Helper function for creating mock user input.

    Params:
        input_list (list of str): The list of inputs to be returned
    Returns:
        function (str=>str): The mock input function that is returned, which
                             will return the next element of input_list each
                             time it is called.
    """
    generator = iter(input_list)

    def mock_input(prompt=''):
        """

        Args:
            prompt:

        Returns:

        """
        print(prompt)
        try:
            return next(generator)
        except StopIteration as SI:
            if repeat is None:
                # TODO: Make this a custom exception
                raise SandboxNoMoreInputsException("User had no more input to give.")
            else:
                return repeat

    return mock_input


class PrintingStringIO(StringIO):
    _ORIGINAL_STDOUT = sys.stdout

    def __init__(self, stdout=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_stdout = self._ORIGINAL_STDOUT if stdout is None else stdout

    def write(self, s):
        self._original_stdout.write(s)
        return super().write(s)

    def flush(self):
        self._original_stdout.flush()
        return super().flush()

    def writelines(self, lines):
        self._original_stdout.writelines(lines)
        return super().writelines(lines)


def make_fake_output(also_print=False) -> StringIO:
    """
    Creates a fake output stream that can be used to capture the output
    of a function. This is useful for testing functions that print things.

    Args:
        also_print (bool): Whether to also print the output to the console.

    Returns:
        StringIO: The fake output stream.
    """
    fake_output = StringIO()


    return fake_output


def create_module(module_names):
    """
    Creates empty ModuleTypes based on the ``module_name``. Correctly
    creates parent modules for submodules as needed to fill in the path.

    Args:
        module_name: A dot-separated string of modules, as if for ``import``. A list of
            names can also be passed in instead. If multiple names are given, they should all have the same root!

    Returns:
        :py:class:`types.ModuleType`: The root module created.
        dict[str, :py:class:`types.ModuleType`]: A dictionary of newly created
            modules, including the root and the actual target.
        :py:class:`types.ModuleType`: The target module created.
    """
    if isinstance(module_names, str):
        module_names = [module_names]
    if not module_names:
        raise ValueError("No modules provided; need at least one module to create!")
    root = None
    modules = {}
    for module_name in module_names:
        submodule_names = module_name.split(".")
        if root is None:
            root = types.ModuleType(submodule_names[0])
        modules[submodule_names[0]] = root
        reconstructed_path = submodule_names[0]
        for submodule_name in submodule_names[1:]:
            reconstructed_path += "." + submodule_name
            new_submodule = types.ModuleType(reconstructed_path)
            setattr(root, submodule_name, new_submodule)
            modules[reconstructed_path] = new_submodule
    return root, modules, modules[module_names[0]]


class MockModule:
    SUBMODULES = {}

    def _generate_patches(self):
        return {k: v for k, v in vars(self).items()
                if not k.startswith('_')}

    def add_to_module(self, main_module, submodules=None):
        for name, value in self._generate_patches().items():
            setattr(main_module, name, value)
        for submodule_name in self.SUBMODULES:
            property_name = submodule_name.split('.', maxsplit=1)[1]
            mock_submodule = getattr(main_module, property_name)
            # the actual created Module object
            submodule = submodules[submodule_name]
            # Populate the actual module object with the fake submodule's data
            mock_submodule.add_to_module(submodule)
            # Update the main module to point to the actual module, instead of the fake submodule
            setattr(main_module, property_name, submodule)


class MockDictModule(MockModule):
    def __init__(self, fields):
        self.fields = fields

    def _generate_patches(self):
        return self.fields


class BlockedModule(MockModule):
    def __init__(self, name):
        self.module_name = name

    def _generate_patches(self):
        return {'__getattr__': self.getter}

    def getter(self, key):
        """ If anything asks, we prevent the module. Except for __file__. """
        # Needed to support coverage - it's okay to ask who I am.
        if key == '__file__':
            return self.module_name
        else:
            self.prevent_module()

    def prevent_module(self, *args, **kwargs):
        """

        Args:
            **kwargs:
        """
        raise SandboxPreventModule(f"You cannot import `{self.module_name}` from student code.")


class MockPedal(BlockedModule):
    """ TODO: Deprecated? """
    module_name = "pedal"


from pedal.sandbox.library import *

