Researchers: Analyzing with Pedal
---------------------------------

This document summarizes how to use Pedal to analyze student code.

.. warning:: We aren't quite ready with this page yet, sorry!

If you are having trouble with Jupyter Notebooks crashing when you run student code that has an infinite recursive loop, this will fix things.


.. code-block:: python

    import sys
    sys.setrecursionlimit(1000)