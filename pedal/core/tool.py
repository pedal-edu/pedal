"""
Tools are effectively submodules within Pedal - notable exceptions are
:py:mod:`pedal.core`, :py:mod:`pedal.environments`,
:py:mod:`pedal.utilities`, and :py:mod:`pedal.resolvers`.

All Tools with any kind of state are expected to have a `reset` function.
Although this can take parameters, we recommend avoiding that. The `reset`
should be for putting things back into a "null" state, and then you could have
followup functions that also give initial state.

Tools should avoid removing their references (i.e., clear out data from lists
and dictionaries instead of assigning a new one).

Tools should define a ``constants.py`` file with any useful constants. One of
these should be ``TOOL_NAME``, a string value indicating their desired namespace
(e.g., ``TOOL_NAME = "source"``).

Tools should define a ``feedbacks.py`` module that centralizes
:term:`Feedback Functions<Feedback Function>` for that tool.

Any function that interacts with Reports should expose a ``report`` parameter
that defaults to :py:data:`pedal.core.report.MAIN_REPORT`. All internal
functions should respect the ``report`` that was passed in, and not assume the
``MAIN_REPORT``.

Tools are allowed to store state within their namespace of a
:py:class:`pedal.core.report.Report`.
If the tool has not yet been initialized, its `reset` function will be called.
You can update and access fields via dictionary access.

.. code-block:: python

    report[TOOL_NAME]['my field'] = False

The ``__init__.py`` file for a Tool should use  ``__all__`` to expose any
interesting teacher-level functions, classes, and data. That way, teachers can
just consistently use ``from pedal.tool import *`` to instantly gain access to
the interesting set of members. The big exception to this is
:ref:`toolkit`, which is full of prototypical Tools organized
into subsubmodules. If it's just a single function without much complexity, it
probably belongs in the Toolkit; but as soon as complexity or multiple
functions emerge with a theme, it can be promoted to a Tool.

"""

__all__ = ['ToolRegistration']


class ToolRegistration:
    """
    ToolRegistration is a data class for holding general, system-wide
    information about a Tool. Note that it doesn't hold the tool's data, just
    the static information about the tool like its reset function.

    Attributes:
        name (str): The formal name of this tool.
        reset (callable): A function defined for initializing and
            re-initializing the tool's data.
    """
    def __init__(self, name, reset):
        self.name = name
        self.reset = reset
