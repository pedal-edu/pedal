

So you want to analyze student code with Pedal.

If you are having trouble with Jupyter Notebooks crashing when you run student code that has an infinite recursive loop, this will fix things.


.. code-block:: python

    import sys
    sys.setrecursionlimit(1000)