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

from pedal.resolvers import simple as simple_resolver


def print_resolve(*args, **kwargs):
    """
    Trivial formatter for resolver, just dumps the
    Title/Label/Score/Message. Any arguments are forwarded to
    :py:func:`pedal.resolvers.simple.resolve`
    """
    result = simple_resolver.resolve(*args, **kwargs)
    # Handle the new unified dictionary format
    if isinstance(result, dict) and 'final' in result:
        final = result['final']
        if final:
            print("Title:", final.get('title'))
            print("Label:", final.get('label'))
            print("Score:", final.get('score'))
            print("Message:", final.get('message'))
        else:
            print("Title: None")
            print("Label: None") 
            print("Score: None")
            print("Message: None")
    else:
        # Fallback for unexpected format
        print("Result:", result)
    return result
