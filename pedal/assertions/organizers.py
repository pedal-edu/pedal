from pedal.report.imperative import MAIN_REPORT
from pedal.assertions.setup import _setup_assertions


def contextualize_calls():
    pass


def try_all():
    pass


class _finish_section:
    def __init__(self, number, *functions):
        if isinstance(number, int):
            self.number = number
        else:
            self.number = -1
            functions = [number] + list(functions)
        self.functions = functions
        for function in functions:
            self(function, False)

    def __call__(self, f=None, quiet=True):
        if f is not None:
            f()
        if quiet:
            print("\tNEXT SECTION")

    def __enter__(self):
        pass

    def __exit__(self, x, y, z):
        print("\tNEXT SECTION")
        # return wrapped_f


def finish_section(number, *functions, next_section=False):
    if len(functions) == 0:
        x = _finish_section(number, *functions)
        x()
    else:
        result = _finish_section(number, *functions)
        if next_section:
            print("\tNEXT SECTION")
        return result

def section(*args):
    '''
    '''
    _setup_assertions(MAIN_REPORT)
    def wrap(f):
        MAIN_REPORT['assertions']['functions'].append(f)
        return f
    section_number = -1
    if len(args) >= 1 and callable(args[0]):
        if len(args) >= 2:
            section_number = args[1]
        return wrap(args[0])
    elif len(args) >= 1:
        section_number = args[0]
    return wrap


def precondition(function):
    pass


def postcondition(function):
    pass
