.. _developers_ffs:

Developers: Feedback Functions
==============================

The most important unit of Pedal are its Feedback Functions.
This document walks through Feedback Functions from a Tool developer's perspective.

Why Feedback Functions?
-----------------------

When we first started giving automated feedback, our scripts became a pile of ``if`` statements
and messages. The complex logic was very delicate, and any reordering could
potentially break the chain. Large chunks of code were clearly representing very
atomic ideas, and we desired more code reuse between problems. All of our analysis
was ad-hoc and therefore much harder to do.

This led to the development of Feedback Functions, which encapsulate the detection
of issues in student code and the desired response (a Function in the relational sense).
By elevating Feedback to be a first-class object,
we can approach the development process in a declarative, data-driven
manner without sacrificing the power and flexibility of instructor logic.
Not only are Feedback Functions reusable, but they are also (probably) easier to analyze.

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

Encapsulation
    Fundamentally, a FF is composed of the *condition*, *response*, and
    *metadata*. The condition indicates whether the FF should be active. The response
    is what should happen as a result of detecting or not detecting the condition.
    The metadata provides additional information about the FF.

Truthiness
    When a FF is evaluated in a boolean context (e.g., as the conditional of an
    ``if`` statement), the FF returns whether its condition was detected.

    Feedback functions also support the bitwise exclusive or (XOR) operator (the caret, ``^``)
    in order to "turn off" their response based on the condition of another FF.

Composition
    Any given FF can be a member of a group or be a parent to a group
    of other FFs. Groups allow FFs to be controlled as an aggregate. This is particularly
    useful for things like grouped unit tests, assignments with independent sections, or
    phases of feedback evaluation.

Deserialization
    Feedback Functions can be deserialized into JSON data so their results can be
    passed to other systems for analysis.

Report
    Feedback Functions are expected to be attached to a report object.
    By default, they are all attached to the `MAIN_REPORT`. Attempting to reuse
    a specific FF instance is undefined behavior.

Creating a Feedback Function
----------------------------

Technically, you can create a new instance of a `Feedback` class directly, and pass in arguments
for all of its metadata and associated values. Simply calling the constructor will create a new
instance of the Feedback Function AND automatically attaches it to a report. That means it will
be considered as possible output for the resolver to show to the student. You don't even have to
save the instance to a variable. The constructor does all the work!

.. code:: python

    from pedal.core.feedback import Feedback

    # Possible, but not recommended!
    Feedback(label="addition_error", title="Addition Error",
             message="You should not have added those two numbers!",
             category=Feedback.CATEGORIES.SPECIFICATION)

However, this is not the recommended way. First, this approach is not reusable: you'd have to
have all those arguments every time you wanted to create a new instance. You could put this into
a function, but at that point you might as well have gone with the recommended approach and created
a subclass of ``Feedback`` instead.

.. code:: python

    from pedal.core.feedback import Feedback

    # Recommended!
    class addition_error(Feedback):
        title = "Addition Error"
        message = "You should not have added those two numbers!"
        category=Feedback.CATEGORIES.SPECIFICATION

    # Then in your instructor control script, you just call:
    addition_error()

Now, when you call ``addition_error()`` the feedback will be created and automatically added to the
report. Since we chose the ``SPECIFICATION`` category, the feedback will only be shown if there are no
runtime or syntax errors. If you want to show the feedback regardless of runtime or algorithmic, you can use the
``INSTRUCTOR`` category instead (although syntax errors will still win out). The default priority list is:

1. ``"highest"``
2. ``Feedback.CATEGORIES.SYNTAX``
3. ``Feedback.CATEGORIES.MISTAKES``
4. ``Feedback.CATEGORIES.INSTRUCTOR``
5. ``Feedback.CATEGORIES.ALGORITHMIC``
6. ``Feedback.CATEGORIES.RUNTIME``
7. ``Feedback.CATEGORIES.STUDENT``
8. ``Feedback.CATEGORIES.SPECIFICATION``
9. ``Feedback.CATEGORIES.POSITIVE``
10. ``Feedback.CATEGORIES.INSTRUCTIONS``
11. ``Feedback.CATEGORIES.UNKNOWN``
12. ``"lowest"``

Now, what if you wanted to have the FF only activated if the student's code contained a specific
error? Perhaps you are checking if the plus sign ever appears in their original source code of the
submission. By implementing the ``condition`` method, you can have the FF check whether it should
actually be activated.

.. code:: python

    from pedal.core.feedback import Feedback

    class addition_error(Feedback):
        title = "Addition Error"
        message = "You should not have added those two numbers!"
        category=Feedback.CATEGORIES.SPECIFICATION

        def condition(self):
            return "+" in self.report.submission.main_code

    # Then, in your instructor control script, you can just call:
    addition_error()


What if we wanted to parameterize the check, so the instructor could specify the operator?
If you don't care about changing the message, this is easy. Any extra positional arguments or
non-default keyword arguments will be passed to the ``condition`` method.

