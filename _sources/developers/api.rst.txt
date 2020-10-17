.. _full_api:

Developer API
=============

This is the complete API reference for Pedal and its associated components.
If you are an instructor, you might find it more helpful to read over the :ref:`tutorial` too.

Important Concepts
******************

.. describe:: Feedback Function

    Any function that can attach a Feedback object to a Report is technically a Feedback Function, and
    should be clearly marked as such.

    Feedback Response should be Markdown, but should also provide a plain-text console-friendly version.

    Recommended to have a `muted` boolean parameter that allows you to use it strictly as a Condition.
    When muted, a function still attaches feedback but that feedback will not contribute to correctness
    or consider being displayed to the user. Its score will be added, though!

    Three perspectives:
        Grader Developer: We need to be able to create feedback responses that are delivered clearly
            to the autograder without being cumbersome.
        Feedback Experimenter: We need to be able to customize these messages in a way that exposes all
            the features.
        Researcher: We aren't trying to analyze Feedback through the source code. We want to be
            able to generate metadata about any piece of Feedback included in the Report.

    Tools should register all their known Feedback labels up front. Goal is to broadcast what the current
    feedback is. Ideally we'd also have a system for elegantly overriding that feedback's wording.

    Feedback Labels should have a standard naming schema; the other fields should also have some guidance
    on how they should be authored. In general, we attempt to follow Python variable naming
    rules (lowercase, underscores)

    An "Atomic" Feedback Function is one that has exactly one possible label outcome.
    They should have their metadata moved to be static function attributes.

    - TEMPLATE_TEXT ((**)=>str): A function that can be used to generate the ``text`` string. All of the fields will be passed in as keyword arguments.
    - MESSAGE_TEXT ((**)=>str): They might also have MESSAGE_TEXT with the same concept.
    - JUSTIFICATION (str): A static justification
    - TITLE (str): A static student-friendly title
    - VERSION (str): A semvar string (e.g., '0.0.1'), should be paired with a docstring changelog.

    A "Composite" Feedback Function has multiple possible label outcomes.
    - LABELS attribute could spell them all out?

    Feedback in tools:
        TIFA: Relatively centralized. Finite set. Desire for configurability, reuse of phrasings.
        Source: Mostly reporting syntax errors. Finite set.
        CAIT: No feedback functions, just feedback condition detectors.
        Assertions: Finite set. Desire for configurability, reuse of phrasings. Heavily procedurally developed.
        Questions: Finite set, but inherits from others?
        Sandbox: Runtime errors. Finite set, but also external? Strong desire for configurability.
        Toolkit: Could be Finite set. Often want to mute these and use them as conditions.

Core Commands
*************

.. automodule:: pedal.core.commands
    :members:

Report
******
    
.. automodule:: pedal.core.report
    :members:

Location
********

.. automodule:: pedal.core.location
    :members:

Feedback
********

.. automodule:: pedal.core.feedback
    :members:

Environment
***********

.. automodule:: pedal.core.environment
    :members:

Submission
***********

.. automodule:: pedal.core.submission
    :members:

Tools
*****

.. automodule:: pedal.core.tool
    :members:
