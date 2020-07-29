"""
Environments are a collection of defaults, setups, and overrides that make
Pedal adapt better to a given autograding platform (e.g., BlockPy, WebCAT,
GradeScope). They are meant to streamline common configuration.
"""

__all__ = ['Environment']


class Environment:
    """
    Abstract Environment class, meant to be subclassed by the environment to
    help simplify configuration. Technically doesn't need to do anything.
    """
