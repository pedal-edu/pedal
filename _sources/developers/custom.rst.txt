.. custom:

Customizing Pedal
=================

There are a few major ways to extend Pedal with new functionality.


Custom Environments
-------------------

Custom Tools
------------

Custom Resolvers
----------------

Technically, all that you need to do to create a custom resolver is to create a function that takes in a ``Report`` and returns a ``FinalFeedback`` object.
Then attach the ``make_resolver`` decorator to the function.
It's also a good idea to call the ``report.finalize_feedbacks()`` method to ensure that all the feedback objects have been created before you start working with them.

.. code-block:: python

    from pedal.resolvers.core import make_resolver
    from pedal.core.report import Report, MAIN_REPORT
    from pedal.core.final_feedback import FinalFeedback

    @make_resolver
    def my_resolver(report: Report = MAIN_REPORT) -> FinalFeedback:
        report.finalize_feedbacks()
        # ...
        return FinalFeedback()


Of course, the actual work of populating the ``FinalFeedback`` object is up to you.
You can use the ``report`` object to access the ``Feedback`` objects that have been created by the tools, and use that information to create your own feedback.

Let's take a look at what the ``simple`` resolver does, with some details simplified for explanatory purposes:

.. code-block:: python

    @make_resolver
    def resolve(report=MAIN_REPORT):
        # Prepare feedbacks
        report.finalize_feedbacks()
        feedbacks = report.feedback + report.ignored_feedback
        feedbacks.sort(key=by_priority)
        # Create the initial final feedback
        final = set_correct_no_errors(report)
        # Process each feedback in turn
        for feedback in feedbacks:
            final.merge(feedback)
        # Override empty message
        final.finalize()
        # Keep track of the final object and also return it
        # IDK how important this is, but you should probably do it too
        report.result = final
        report.resolves.append(final)
        return final

The ``by_priority`` function is a simple key function that returns the priority of a feedback object.
This largely relies on the ``DEFAULT_CATEGORY_PRIORITY`` dictionary that is defined in the ``pedal.core.feedback`` module.

.. code-block:: python

    # pedal/core/feedback.py
    DEFAULT_CATEGORY_PRIORITY = [
        "highest",
        # Static
        Feedback.CATEGORIES.SYNTAX,
        Feedback.CATEGORIES.MISTAKES,
        Feedback.CATEGORIES.INSTRUCTOR,
        Feedback.CATEGORIES.ALGORITHMIC,
        # Dynamic
        Feedback.CATEGORIES.RUNTIME,
        Feedback.CATEGORIES.STUDENT,
        Feedback.CATEGORIES.SPECIFICATION,
        Feedback.CATEGORIES.POSITIVE,
        Feedback.CATEGORIES.INSTRUCTIONS,
        Feedback.CATEGORIES.UNKNOWN,
        "lowest"
    ]

    # pedal/resolvers/simple.py
    def by_priority(feedback):
        """
        Converts a feedback into a numeric representation for sorting.

        Args:
            feedback (Feedback): The feedback object to convert
        Returns:
            float: A decimal number representing the feedback's relative priority.
        """
        category = Feedback.CATEGORIES.UNKNOWN
        if feedback.category is not None:
            category = feedback.category.lower()
        priority = 'medium'
        if feedback.priority is not None:
            priority = feedback.priority.lower()
            priority = Feedback.CATEGORIES.ALIASES.get(priority, priority)
        if category in DEFAULT_CATEGORY_PRIORITY:
            value = DEFAULT_CATEGORY_PRIORITY.index(category)
        else:
            value = len(DEFAULT_CATEGORY_PRIORITY)
        if priority in DEFAULT_CATEGORY_PRIORITY:
            value = DEFAULT_CATEGORY_PRIORITY.index(priority)
            priority = 'medium'
        offset = priority_offset(priority)
        return value + offset


The ``set_correct_no_errors`` function is from the ``pedal.core.final_feedback`` module,
and is a convenience function that creates a new ``FinalFeedback`` object with the
``correct`` field set to ``True``, a blank title and message, and feedback that basically says "No feedback was provided".
The expectation is that this information will be completely overwritten by other feedback.

Most of the actual logic for "merging" the individual feedback objects and then finalizing the result is
in the ``FinalFeedback`` class itself.
This class is *very* similar to the ``Feedback`` class, but it has fewer features, is meant to be serializable
to a JSON object, and has a few extra methods for merging and finalizing the feedback.

Your custom resolver might not take advantage of the ``merge`` method, but it's still very useful to review
what that function does in order to understand how Pedal currently defaults to handling feedback objects.
We strongly recommend checking its source code in ``pedal/core/final_feedback.py``.

Note that the ``finalize`` method does rely on ``combine_scores``,
which is actually fairly complex. Mostly, you should just be aware that it exists and that it is used to combine the scores of the feedback objects.

Custom Feedback
---------------

Custom Hooks
------------
