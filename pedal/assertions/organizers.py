
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

def section(number):
    '''
    '''
    pass


def precondition(function):
    pass


def postcondition(function):
    pass
