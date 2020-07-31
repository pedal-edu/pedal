"""
Categories and Kinds are special enumerations that classify the feedback
conditions and responses, respectively.
"""


class FeedbackCategory:
    """
    An Enumeration of feedback condition categories.
    These categories represent distinct types of feedback conditions based on their
    presence within the students' submission.
    Notice that these explain the condition, not the feedback response (which would
    fall under Kind).

    Some are contextualized to instruction ("mistakes", "specification", "instructor")
    and some are generic ("syntax", "runtime", "algorithmic"). One category is also
    available for errors identified by the student.
    """

    #: Grammatical and typographical errors that prevent parsing.
    SYNTAX = 'syntax'
    #: Execution errors triggered during runtime by an invalid Python operation
    RUNTIME = 'runtime'
    #: Errors that do not prevent functioning code but are generically wrong.
    ALGORITHMIC = 'algorithmic'
    #: Errors that do not prevent functioning code but are specifically wrong.
    MISTAKES = 'mistakes'
    #: Errors suggested because the code failed to meet specified behavior.
    SPECIFICATION = 'specification'
    #: Errors marked by the instructor in a one-off fashion.
    INSTRUCTOR = 'instructor'
    #: Errors marked by the students' own code, such as failing test cases.
    STUDENT = 'student'
    #: Stylistic errors that do not prevent correct behavior but are otherwise undesirable
    STYLE = 'style'
    #: Errors caused by the Pedal grading infrastructure or the surrounding infrastructure.
    SYSTEM = 'system'
    #: A category for feedback that are not actually errors, but is positive information.
    POSITIVE = 'positive'
    #: A special category recognizing a completed submission
    COMPLETE = 'complete'
    #: A category for feedback that are not actually errors, but is neutral.
    INSTRUCTIONS = 'instructions'
    #: A category for unknown feedback. Ideally, never used.
    UNKNOWN = 'uncategorized'

    ALIASES = {
        'parser': SYNTAX,
        'verifier': SYNTAX,
        'instructor': INSTRUCTOR,
        'analyzer': ALGORITHMIC
    }


class FeedbackKind:
    """
    An enumeration of the possible kinds of feedback responses, based on their pedagogical role.
    Valence can vary between specific instances of a kind of feedback, but some tend to
    have a specific valence.

    Attributes:
        MISCONCEPTION (str): A description of the misconception that
            is believed to be in the student's mind, or perhaps the relevant concept from the
            material that should be associated with this. ("Variables must be initialized before they are used").
        MISTAKE (str): A description of the error or bug that the student has created ("NameError on line 5: sum
            has not been defined").
        HINT (str): A suggestion for what the student can do ("Initialize the sum variable on line 2").
        CONSTRAINT (str): A description of the task requirements or task type that the student has violated
            ("You used a for loop, but this question expected you to use recursion.").
        METACOGNITIVE (str): A suggestion for more regulative strategies ("You have been working for 5
            hours, perhaps it is time to take a break?").
    """
    # Negative
    MISCONCEPTION: str = "Misconception"
    MISTAKE = "Mistake"
    HINT = "Hint"
    CONSTRAINT = "Constraint"
    METACOGNITIVE = "Metacognitive"
    REINFORCEMENT = "Reinforcement"
    # Positive
    COMPLIMENT = "Compliment"
    ENCOURAGEMENT = "Encouragement"
    # Variable
    RESULT = "Result"
    PERFORMANCE = "Performance"
    # Neutral
    INSTRUCTIONAL = "Instructional"
    META = "Meta"


class FeedbackStatus:
    """ Enumeration of feedback status outcomes. When you create a piece of
    feedback, it will be either active or inactive depeneding on whether its
    condition was met. Alternatively, it is also possible that it triggered
    an exception. It may also be delayed, indicating that it has not yet been
    checked. """
    INACTIVE = "inactive"
    ERROR = "error"
    ACTIVE = "active"
    DELAYED = "delayed"
