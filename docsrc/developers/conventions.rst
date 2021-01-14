Internal Naming Conventions
===========================

Labels
    Should be valid Python identifiers when possible. Treat them like
    variable names, basically: mostly lowercase, underscores as separators,
    ideally not crazy long. Try to keep them unique, distinct, and specialized,
    especially within a Category.

Category
    These should be referred to by their
    :py:class:`~pedal.core.feedback_category.FeedbackCategory` constant.
    See examples in that class for naming conventions.

Kind
    These should be referred to by their
    :py:class:`~pedal.core.feedback_category.FeedbackKind` constant.
    See examples in that class for naming conventions.

Priority
    These can be ``"low"``, ``"medium"``, or ``"high"``, or the name of a
    category.

Tool
    These should be referred to by their constant whenever possible. There are
    no restrictions on the Tool's naming schema, but we recommend something
    short, simple, and human-friendly.
