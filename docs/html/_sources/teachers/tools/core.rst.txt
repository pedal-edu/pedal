Core Commands
-------------

Imported as::

    from pedal import *

.. function:: set_success(justification: str = None)

    Set this submission as correct/complete/successful. Typically resolved as overriding
    all other feedback. Often triggered as part of a conditional. You can optionally set
    an (internal) `justification` message for why this was triggered.

    ::

        set_success()

.. function:: compliment(message: str, value: float = 0, justification: str = None)

    Provides a `message` to the student complimenting them on something they did correctly.
    You can also specify a numeric `value` that will be added as partial credit.
    Finally, you can optionally set an internal `justification` message for why this was triggered.

    ::

        compliment("Your `for` loop looks correct!")

.. function:: give_partial(value: float, justification: str = None)

    Increases the student's overall score by the numeric `value`.
    Finally, you can optionally set an internal `justification` message for why this was triggered.

    ::

        give_partial(.5)

.. function:: explain(message: str, label: str = "explain", justification: str = None)

    A core feedback function, used to display a specific feedback `message` response to the
    learner. The `label` can be given to help track this piece of feedback; we strongly recommend
    always including a :term:`Feedback Label` when you can! You can also provide the internal `justification`
    text to give some debug information about the justification for this feedback. By default,
    this feedback's priority tends to override almost any other kind besides syntax errors.

    ::

        explain("You need to use a For loop for this problem!")

        explain("You need to use a For loop for this problem!", label="do_not_use_for_loop")

.. function:: gently(message: str, label: str, justification: str = None)

    A core feedback function, used to display a specific feedback `message` to the learner.
    Basically the same as the :py:func:`explain`, except the priority is much lower. This will not
    override runtime or :ref:`algorithmic <tifa>` errors.
    The `label` can be given to help track this piece of feedback; we strongly recommend
    always including a :term:`Feedback Label` when you can! You can also provide the internal `justification`
    text to give some debug information about the justification for this feedback.

    ::

        gently("Your solution looks close, but you haven't incorporated any multiplication.")

        gently("Your solution looks close, but you haven't incorporated any multiplication.",
               label="need_multiplication")

.. function:: guidance(message: str, label: str = "guidance", justification: str = None)

    Used to display guiding feedback such as a hint or revised instructions via the `message` to the learner.
    You are recommended to include a :term:`Feedback Label`, but not obligated. You can also optionally
    include a justification.

    ::

        guidance("Great work so far - now try incorporating a variable!")

        guidance("Great work so far - now try incorporating a variable!",
                 label="incorporate_variable")

.. function:: hide_correctness()

    Special function to signal to the environment to not report whether or not this submission was correct.
    Useful in exam situations where you do not want to explicitly state whether the student has a correct
    answer even if the system can detect it.; not that we take a stance on whether that's a sound strategy
    pedagogically.

    ::

        hide_correctness()

.. function:: suppress(category: str = None, label: str = None)

    Override whether a particular :term:`Feedback Category` or an individual :term:`Feedback Label`
    should be displayed to the user. You can specify one or both, and it will refine the answer accordingly.

    ::

        from pedal.core.feedback_category import FeedbackCategory

        # Suppress Type Errors
        suppress(FeedbackCategory.RUNTIME, "TypeError")
        # Suppress all TIFA feedback
        suppress(FeedbackCategory.ALGORITHMIC)
        # Suppress any occurrences of this custom feedback label
        suppress(label="wrong_output")

.. function:: log(message)

    A muted feedback type meant for internal system usage, will not be shown to the student. You can use
    this to log data that will be viewable as an instructor, since printing is often not available when
    writing grading scripts.

    ::

        log("This line of code was reached!")

.. function:: debug(message)

    Similar to :py:func:`log`, a muted feedback type meant for internal system usage. However, this one
    should be used to indicate that something went wrong.

    ::

        debug("The conditional should be false, but was true instead.")

.. function:: clear_report()

    Removes all existing data from the report, including any submissions, suppressions, feedback,
    and Tool data. Essentially resets the entire grading script. Be careful about using this one!

    ::

        clear_report()

.. function:: contextualize_report(submission: str or Submission, filename: str = "answer.py", clear: bool = True)

    Updates the report with the submission.
    You can pass in either an actual :py:class:`~pedal.core.submission.Submission` or a string representing
    the code of the submission, for the first parameter. The second parameter is unused if you pass in a
    Submission object, but otherwise will be used as the filename of the student's code. You can optionally
    choose to avoid clearing out any existing report information, but by default, clears out any old information
    in the report.
    Most environments handle contextualizing the report for you, but you might want to do so yourself. You
    can use the :ref:`Source <source>` tool to temporarily override the current code for the submission (e.g., to
    handle follow-up evaluations). Using a full Submission object is more powerful, since you can attach
    additional meta information and specify additional files.

    ::

        # Simple two-argument version
        contextualize_report("print('hello world')", "answer.py")

        # More complex configuration using a Submission
        from pedal.core.submission import Submission
        files = {"answer.py": "print(open('input.txt').read())", "input.txt": "1\n31\n44\n2"}
        contextualize_report(Submission(files, user={"name": "Ada Bart"}))

.. function:: get_all_feedback() -> List[Feedback]

    Retrieves a list of all the :py:class:`~pedal.core.feedback.Feedback` currently attached to the report,
    which you could inspect in order to reuse conditions or even perhaps modify responses.
    Not very convenient currently, but we will improve the interface if there is demand.

    ::

        labels = [feedback.label for feedback in get_all_feedback()]
        if "wrong_output" in labels and "not_printing" in labels:
            gently("Looks like you are not printing and you have the wrong output!")