.. code:: python

    from pedal.core.feedback import Feedback

    class addition_error(Feedback):
        title = "Addition Error"
        message = "You should not have added those two numbers!"
        category=Feedback.CATEGORIES.SPECIFICATION

        def condition(self, operator):
            return operator in self.report.submission.main_code

    # Then, in your instructor control script, you can just call:
    addition_error("+")
    addition_error("-")


What if we wanted to modify the message? We could use the ``message_template`` field. There are
various shortcut ways to do this, but let's look at a more sophisticated way of overriding things:
overriding the constructor and updating the fields. One of the fields comes directly from the
constructor, but the other is calculated based on that parameter. We allow the instructor to also
pass in other fields, if they so choose.

.. code:: python

    from pedal.core.feedback import Feedback

    class addition_error(Feedback):
        title = "Addition Error"
        message_template = "You used the {operator} operator. Do not {verb}!"
        category = Feedback.CATEGORIES.SPECIFICATION

        def __init__(self, operator, **kwargs):
            fields = kwargs.setdefault('fields', {})
            fields['operator'] = operator
            fields['verb'] = "add" if operator == "+" else "subtract"
            super().__init__(**kwargs)

        def condition(self):
            return self.fields['operator'] in self.report.submission.main_code

    # Then, in your instructor control script, you can call:
    addition_error("+")
    addition_error("-")

These are just some examples of what you can do with Feedback Functions!

The Lifetime of a Feedback Function
-----------------------------------

The following describes what happens when you create an instance of a Feedback Function.

1. The FF subclasses constructor is called.
2. Parent constructors should be executed, including the root ``Feedback`` constructor.
3. Most instance fields are updated during this time if they were provided as parameters.
4. The ``fields`` are updated with the values from the ``constant_fields``.
5. If not specified explicitly, the ``parent`` is set to be the report's current group (if there is one).
6. Any additional keyword parameters are saved as ``fields``.
7. If the ``delay_condition`` was ``False``, then the ``condition`` is evaluated.
    Otherwise, the creator of the class is obligated to call ``self._handle_condition()`` at some point.
8. The ``message``, ``else_message``, and ``justification`` are calculated.
    If the ``message`` is not ``None``, then that is returned.
    Otherwise, if the ``message_template`` is not ``None``, then that is formatted with the ``fields``.
    Otherwise, the default feedback message is shown.
    Similar logic is used for the ``else_message`` and ``justification``.
9. The ``status`` is set to ``ACTIVE`` if the ``condition`` was ``True``, otherwise it is set to ``INACTIVE``.
10. If the condition was met, then the Feedback object is added to the report's ``feedbacks``.
    Otherwise, the Feedback object is added to the report's ``ignored_feedback``.
11. If the feedback has a parent, that parent will have its ``get_child_feedback`` method called.
    The parent might decide to post-processs the child feedback, or it might decide to leave it unchanged.
