"""
Perhaps better named "single" instead, this returns exactly one piece of feedback.


# Scoring

Some more notes on scoring.

NEGATIVE feedback function that IS TRIGGERED will subtract it's percentage.
    i.e., a bad thing happened
NEGATIVE feedback function that is NOT triggered will not subtract it's percentage.
POSITIVE feedback function that IS triggered will add it's percentage.
POSITIVE feedback function that is NOT triggered will not add it's percentage.

What happens when you have no `score` given? It's just a None. Probably should
    default to doing nothing, right? Just gets skipped in calculating the score.


Valence  | Triggered? | Operator | Result | Example
---------------------------------------------------
Positive | Yes        | +        | Add 5  | compliment()
Negative | Yes        | +        | 0      | assert_equal()
Positive | No         | +        | 0      | compliment()
Negative | No         | +        | Add 5  | assert_equal()
Positive | Yes        | -        | 0      | compliment()
Negative | Yes        | -        | Sub 5  | assert_equal()
Positive | No         | -        | Sub 5  | compliment() * Weird situation
Negative | No         | -        | 0      | assert_equal()

"+N": Default behavior for a float argument
"+N%": allows you to use whole numbers ("+20%" == "+.2" == .2)
"+N/Z": allows you to specify the total number of points consistently.
"-N"
"-N%"
"*N"
"*N%"
"/N"
"/N%"
"=N": set the score absolutely
"=N%": set the score to the percentage
"^N" or "^N%": Cap the maximum number of points possible
"_N" or "_N%": Cap the minimum number of points possible

How do scores work within a group? How do you specify that point allocations
happen within a group, or absolutely overall?
* Unit test - we control, this so teacher API is for "this function overall"
* Sections - teachers write statement level stuff
* Phase - teachers write statement level stuff

So I think scores default to their current group OR global depending on context.
You can override a score given within a group to be global using "global"?
    "+N% global"

You could also have "scoring modes" to change default behavior.
    { (Feedback.NEGATIVE, None): "=0%" }
    set_score_mode("Negative None is =0%")
        If you encounter a Negative None, then the score gets set to 0%.

I'd like to be able to use constants too, I think.
    set_grading_constant("UNITTESTS", .25)
    "+UNITTESTS%"
    "+DEFINITION%"

```python
# Give 5% if this does not get triggered
assert_equal(4, 5, score="+5%")

# Give 5% if this does get triggered
give_partial("+5%")
```

"""
from pedal.core.report import MAIN_REPORT
from pedal.core.final_feedback import FinalFeedback
from pedal.core.feedback import Feedback, DEFAULT_CATEGORY_PRIORITY
from pedal.resolvers.core import make_resolver


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


def priority_offset(priority):
    """

    Args:
        priority:

    Returns:

    """
    if priority == 'low':
        return .7
    elif priority == 'medium':
        return .5
    elif priority == 'high':
        return .3
    else:
        return .1


@make_resolver
def resolve(report=MAIN_REPORT, priority_key=by_priority):
    """
    Args:
        priority_key: The key function to sort feedbacks by
        report (Report): The report object to resolve down. Defaults to the
                         global MAIN_REPORT

    Returns
        str: A string of HTML feedback to be delivered
    """
    # Prepare feedbacks
    feedbacks = report.feedback + report.ignored_feedback
    feedbacks.sort(key=priority_key)
    # Create the initial final feedback
    final = FinalFeedback(success=True, score=0,
                          title=None, message=None,
                          category=Feedback.CATEGORIES.COMPLETE, label='set_success_no_errors',
                          data=[], hide_correctness=False,
                          suppressions=report.suppressions,
                          suppressed_labels=report.suppressed_labels)
    # Process each feedback in turn
    for feedback in feedbacks:
        final.merge(feedback)
    # Override empty message
    final.finalize()
    report.result = final
    report.resolves.append(final)
    return final

