"""
Simple data classes for storing feedback to present to learners.
"""

__all__ = ['Feedback', 'FeedbackKind', 'FeedbackCategory', "AtomicFeedbackFunction"]

from pedal.core.location import Location
from pedal.core.report import MAIN_REPORT
from pedal.core.feedback_category import FeedbackKind, FeedbackCategory


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
        message (str): A markdown-formatted message (aka also supporting HTML) that could be rendered
            to the user.
        text (str): A console-friendly, plain-text message that could be rendered to the user.
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
            helpful to give to the student. They will still contribute to overall score, but not to the correcntess
            of the submission.

        author (List[str]): A list of names/emails that indicate who created this piece of feedback. They can be
            either names, emails, or combinations in the style of `"Cory Bart <acbart@udel.edu>"`.
        version (str): A version string in the style of Semantic Version (semvar) such as `"0.0.1"`. The last (third)
            digit should be incremented for small bug fixes/changes. The middle (second) digit should be used for more
            serious and intense changes. The first digit should be incremented when changes are made on exposure to
            learners or some other evidence-based motivation.
        tags (List[str]): Any tags that you want to attach to this feedback.

        group (int or str): Information about what logical grouping within the submission this belongs to. Various
            tools can chunk up a submission (e.g., by section), they can use this field to keep track of how that
            decision was made. Resolvers can also use this information to organize feedback or to report multiple
            categories.
    """

    POSITIVE_VALENCE = 1
    NEUTRAL_VALENCE = 0
    NEGATIVE_VALENCE = -1
    CATEGORIES = FeedbackCategory
    KINDS = FeedbackKind

    def __init__(self, label, tool=None, category='instructor', kind='mistake', justification=None,
                 priority=None, valence=-1, title=None, message=None, text=None, fields=None,
                 locations=None, score=None, correct=None, muted=None, version=None, author=None, tags=None,
                 group=None, report=MAIN_REPORT):
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
        self.text = text
        self.fields = fields
        if isinstance(locations, int):
            locations = [Location(locations)]
        elif isinstance(locations, Location):
            locations = [locations]
        # TODO: Handle tuples (Line, Col) and (Filename, Line, Col), and possibly lists thereof
        self.locations = locations
        # Result
        self.score = score
        self.correct = correct
        self.muted = muted
        # Metadata
        self.version = version
        self.author = author
        self.tags = tags
        # Organizational
        self.group = group
        # Self-attach to a given report?
        if report is not None:
            report.add_feedback(self)

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


def AtomicFeedbackFunction(title=None, version='0.0.1', message_template=None, text_template=None,
                           justification=None, tags=None, muted=None):
    """
    Decorator for feedback functions to indicate their intent.

    Args:
        tags:
        title:
        text_template:
        message_template:
        version:
        justification:

    Returns:

    """
    def AtomicFeedbackFunction_with_attrs(function):
        """

        Args:
            function:

        Returns:

        """
        function.title = title if title is not None else function.__name__
        function.tags = tags if tags is not None else []
        function.version = version
        function.justification = justification
        function.message_template = message_template or text_template
        function.text_template = text_template or message_template
        function.muted = muted
        return function
    return AtomicFeedbackFunction_with_attrs


def CompositeFeedbackFunction():
    """

    Returns:

    """
    def CompositeFeedbackFunction_with_attrs(function):
        """

        Args:
            function:

        Returns:

        """
        return function
    return CompositeFeedbackFunction_with_attrs


PEDAL_DEVELOPERS = ["Austin Cory Bart <acbart@udel.edu>", "Luke Gusukuma <lukesg08@vt.edu>"]
