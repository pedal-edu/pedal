"""

Resolver Types

Does there need to be some kind of hook for Tools to wrap up their business?

Simple
    Find the highest priority feedback and show that, along with any positive feedback.
    Break ties by showing the first one that was triggered.

Sectional
    Find the highest priority feedback for each section, and show that along with any positive feedback.

Full
    Report all feedback, grouped by tool/category/priority/time.

Full Summary
    Report all feedback but divided into frequencies of labels grouped by tool/category/priority/time.

"""

from pedal.resolvers import simple


def print_resolve(*args, **kwargs):
    """
    Trivial formatter for resolver, just dumps the
    Title/Label/Score/Message. Any arguments are forwarded to
    :py:func:`pedal.resolvers.simple.resolve`
    """
    result = simple.resolve(*args, **kwargs)
    print("Title:", result.title)
    print("Label:", result.label)
    print("Score:", result.score)
    print("Message:", result.message)
    return result
