"""
Mocked functions that can be used to prevent malicious or accidental `eval`
behavior.
"""
import re
import types

from pedal.sandbox.exceptions import (SandboxNoMoreInputsException,
                                      SandboxPreventModule)


def _disabled_compile(source, filename, mode, flags=0, dont_inherit=False):
    """
    A version of the built-in `compile` method that fails with a runtime
    error.
    """
    raise RuntimeError("You are not allowed to call 'compile'.")


def _disabled_eval(object, globals=globals(), locals=locals()):
    """
    A version of the built-in `eval` method that fails with a runtime
    error.
    """
    raise RuntimeError("You are not allowed to call 'eval'.")


# -------------------------------------------------------------


def _disabled_exec(object, globals=globals(), locals=locals()):
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
    if isinstance(__builtins__, types.ModuleType):
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


def _make_inputs(*input_list, **kwargs):
    """
    Helper function for creating mock user input.

    Params:
        input_list (list of str): The list of inputs to be returned
    Returns:
        function (str=>str): The mock input function that is returned, which
                             will return the next element of input_list each
                             time it is called.
    """
    if 'repeat' in kwargs:
        repeat = kwargs['repeat']
    else:
        repeat = None
    generator = iter(input_list)

    def mock_input(prompt=''):
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


_sys_modules = {}


def _override_builtins(namespace, custom_builtins):
    """
    Add the custom builtins to the `namespace` (and the original `__builtins__`)
    suitable for `exec`.
    """
    # Obtain the dictionary of built-in methods, which might not exist in
    # some python versions (e.g., Skulpt)

    # Create a shallow copy of the dictionary of built-in methods. Then,
    # we'll take specific ones that are unsafe and replace them.
    namespace["__builtins__"] = _default_builtins.copy()
    for name, function in custom_builtins.items():
        namespace["__builtins__"][name] = function


def create_module(module_name):
    submodule_names = module_name.split(".")
    modules = {}
    root = types.ModuleType(submodule_names[0])
    modules[submodule_names[0]] = root
    reconstructed_path = submodule_names[0]
    for submodule_name in submodule_names[1:]:
        reconstructed_path += "." + submodule_name
        new_submodule = types.ModuleType(reconstructed_path)
        setattr(root, submodule_name, new_submodule)
        modules[reconstructed_path] = new_submodule
    return root, modules


class MockModule:
    def _generate_patches(self):
        return {k: v for k, v in vars(self).items()
                if not k.startswith('_')}

    def _add_to_module(self, module):
        for name, value in self._generate_patches().items():
            setattr(module, name, value)


class BlockedModule(MockModule):
    MODULE_NAME = "this module"

    def _generate_patches(self):
        return {'__getattr__': self.prevent_module}

    def prevent_module(self, **kwargs):
        raise SandboxPreventModule("You cannot import {module_name} from student code.".format(
            module_name=self.MODULE_NAME
        ))


class MockPedal(BlockedModule):
    MODULE_NAME = "pedal"


class MockPlt(MockModule):
    """
    Mock MatPlotLib library that can be used to capture plot data.

    Attributes:
        plots (list of dict): The internal list of plot dictionaries.
    """

    def __init__(self):
        super().__init__()
        self._reset_plots()

    def show(self, **kwargs):
        self.plots.append(self.active_plot)
        self._reset_plot()

    def unshown_plots(self):
        return self.active_plot['data']

    def __repr__(self):
        return repr(self.plots)

    def __str__(self):
        return str(self.plots)

    def _reset_plots(self):
        self.plots = []
        self._reset_plot()

    def _reset_plot(self):
        self.active_plot = {'data': [],
                            'xlabel': None, 'ylabel': None,
                            'title': None, 'legend': False}

    def hist(self, data, **kwargs):
        label = kwargs.get('label', None)
        self.active_plot['data'].append({'type': 'hist', 'values': data,
                                         'label': label})

    def plot(self, xs, ys=None, **kwargs):
        label = kwargs.get('label', None)
        if ys is None:
            self.active_plot['data'].append({'type': 'line',
                                             'x': list(range(len(xs))),
                                             'y': xs, 'label': label})
        else:
            self.active_plot['data'].append({'type': 'line', 'x': xs,
                                             'y': ys, 'label': label})

    def scatter(self, xs, ys, **kwargs):
        label = kwargs.get('label', None)
        self.active_plot['data'].append({'type': 'scatter', 'x': xs,
                                         'y': ys, 'label': label})

    def xlabel(self, label, **kwargs):
        self.active_plot['xlabel'] = label

    def title(self, label, **kwargs):
        self.active_plot['title'] = label

    def suptitle(self, label, **kwargs):
        self.title(label, **kwargs)

    def ylabel(self, label, **kwargs):
        self.active_plot['ylabel'] = label

    def legend(self, **kwargs):
        self.active_plot['legend'] = True

    def _generate_patches(self):
        def dummy(**kwargs):
            pass

        return dict(hist=self.hist, plot=self.plot,
                    scatter=self.scatter, show=self.show,
                    xlabel=self.xlabel, ylabel=self.ylabel,
                    title=self.title, legend=self.legend,
                    xticks=dummy, yticks=dummy,
                    autoscale=dummy, axhline=dummy,
                    axhspan=dummy, axvline=dummy,
                    axvspan=dummy, clf=dummy,
                    cla=dummy, close=dummy,
                    figlegend=dummy, figimage=dummy,
                    suptitle=self.suptitle, text=dummy,
                    tick_params=dummy, ticklabel_format=dummy,
                    tight_layout=dummy, xkcd=dummy,
                    xlim=dummy, ylim=dummy,
                    xscale=dummy, yscale=dummy)
