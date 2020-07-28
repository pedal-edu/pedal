'''

**Sections** are a way to separate the pieces of a file such that the pieces do not
interfere with each other.

**Phases** are a way to chunk a collection of functions together. If one of these
functions fails, the other functions in the phase will continue to be evaluated.
However, that phase will still have failed. You can establish that one phase
comes before or after another phase; if a precondition phase fails, then the
subsequent phase will not run.

Example:
    Students are working on a text adventure game and have to implement a
    function named create_world(). The grading for portion of the assignment
    has three phases:
        'create_world_exists' which confirms that the function was defined
        'create_world_returns' which confirms that calling the function
            produces the right result.
        'create_world_complete' which confirms that the previous phase
            terminated in order to give some partial credit.
    
    Although the 'create_world_exists' phase is composed of one function, the
    'create_world_returns' phase is actually composed of several functions that
    check the components of the function.
    
    @phase('create_world_exists')
    
    @phase('create_world_returns', after='create_world_exists')
    
Phases are reset between sections.

**Subtests** are a way to combine multiple assertions into a single cohesive test.
TODO: Rename? And expand on.
with assert_group('test_add') as test_add_group:

if assert_unit_tests('function_name', FUNCTION_CASES):


'''


from pedal.core.report import MAIN_REPORT
from pedal.assertions.setup import (_setup_assertions, AssertionException,
                                    _add_relationships, _add_phase)
from functools import wraps


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
    """

    Args:
        number:
        *functions:
        next_section:

    Returns:

    """
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
    TODO: Deprecate?
    '''
    _setup_assertions(MAIN_REPORT)
    def wrap(f):
        """

        Args:
            f:

        Returns:

        """
        _add_phase(phase_name, _handle_entry)
        MAIN_REPORT['assertions']['phases'].append((section_number, f))
        return f
    section_number = -1
    if len(args) >= 1 and callable(args[0]):
        if len(args) >= 2:
            section_number = args[1]
        return wrap(args[0])
    elif len(args) >= 1:
        section_number = args[0]
    return wrap


def phase(phase_name, before=None, after=None):
    '''
    
    Args:
        phase_name (str): The name of the phase this function will belong to.
        before (list[str] or str): the name(s) of any phases that this phase
                                   should be before.
        after (list[str] or str): the name(s) of any phases that this phase
                                  should be after.
    '''
    _setup_assertions(MAIN_REPORT)
    def wrap(f):
        """

        Args:
            f:

        Returns:

        """
        @wraps(f)
        def _handle_entry(*args, **kwargs):
            old_exception_state = MAIN_REPORT['assertions']['exceptions']
            MAIN_REPORT['assertions']['exceptions'] = True
            value = f(*args, **kwargs)
            MAIN_REPORT['assertions']['exceptions'] = old_exception_state
            return value
        _add_phase(phase_name, _handle_entry)
        _add_relationships(phase_name, before)
        _add_relationships(after, phase_name)
        return _handle_entry
    return wrap


def stop_on_failure(f):
    """

    Args:
        f:

    Returns:

    """
    _setup_assertions(MAIN_REPORT)
    @wraps(f)
    def wrapped(*args, **kwargs):
        """

        Args:
            *args:
            **kwargs:

        Returns:

        """
        old_exception_state = MAIN_REPORT['assertions']['exceptions']
        MAIN_REPORT['assertions']['exceptions'] = True
        value = None
        try:
            value = f(*args, **kwargs)
        except AssertionException:
            pass
        MAIN_REPORT['assertions']['exceptions'] = old_exception_state
        return value
    return wrapped


def try_all(f):
    """

    Args:
        f:

    Returns:

    """
    _setup_assertions(MAIN_REPORT)
    @wraps(f)
    def wrapped(*args, **kwargs):
        """

        Args:
            *args:
            **kwargs:

        Returns:

        """
        old_exception_state = MAIN_REPORT['assertions']['exceptions']
        MAIN_REPORT['assertions']['exceptions'] = False
        value = f(*args, **kwargs)
        MAIN_REPORT['assertions']['exceptions'] = old_exception_state
        return value
    return wrapped


def precondition(function):
    """

    Args:
        function:
    """
    pass


def postcondition(function):
    """

    Args:
        function:
    """
    pass
