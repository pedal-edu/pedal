"""
File containing errors throwable by Pedal.
"""

__all__ = ['PedalToolNotRegistered', 'PedalToolAlreadyRegistered']


class PedalToolNotRegistered(Exception):
    """ Raised when you reference a Tool that is not registered. """
    def __init__(self, missing_name, available_names):
        message = (f"The tool {missing_name!r} is not registered. "
                   f"Available tools are:\n{available_names!r}")
        super().__init__(message)


class PedalToolAlreadyRegistered(Exception):
    """ Raised when you register an already-existing tool. """
    def __init__(self, existing_name):
        message = f"The tool {existing_name!r} is already registered."
        super().__init__(message)
