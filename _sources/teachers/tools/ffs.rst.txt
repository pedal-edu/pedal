.. _teachers_ffs:

Feedback Functions
------------------

A major concept in Pedal is a :term:`Feedback Function`, which encapsulate the idea of a :term:`Feedback Condition` and
a :term:`Feedback Response` pair. Pedal provides a large number of Feedback Functions and mechanisms to create new ones.
As instructors, you have can control and override the default behavior of these feedback functions in various ways.

Some Composite Feedback Functions do not have keyword parameters, because of their complexity. However, we strive to
universally provide these parameters!

This documentation describes Feedback Functions from the perspective of *teachers* who are interested in writing
autograding scripts. If you are interested in extending Pedal, you might want to consult the :ref:`developers_ffs`
documentation page.



.. py:attribute:: title
    :type: str

    The descriptive name for this Feedback Function that will be shown to students as a "header" of
    sorts.

.. py:attribute:: message
    :type: str

    The actual text of the feedback that will be shown to the student. Depending on the current Formatter
    and Environment, may support HTML or Markdown. Will override the :py:attr:`message_template` if provided.

.. py:attribute:: message_template
    :type: str

    The string template used to generate the text to show the student if the :py:attr:`message` is not provided.
    Any field names wrapped in curly braces will be interpolated when the Feedback Function meets its condition.
    These fields can be further manipulated by incorporating the :ref:`teacher_formatter`'s supported conversion flags:

    .. code-block::

        # A message_template can have fields and conversion flags:
        "Your code returned {student_answer!python_value}"

        # Which will generate the HTML output:
        "Your code returned <code>5</code>"

        # Or the plain-text output:
        "Your code returned 5"

    Usually, you will override the :py:attr:`message` instead of the template, to set a specific message instead.

.. py:attribute:: else_message
    :type: str

    A string to render as the :py:attr:`message` if the Feedback Function's condition is NOT met.
    Except for Feedback Functions that have a positive valence - then this message is shown when the
    FF's condition IS met.
    Otherwise follows the same rules as the message field.
    The typical use case for this parameter is to display a positive message if the students happen to complete
    a specific subtask or task and a Resolver is chosen that will show multiple kinds of feedback.
    Note that because A) the default Resolver only shows one piece of feedback, B) that resolver prioritizes errors,
    and C) that resolve prioritizes the final Success over lesser successes, you are unlikely to see these messages
    in most cases as the actual feedback. However, the message will be provided as a Positive feedback, for environments
    that choose to render such things.

.. py:attribute:: else_message_template
    :type: str

    The corresponding string template parameter for the :py:attr:`else_message` parameter. Works the same as its
    corresponding :py:attr:`message_template` field, just for providing text to the student in the case of no
    ``else_message`` being provided. Usually not used.

.. py:attribute:: category
    :type: pedal.core.feedback_category.FeedbackCategory

    An internal name categorizing the feedback condition, such as ``"syntax"`` or ``"runtime"``.
    Usually you don't want to change this.

.. py:attribute:: kind
    :type: pedal.core.feedback_category.FeedbackKind

    An internal name categorizing the feedback response, such as ``"hint"`` or ``"mistake"``.
    Usually you don't want to change this.

.. py:attribute:: fields
    :type: dict[str, typing.Any]

    Internal data for the Feedback Function used in constructing its message and justification.

.. py:attribute:: field_names
    :type: list[str]

    An explicit list of the field names for this Feedback Function. If not provided, then it will
    be inferred from the :py:attr:`fields`. Usually you won't need to do anything with this.


.. py:attribute:: tool
    :type: str

    What Tool was responsible for creating this feedback function. Usually you don't want to change this.

.. py:attribute:: label
    :type: str

    A unique name for this general class of feedback. You might override this to give a more specific
    identifier to the feedback for future analysis purposes.

.. py:attribute:: justification
    :type: str | tuple[str, str]

    An internal explanation for why this feedback was chosen (and/or not chosen), which can be shown
    to the instructor (but not the student). Usually you don't want to change this.


.. py:attribute:: priority
    :type:

.. py:attribute:: score
    :type:

.. py:attribute:: correct
    :type:

.. py:attribute:: muted
    :type:

.. py:attribute:: unscored
    :type:


.. py:attribute:: activate
    :type:
