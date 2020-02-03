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

    The message that should be delivered to a learner. Typically plain text, MarkDown, or HTML.

.. describe:: Feedback Function

    A function that has a side-effect of adding Feedback to the report, along with whatever other
    return values it produces.

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

.. describer:: Environment

    Specific configuration for an autograding environment that is hosting Pedal, such as
    `BlockPy <https://blockpy.com>`, `WebCAT <https://web-cat.cs.vt.edu/>`, or
    `GradeScope <https://www.gradescope.com/>`. The Environment can take care of running common
    setup functions for tools and providing the instructor with a simpler interface, as well as
    adjusting the `Submission`_ and `Resolver`_ output as needed for the autograder itself.

Based on work by Narciss 2006, we categorize feedback into the following categories.

* Result (bool): Whether or not this feedback is associated with the learner completing the task ("Success!")
* Performance (float): A relative amount that this feedback contributes to the students' performance (think in terms of partial credit, like "Triggering this feedback is worth 20%").
* misconceptions (Component): A description of the misconception that is believed to be in the student's mind, or perhaps the relevant concept from the material that should be associated with this. ("Variables must be initialized before they are used.")
* mistakes (Component): A description of the error or bug that the student has created ("NameError on line 5: sum has not been defined")
* hints (Component): A suggestion for what the student can do ("Initialize the sum variable one line 1")
* constraints (Component): A description of the task requirements or task type that the student has violated ("You used a for loop, but this question expected you to use recursion.")
* metacognitives (Component): A suggestion for more regulative strategies ("You have been working for 5 hours, perhaps it is time to take a break?")

One of these components is described by the following union type, where a Component is one of:

* A str field representing renderable text for a student
* An object with a "message (str)" field of renderable text for a student, along with whatever other fields are useful (e.g., the line number of the error)
* A list of Components

Additionally, a given Feedback object has the following metadata:

* label (str): An internal name for this specific piece of feedback. This is particularly useful for us for research purposes (we currently show it in italics as part of the message)
* tool (str): An internal name for indicating the tool that created this feedback (e.g., "tifa" or "source")
* category (str): A human-presentable name showable to a student (this is like the "Analyzer Error" message in the top left of our BlockPy boxes).
* priority (str): An indication of how important this feedback is. Might be "high/medium/low" or the name of a category to supersede.


.. image:: _static/pedal-overview.png