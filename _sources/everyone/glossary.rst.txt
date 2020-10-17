Glossary
========

.. glossary::

    Submission
        The learners' code along with other relevant metadata about the learner, assignment, and course.

    Instructor Control Script
        A Python script authored by the instructor using the Pedal API that contains the grading logic.

    Feedback
        Information meant to be delivered to a learner because of an identified issue with their :term:`Submission`.
        Combines the concept of a :term:`Feedback Condition` and a :term:`Feedback Response`.
        Technically speaking, a given Condition could warrant any number of possible responses; it is an open
        research question as to the best form of that Response. Often, the Response is the result of an inference
        of the learners' mental state backing the concrete Condition that was detected.

    Feedback Condition
        The conditional logic that identified an issue in a :term:`Submission`.

    Feedback Response
        The message that should be delivered to a learner. We support two kinds of responses: a plain text response
        that should be suitable for command line environments ("text"), and a Markdown/HTML version that is suitable
        for web environments ("message").

    Feedback Function
        A function that has a side-effect of adding Feedback to the report, along with whatever other
        return values it produces. If a Feedback Function intentionally only involves a single kind of
        feedback that it attaches, we refer to it as an :term:`Atomic Feedback Function` and there may be
        metadata attached. Otherwise, it would be a :term:`Composite Feedback Function` since it could produce
        several possible pieces of Feedback. Either way, the codebase attempts to document when a given
        function is also a Feedback Function.

    Feedback Label
        An identifier for feedback. Labels are meant to be unique within a given :term:`Feedback Category`, but
        they do not necessarily correspond to a specific response (especially since those can be overridden).
        The label is really identifying the condition, not the response. Tools need to do some amount of
        coordination to avoid stepping on each other's labels.

    Report
        A centralized container for Feedback and the results of each :term:`Tool`. The data for a tool is namespaced by the
        name of the tool. By default, a given :term:`Feedback Function` add :term:`Feedback` to the :term:`Main Report`, although
        technically a system can use another report instead. Reports are eventually given to a :term:`Resolver` to
        be condensed into some coherent response for the learner. Reports can allow feedback to be suppressed,
        and have a few other useful features.

    Main Report
        A global singleton used as the default :term:`Report`. Meant as a convenience, since most of the time grading
        scripts are written with the expectation that only a single Report is being generated.

    Tool
        A submodule that can read and write to a :term:`Report`, potentially building on previous Tools.

    Resolver
        A system that can analyze a Report and create a relevant bit of output for an :term:`Environment`.

    Environment
        Specific configuration for an autograding environment that is hosting Pedal, such as
        `BlockPy <https://blockpy.com>`, `WebCAT <https://web-cat.cs.vt.edu/>`, or
        `GradeScope <https://www.gradescope.com/>`. The Environment can take care of running common
        setup functions for tools and providing the instructor with a simpler interface, as well as
        adjusting the :term:`Submission` and :term:`Resolver` output as needed for the autograder itself.

    Feedback Category
        We organize feedback in several ways, including the distinct types of feedback conditions
        based on their presence within the students' submission. These categories include "Syntax",
        "Runtime", "Style", and several others.

    Feedback Kind
        Another way we organize feedback is by its pedagogical role. This reflects the way that the
        Feedback Response has been written. These kinds include "Mistake", "Misconception", "Hint",
        and several others. Different kinds may have an implicit valence.

    Atomic Feedback Function
        A :term:`Feedback Function` that returns no more than one type of feedback (as determined by the
        Label). Such functions can be decorated with the :py:func:`~pedal.core.feedback.AtomicFeedbackFunction`
        decorator to have additional meta information. It is not required that an Atomic Feedback Function
        always returns its type of feedback (i.e., it can do some checks to determine if the scenario exists).
        Typically, the name of the function is the same as its label.

    Composite Feedback Function
        A :term:`Feedback Function` that potentially returns more than one type of feedback. This is not
        a required tag, but helps provide more metadata about the possible kinds of feedback that a given
        function returns.
