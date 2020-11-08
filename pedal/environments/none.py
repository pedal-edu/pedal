"""
A completely barebones environment that loads nothing.
"""

from pedal.core.environment import Environment


class NoneEnvironment(Environment):
    """
    The NoneEnvironment is an environment that does pretty much nothing.
    It actually just subclasses the abstract Environment without extending
    any behavior.
    """

setup_environment = NoneEnvironment
