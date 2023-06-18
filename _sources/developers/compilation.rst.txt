Compilation
===========

Pedal is a pure Python library, with almost zero dependent :ref:`libraries`. However, for deployment on certain platforms,
you may need to compile Pedal. The most obvious example is BlockPy, which uses Skulpt to run Python code in the browser.

Compiling Pedal for Skulpt
--------------------------

From within the `blockpy-edu/skulpt` project's main folder, you can run the following command (replacing ``$PEDAL_PATH`` with the path to the Pedal project folder):

.. code::

  $> npm run precompile $PEDAL_PATH/dist-js/skulpt-pedal.js $PEDAL_PATH/ pedal -- -m

The ``-- -m`` arguments at the end will make Skulpt compile the output down with various optimizations. While debugging,
you may find it helpful to remove those arguments to 1) make the compilation faster, and 2) leave in certain debug
information that might be useful.

Compiling Pedal for Pyodide
---------------------------

Nothing special is needed!
