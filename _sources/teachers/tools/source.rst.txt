Source
======

Imported as::

    from pedal.source import *


.. function:: verify()

    Parses the current main code of the submission and reports any syntax errors as feedback.
    You can actually pass in explicit code and filename as strings, but by default uses the
    current submission.

.. function:: get_program() -> str

    Retrieves the current main code of the submission.

.. function:: set_source(code: str, filename: str)

    Convenience function for overriding the current submission with some other code.
    Any checks that use the main code of the submission will use this code instead.
    No longer necessary, mostly a legacy solution in light of the new contextualization through
    submissions.

.. function:: restore_code()

    Undoes the latest set_source.

Sections
--------

.. function:: separate_into_sections(pattern = r'^(##### Part .+)$')

    Breaks the current main code file into multiple sections using the regular expression `pattern`.
    The first section will be set as the main code submission, and you can advance through to the
    next one by calling :py:func:`next_section`, or verify that there are the right number of sections
    with :py:func:`check_section_exists`.

.. function:: check_section_exists(number: int)

    Verifies that the right number of expected sections exist after a separation is performed. Otherwise,
    creates new feedback indicating the issue.
    The prologue before the
    first section is 0, while subsequent ones are 1, 2, 3, etc.
    So if you have 3 sections in your code plus the prologue,
    you should pass in 3 and not 4 to verify that all of them exist.

.. function:: next_section()

    Moves the current submission main code to be the next section that was found during separation.
    If used when there are no more sections, the `not_enough_sections` feedback is given.

.. function:: stop_sections()

    Removes any separations and restores the main code submission back to a single file.

Source Feedbacks
----------------

.. feedback_function:: pedal.source.feedbacks.blank_source

.. feedback_function:: pedal.source.feedbacks.not_enough_sections

.. feedback_function:: pedal.source.feedbacks.source_file_not_found

.. feedback_function:: pedal.source.feedbacks.syntax_error

.. feedback_function:: pedal.source.feedbacks.incorrect_number_of_sections