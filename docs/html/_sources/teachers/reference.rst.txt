.. _quick_reference:

Teacher Reference
=================

This section describes the functions and tools available within Pedal for the
benefit of an instructor authoring feedback. It does not attempt to exhaustively
document all the features available - for that, you should refer to the :ref:`full_api`.

.. toctree::
    :maxdepth: 2
    :caption: Contents

    tools/core
    tools/tifa
    tools/cait
    tools/source

tools/source
tools/sandbox
tools/assertions
tools/toolkit


Getting Output
^^^^^^^^^^^^^^
.. code:: python

    from pedal.sandbox.compatibility import get_output
    output = get_output()
    for item in output:
        print(item)  # Each line of output is given as a separate item in the list.
