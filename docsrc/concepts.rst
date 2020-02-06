Important Concepts
==================

.. describe:: Submission

    The learners' code along with other relevant metadata about the learner, assignment, and course.

.. describe:: Instructor Control Script

    A Python script authored by the instructor using the Pedal API that contains the grading logic.

.. describe:: Feedback

    Information meant to be delivered to a learner because of an identified issue with their `Submission`_.
    Combines the concept of a `Feedback Condition`_ and a `Feedback Response`_.
    Technically speaking, a given Condition could warrant any number of possible responses; it is an open
    research question as to the best form of that Response. Often, the Response is the result of an inference
    of the learners' mental state backing the concrete Condition that was detected.

.. describe:: Feedback Condition

    The conditional logic that identified an issue in a `Submission`_.

.. describe:: Feedback Response

    The message that should be delivered to a learner. We support two kinds of responses: a plain text response
    that should be suitable for command line environments, and a Markdown/HTML version that is suitable for web
    environments.

.. describe:: Feedback Function

    A function that has a side-effect of adding Feedback to the report, along with whatever other
    return values it produces. If a Feedback Function intentionally only involves a single kind of
    feedback that it attaches, we refer to it as an `Atomic Feedback Function`_ and there may be
    metadata attached. Otherwise, it would be a `Composite Feedback Function`_ since it could produce
    several possible pieces of Feedback. Either way, the codebase attempts to document when a given
    function is also a Feedback Function.

.. describe:: Report

    A centralized container for Feedback and the results of each `Tool`_. The data for a tool is namespaced by the
    name of the tool. By default, `Feedback Functions`_ add `Feedback`_ to the `Main Report`_, although
    technically a system can use another report instead. Reports are eventually given to a `Resolver`_ to
    be condensed into some coherent response for the learner. Reports can allow feedback to be suppressed,
    and have a few other useful features.

.. describe:: Main Report

    A global singleton used as the default `Report`_. Meant as a convenience, since most of the time grading
    scripts are written with the expectation that only a single Report is being generated.

.. describe:: Tool

    A submodule that can read and write to a `Report`_, potentially building on previous Tools.

.. describe:: Resolver

    A system that can analyze a Report and create a relevant bit of output for an `Environment`_.

.. describe:: Environment

    Specific configuration for an autograding environment that is hosting Pedal, such as
    `BlockPy <https://blockpy.com>`, `WebCAT <https://web-cat.cs.vt.edu/>`, or
    `GradeScope <https://www.gradescope.com/>`. The Environment can take care of running common
    setup functions for tools and providing the instructor with a simpler interface, as well as
    adjusting the `Submission`_ and `Resolver`_ output as needed for the autograder itself.

.. describe:: Feedback Category

    We organize feedback in several ways, including the distinct types of feedback conditions
    based on their presence within the students' submission. These categories include "Syntax",
    "Runtime", "Style", and several others.

.. describe:: Feedback Kind

    Another way we organize feedback is by its pedagogical role. This reflects the way that the
    Feedback Response has been written. These kinds include "Mistake", "Misconception", "Hint",
    and several others. Different kinds may have an implicit valence.
