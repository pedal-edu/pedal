Feedback Functions
==================

The most important unit of Pedal are its Feedback Functions.
This document walks through all of the features available on a Feedback Function.

Why Feedback Functions?
-----------------------

When we first giving automated feedback, our scripts became a pile of ``if`` statements
and messages. The complex logic was very delicate, and any reordering could
potentially break the chain. Large chunks of code were clearly representing very
atomic ideas, and we desired more code reuse between problems. All of our analysis
had to be ad-hoc and suffered.

This led to the development of Feedback Functions, which encapsulate the detection
of issues in student code and the desired response (a Function in the relational,
Discrete Mathematics sense). By elevating Feedback to be a first-class object,
we can approach the development process in a declarative, data-driven
manner without sacrificing the power and flexibility of instructor logic.
Not only are Feedback Functions reusable, but they are also easier to analyze.

Feedback Function Concepts
--------------------------

This section details the structure and interface of Feedback Functions.

Inheritance
    All Feedback Functions descend from the main `Feedback` class. This class
    has a huge number of fields and default behavior. Many of Pedal's Tools subclass
    the Feedback class, and Feedback Developers are encouraged to build their own hierarchy.
    Then, teachers writing their Instructor Control Scripts can call Feedback Functions
    in order to create instances of feedback, which are automatically attached to the
    Report.

Composition
    Fundamentally, a FF is composed of the *condition*, *response*, and
    *metadata*. The condition indicates whether the FF should be active. The response
    is what should happen as a result of detecting or not detecting the condition.
    The metadata provides additional information about the FF.

Truthiness
    When a FF is evaluated in a boolean context (e.g., as the conditional of an
    ``if`` statement), the FF returns whether its condition was detected.

Hierarchy
    Any given FF can be a member of a group or be a parent to a group
    of other FFs. Groups allow FFs to be controlled as an aggregate. This is particularly
    useful for things like grouped unit tests, assignments with independent sections, or
    phases of feedback evaluation.

    Feedback functions also support the bitwise exclusive or (XOR) operator (the caret, ``^``)
    in order to "turn off" their response based on the condition of another FF.

Serialization
    Feedback Functions can be serialized and deserialized into JSON
    data so their results can be passed to other systems for analysis.

Report
    Feedback Functions are expected to be attached to a report object.
    By default, they are all attached to the `MAIN_REPORT`. Attempting to reuse
    an instance of FF is undefined behavior.

The Metadata of Feedback Functions
----------------------------------

Label
    Every Feedback Function needs to be given a semi-unique name for
    identification. The label should be an underscore-separated string
    following the same conventions as names in Python. They do not
    have to be globally unique, but labels should be unique within a
    category or risk being treated as equivalent. Often the label will
    be the name of the underlying Python class or function that creates
    instances of that Feedback.

Category
    An internal name for indicating the tool that created
    this feedback. Should be taken directly from the Tool itself. If `None`, then
    this was not created by a tool but directly by the control script.

Tool
    What Tool was responsible for creating this feedback function.

Message
^^^^^^^

The Response to show to students.

Message Template
^^^^^^^^^^^^^^^^

An interpolatable string, with any fields automatically injected.
Has a lower priority than the ``message``.