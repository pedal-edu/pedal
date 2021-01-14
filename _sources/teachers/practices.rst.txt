Best Practices
==============


This document attempts to summarize our positions on the best practices
for using Pedal.

.. warning:: We aren't quite ready with this page yet, sorry!


Documenting Feedback
--------------------

**Provide as much metadata about feedback as you can.**

When creating any piece of feedback, there are a lot of fields you can use. A particularly critical one is ``label``, since
that will allow you to track usages of a piece of feedback:

.. code-block:: python
    :caption: grade_assignment.py

    gently("The output is wrong!", label="wrong_output")

If possible, you can also label the condition category and response kind:

.. code-block:: python
    :caption: grade_assignment.py

    gently("Try to avoid type errors.", category='runtime', response='hint')

Use Novice-Friendly Language
----------------------------