12. If an exception occurred during the creation of the Feedback Function, then that exception is now raised (and the FF's status is ``ERROR``).


The Metadata of Feedback Functions
----------------------------------

Feedback Functions have a number of fields that can be set to control their behavior.
When you create a new FF class, you should probably at least minimally set some of these
static class fields.

``label`` (str)
    Every Feedback Function needs to be given a name for identification.
    This name should ideally be unique within a category.
    The label should be an underscore-separated string
    following the same conventions as names in Python. They do not
    have to be globally unique, but labels should be unique within a
    category or risk being treated as equivalent.
    By default, a subclass of Feedback will have a label equal to the classes name.
    In general, the name will be the name of the underlying Python class or function that creates
    instances of that Feedback.

``category`` (str)
    The type of condition that led to this feedback object being activated.
    Choose an appropriate constant of `Feedback.CATEGORIES` for this.

``kind`` (str)
    The type of response that this feedback is meant to have.
    Choose an appropriate constant of `Feedback.KINDS` for this.

``priority`` (str)
    The priority of this feedback. Higher priority feedbacks are shown first.
    By default, the prioritization is based on the Category, so this is usually not
    needed. However, if you want to override the default ordering, you can set this
    to a different category that it better fits in with, in terms of prioritization.

``valence`` (str)
    The valence of this feedback. Positive feedback is meant to be encouraging,
    while negative feedback is meant to be discouraging. Neutral feedback is meant
    to be informative. This has serious impact on how the feedback's score is interpreted.
    Negative valence will have the score subtracted from the total, while positive
    valence will have the score added to the total.

``tool`` (str)
    An internal name for indicating the tool that created
    this feedback. Should be taken directly from the Tool itself. If `None`, then
    this was not created by a tool but directly by the control script.

``title`` (str)
    The descriptive name of the feedback to be shown to the learner.
    Often very similar to the ``label``.

``message`` (str)
    This is the response text to show to students. You can put whatever you want, but it will
    always be the same thing. Often, you will instead want to define a ``message_template``.

``message_template`` (str)
    If the message to be shown to the user is dynamic, then set this attribute instead of the ``message``.
    This becomes the template for the message to be shown to the learner.
    This is an interpolatable string, with any ``fields`` automatically injected.
    You can also use a set of format specifications to control how the fields are displayed.
    For example, the template ``"The variable {unused_variable:name} was not used."`` will
    not only inject the value of the ``unused_variable`` field, but will also use the ``name``
    formatter; an environment might turn that text into a clickable link, a tooltip, or color
    the text differently.

``score`` (float or str)
    The score to be awarded to the learner. This is a number between 0 and 1, inclusive.
    A numeric score to modify the students' total score, indicating their overall performance.
    It is ultimately up to the Resolver to decide how to combine all the different scores; the default
    strategy is to add all the scores together for any non-muted feedback.
    Most feedback is worth 0 points, but some feedback is worth a small amount of partial credit.
    Besides a numeric score, you can also give a string like ``"+50%"``.

``correct`` (bool)
    Indicates that the entire submission should be marked as correct (successful) and that the
    task is now finished. Most feedback should be marked as ``None`` (the default).

``muted`` (bool)
    Whether this piece of feedback is something that should be shown to a student. There are
    various use cases for muted feedback: they can serve as flags for later conditionals, suppressed
    default kinds of feedback, or perhaps feedback that is interesting for analysis but not pedagogically
    helpful to give to the student. They will still contribute to overall score, but not to the correctness
    of the submission.

``justification`` (str)
    A short description of why this feedback is being shown to the learner.
    This is used for debugging purposes, and is not shown to the learner.

``fields`` (dict[str, Any])
    A dictionary of information about the Feedback Function, typically to be injected into the
    message template, or meant to be used for analysis later on. The keys should all be strings
    that are valid Python identifiers. The values should be JSON-serializable, or else a custom
    serializer (``to_json``) should be provided.

``location`` (int or FeedbackLocation)
    A special field is the ``location`` field, which can be a line number or a
    :py:attr:`pedal.source.FeedbackLocation` object. This is used to indicate where the
    user's attention should be directed.


Different Ways of Disabling Feedback
------------------------------------

There are a few different ways to control the behavior of Feedback Functions.

* ``muted``:  Whether this piece of feedback is something that should be shown to a student. There are
    various use cases for muted feedback: they can serve as flags for later conditionals, suppressed
    default kinds of feedback, or perhaps feedback that is interesting for analysis but not pedagogically
    helpful to give to the student. They will still contribute to overall score, but not to the correctness
    of the submission.
* ``activate``: Whether or not this Feedback should be activated. This is useful for Feedback that
      is meant to be conditionally shown; you can pass the condition to the ``activate`` field.
* ``delay_condition``: Whether or not the ``condition`` check should automatically happen
      when the Feedback is instantiated, or if it should be delayed until the Feedback is
      manually checked later. This is useful for Feedback that is meant to be activated later
      on in the execution of the control script, but should not be activated immediately.
      For example, this is how unit tests get grouped, and question pools are able to choose
      which questions to show.
* ``unscored``: Whether or not this Feedback should contribute to the overall score of the
      submission. This is useful for Feedback that is meant to be shown to the student, but
      should not be counted towards their grade.
* Suppression: This is not a feature of Feedback Functions, but a feature of reports. You can
    suppress specific labels and categories of feedback, which means that they will be completely
    and utterly skipped during the resolver phase. They will still have their condition evaluated.

Methods of Feedback Functions
-----------------------------

``__init__``

    If the Feedback object is not meant to be intelligent (e.g., it has no special fields or logic), then you don't need to
    override the ``__init__`` method. But many classes have special fields that need to be created.
    It is critical that you call the ``super().__init__(**kwargs)`` somewhere in your ``__init__`` method.
    Make sure that the ``__init__`` can take all the right parameters by using ``**kwargs``.

``condition``

    This method is called to determine whether the feedback should be activated.
    The function consumes any positional args and kwargs that were provided to the function,
    and also has access to any of the ``fields`` in that attribute.
    It should return a boolean value. If the condition is not met (return False), then the feedback
    will not be activated. If the condition is met, then the feedback will be activated.
    If the condition is not defined, then the feedback will always be activated.
    This allows you to unconditionally instantiate a feedback, but only activate it when its
    condition is met. This is useful for things like unit tests, where you want to create the
    feedback for the student, but only show it to them when they fail the test. The ``assert_equal``
    is always checked, but it only shows the feedback when the condition is met.


``_get_child_feedback``

    This is a special method that gets called when a new piece of feedback is being considered.
    For almost all FFs, this is not necessary. However, when a


Overriding Existing Feedback Functions
--------------------------------------

If you are unhappy with the message we chose for a particular feedback, you can override it.
In fact, you can override any of the attributes of existing Feedback Functions that were defined
as classes.
The ``override`` class method takes in keyword parameters for any of the fields of the Feedback Function.
The system backs up the original value of the fields, in case you ever want to restore them.

.. code:: python

    from pedal.sandbox.feedbacks import name_error

    name_error.override(constant_fields={'suggestion': "THAT NAME DOES NOT EXIST MY DUDE."})

