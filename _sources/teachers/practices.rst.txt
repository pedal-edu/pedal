Best Practices
==============


This document attempts to summarize our positions on the best practices
for using Pedal.


Documentening Feedback
----------------------

**Provide as much metadata about feedback as you can.**

When creating any piece of feedback, there are a lot of fields you can use.

The most critical one is ``label``:

.. code-block::python

    gently("The output is wrong!", label="wrong_output")

If possible, you can also label the condition category and response kind:

.. code-block::python

    gently("Try to avoid type errors.", category='runtime', response='hint')

