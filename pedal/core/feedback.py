"""
Simple data classes for storing feedback to present to learners.
"""

__all__ = ['Feedback', 'FeedbackKind', 'FeedbackCategory']

from pedal.core.location import Location


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

    TODO: Rewrite the documentation below in the #: alternate style.

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
    MISCONCEPTION = "Misconception"
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


class Feedback:
    """
    A class for storing raw feedback.

    Attributes:
        label (str): An internal name for this specific piece of feedback. The label
            should be an underscore-separated string following the same conventions as
            names in Python. They do not have to be globally unique, but labels should be
            as unique as possible (especially within a category).
        tool (str, optional): An internal name for indicating the tool that created
            this feedback. Should be taken directly from the Tool itself. If `None`, then
            this was not created by a tool but directly by the control script.
        category (str): A human-presentable name showable to the learner, indicating what
            sort of feedback this falls into (e.g., "runtime", "syntax", "algorithm").
            More than one feedback will be in a category, but a feedback cannot be in
            more than one category.
        kind (str): The pedagogical role of this feedback, e.g., "misconception", "mistake",
            "hint", "constraint". Usually, a piece of Feedback is pointing out a mistake,
            but feedback can also be used for various other purposes.
        justification (str): An instructor-facing string briefly describing why this
            feedback was selected. Serves as a "TL;DR" for this feedback category, useful
            for debugging why a piece of feedback appeared.
        priority (str): An indication of how important this feedback is relative to other types
            of feedback in the same category. Might be "high/medium/low". Exactly how this
            gets used is up to the resolver, but typicaly it helps break ties.
        valence (int): Indicates whether this is negative, positive, or neutral feedback.
            Either 1, -1, or 0.

        title (str, optional): A formal, student-facing title for this feedback. If None, indicates
            that the :py:attr:`~pedal.core.feedback.Feedback.label` should be used instead.
        message (Dict[str,str]): A dictionary mapping types of message outputs to their generated
            format. By default, we expect `"text"` and `"markdown"`, but other possibilities include
            `"html"`.
        template (Dict[str,str]): The raw string template (using the `str.format` style) that was used to generate
            this feedback's messages.
        fields (Dict[str,Any]): The raw data that was used to interpolate the template to produce the message.
        locations (:obj:`list` of :py:attr:`~pedal.core.location.Location`): Information about specific locations
            relevant to this message.

        score (int): A numeric score to modify the students' total score, indicating their overall performance.
            It is ultimately up to the Resolver to decide how to combine all the different scores; a typical
            strategy would be to add all the scores together for any non-muted feedback.
        correct (bool): Indicates that the entire submission should be considered correct (success) and that the
            task is now finished.
        muted (bool): Whether this piece of feedback is something that should be shown to a student. There are
            various use cases for muted feedback: they can serve as flags for later conditionals, suppressed
            default kinds of feedback, or perhaps feedback that is interesting for analysis but not pedagogically
            helpful to give to the student.

        author (List[str]): A list of names/emails that indicate who created this piece of feedback. They can be
            either names, emails, or combinations in the style of `"Cory Bart <acbart@udel.edu>"`.
        version (str): A version string in the style of Semantic Version (semvar) such as `"0.0.1"`. The last (third)
            digit should be incremented for small bug fixes/changes. The middle (second) digit should be used for more
            serious and intense changes. The first digit should be incremented when changes are made on exposure to
            learners or some other evidence-based motivation.

        group (int or str): Information about what logical grouping within the submission this belongs to. Various
            tools can chunk up a submission (e.g., by section), they can use this field to keep track of how that
            decision was made. Resolvers can also use this information to organize feedback or to report multiple
            categories.
    """

    POSITIVE_VALENCE = 1
    NEUTRAL_VALENCE = 0
    NEGATIVE_VALENCE = -1

    def __init__(self, label, tool=None, category='instructor', kind='mistake', justification=None,
                 priority=None, valence=-1, title=None, message=None, template=None, fields=None,
                 locations=None, score=None, correct=None, muted=None, version=None, author=None,
                 group=None):
        # Model
        self.label = label
        self.tool = tool
        self.category = category
        self.kind = kind
        self.justification = justification
        self.priority = priority
        self.valence = valence
        # Presentation
        self.title = title
        self.message = message
        self.template = template
        self.fields = fields
        if isinstance(locations, int):
            locations = Location(locations)
        # TODO: Handle tuples (Line, Col) and (Filename, Line, Col), and possibly lists thereof
        self.locations = locations
        # Result
        self.score = score
        self.correct = correct
        self.muted = muted
        # Metadata
        self.version = version
        self.author = author
        # Organizational
        self.group = group

    def __str__(self):
        """
        Create a string representation of this piece of Feedback for quick, dev purposes.
        Returns:
            str: String representation
        """
        return "<Feedback ({},{})>".format(self.category, self.label)

    def __repr__(self):
        """
        Create a string representation of this piece of Feedback that displays considerably more information.
        Returns:
            str: String representation with more data
        """
        metadata = ""
        if self.tool is not None:
            metadata += ", tool=" + self.tool
        if self.category is not None:
            metadata += ", category=" + self.category
        if self.priority is not None:
            metadata += ", priority=" + self.priority
        if self.group is not None:
            metadata += ", group=" + str(self.group)
        return "Feedback({}{})".format(self.label, metadata)


PEDAL_DEVELOPERS = ["Austin Cory Bart <acbart@udel.edu>", "Luke Gusukuma <lukesg08@vt.edu>"]
