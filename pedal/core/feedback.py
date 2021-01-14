"""
Simple data classes for storing feedback to present to learners.
"""

__all__ = ['Feedback', 'FeedbackKind', 'FeedbackCategory',
           "CompositeFeedbackFunction",
           "FeedbackResponse"]

from pedal.core.formatting import FeedbackFieldWrapper
from pedal.core.location import Location
from pedal.core.report import MAIN_REPORT
from pedal.core.feedback_category import FeedbackKind, FeedbackCategory, FeedbackStatus

PEDAL_DEVELOPERS = ["Austin Cory Bart <acbart@udel.edu>",
                    "Luke Gusukuma <lukesg08@vt.edu>"]


class Feedback:
    """
    A class for storing raw feedback.

    Attributes:
        label (str): An internal name for this specific piece of feedback. The
            label should be an underscore-separated string following the same
            conventions as names in Python. They do not have to be globally
            unique, but labels should be as unique as possible (especially
            within a category).
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
        message_template (str): A markdown-formatted message template that will
            be used if a ``message`` is None. Any ``fields`` will be injected
            into the template IF the ``condition`` is met.
        fields (Dict[str,Any]): The raw data that was used to interpolate the
            template to produce the message.
        location (:py:attr:`~pedal.core.location.Location` or int): Information
            about specific locations relevant to this message.

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
        unscored (bool): Whether or not this piece of feedback contributes to
            the score/correctness.

        else_message (str): A string to render as a message when a
            NEGATIVE valence feedback is NOT triggered, or a POSITIVE valence
            feedback IS triggered.
            TODO: Should we also have an else_message_template? Probably.

        activate (bool): Used for default feedback objects without a custom
            condition, to indicate whether they should be considered triggered.
            Defaults to True; setting this to False means that the feedback
            object will be deactivated. Note that most inheriting Feedback
            Functions will not respect this parameter.

        author (List[str]): A list of names/emails that indicate who created this piece of feedback. They can be
            either names, emails, or combinations in the style of `"Cory Bart <acbart@udel.edu>"`.
        version (str): A version string in the style of Semantic Version (semvar) such as `"0.0.1"`. The last (third)
            digit should be incremented for small bug fixes/changes. The middle (second) digit should be used for more
            serious and intense changes. The first digit should be incremented when changes are made on exposure to
            learners or some other evidence-based motivation.
        tags (list[:py:class:`~pedal.core.tag.Tag`]): Any tags that you want to
            attach to this feedback.

        parent (int, str, or `pedal.core.feedback.Feedback`): Information about
            what logical grouping within the submission this belongs to.
            Various tools can chunk up a submission (e.g., by section), they
            can use this field to keep track of how that decision was made.
            Resolvers can also use this information to organize feedback or to
            report multiple categories.
        report (:py:class:`~pedal.core.report.Report`): The Report object to
            attach this feedback to. Defaults to MAIN_REPORT. Unspecified fields
            will be filled in by inspecting the current Feedback Function
            context.
    """

    POSITIVE_VALENCE = 1
    NEUTRAL_VALENCE = 0
    NEGATIVE_VALENCE = -1
    CATEGORIES = FeedbackCategory
    KINDS = FeedbackKind

    label = None
    category = None
    justification = None
    constant_fields = None
    fields = None
    field_names = None
    kind = None
    title = None
    message = None
    message_template = None
    else_message = None
    priority = None
    valence = None
    location = None
    score = None
    correct = None
    muted = None
    unscored = None
    tool = None
    version = '1.0.0'
    author = PEDAL_DEVELOPERS
    tags = None
    parent = None

    activate: bool
    _status: str
    _exception: Exception or None
    _met_condition: bool
    _stored_args: tuple
    _stored_kwargs: dict

    #MAIN_REPORT

    def __init__(self, *args, label=None,
                 category=None, justification=None,
                 fields=None, field_names=None,
                 kind=None, title=None,
                 message=None, message_template=None,
                 else_message=None,
                 priority=None, valence=None,
                 location=None, score=None, correct=None,
                 muted=None, unscored=None,
                 tool=None, version=None, author=None,
                 tags=None, parent=None, report=MAIN_REPORT,
                 delay_condition=False, activate=True,
                 **kwargs):
        # Internal data
        self.report = report
        # Metadata
        if label is not None:
            self.label = label
        else:
            self.label = self.__class__.__name__
        # Condition
        if category is not None:
            self.category = category
        if justification is not None:
            self.justification = justification
        self.activate = activate
        # Response
        if kind is not None:
            self.kind = kind
        if priority is not None:
            self.priority = priority
        if valence is not None:
            self.valence = valence

        # Presentation
        if fields is not None:
            self.fields = fields
        else:
            self.fields = {}
        if self.constant_fields is not None:
            self.fields.update(self.constant_fields)
        if field_names is not None:
            self.field_names = field_names
        if title is not None:
            self.title = title
        elif self.title is None:
            self.title = label
        if message is not None:
            self.message = message
        if message_template is not None:
            self.message_template = message_template
        if else_message is not None:
            self.else_message = else_message

        # Locations
        if isinstance(location, int):
            location = Location(location)
        # TODO: Handle tuples (Line, Col) and (Filename, Line, Col), and
        #  possibly lists thereof
        if location is not None:
            self.location = location
        # Result
        if score is not None:
            self.score = score
        if correct is not None:
            self.correct = correct
        if muted is not None:
            self.muted = muted
        if unscored is not None:
            self.unscored = unscored
        # Metadata
        if tool is not None:
            self.tool = tool
        if version is not None:
            self.version = version
        if author is not None:
            self.author = author
        if tags is not None:
            self.tags = tags
        # Organizational
        if parent is not None:
            self.parent = parent
        if self.parent is None:
            # Might inherit from Report's current group
            self.parent = self.report.get_current_group()
        if self.field_names is not None:
            for field_name in self.field_names:
                self.fields[field_name] = kwargs.get(field_name)
        for key, value in kwargs.items():
            self.fields[key] = value
        if 'location' not in self.fields and self.location is not None:
            self.fields['location'] = self.location
        # Potentially delay the condition check
        self._stored_args = args
        self._stored_kwargs = kwargs
        if delay_condition:
            self._met_condition = False
            self._status = FeedbackStatus.DELAYED
        else:
            self._handle_condition()


    def _handle_condition(self):
        """ Actually handle the condition check, updating message and report. """
        # Self-attach to a given report?
        self._exception = None
        try:
            self._met_condition = self.condition(*self._stored_args, **self._stored_kwargs)
            # Generate the message field as needed
            if self._met_condition:
                self.message = self._get_message()
                self._status = FeedbackStatus.ACTIVE
            else:
                self._status = FeedbackStatus.INACTIVE
        except Exception as e:
            self._met_condition = False
            self._exception = e
            self._status = FeedbackStatus.ERROR
        if self.report is not None:
            if self._met_condition:
                self.report.add_feedback(self)
            else:
                self.report.add_ignored_feedback(self)
        # Free up these temporary fields after condition is handled
        # del self._stored_args
        # del self._stored_kwargs
        if self._exception is not None:
            raise self._exception

    def condition(self, *args, **kwargs):
        """
        Detect if this feedback is present in the code.
        Defaults to true through the `activate` parameter.

        Returns:
            bool: Whether or not this feedback's condition was detected.
        """
        return self.activate

    def _get_message(self):
        """
        Determines the appropriate value for the message. It will attempt
        to use this instance's message, but if it's not available then it will
        try to generate one from the message_template. Then, it returns a
        generic message.

        You can override this to create a truly dynamic message, if you want.

        Returns:
            str: The message for this feedback.
        """
        if self.message is not None:
            return self.message
        if self.message_template is not None:
            fields = {field: FeedbackFieldWrapper(field, value, self.report.format)
                      for field, value in self.fields.items()}
            return self.message_template.format(**fields)
        return "No feedback message provided"

    def _get_child_feedback(self, feedback, active):
        """ Callback function that Reports will call when a new piece of
        feedback is being considered. By default, does nothing. This is useful
        for :py:class:`pedal.core.group.FeedbackGroup`, most other feedbacks
        will just not care.

        The ``active`` parameter controls whether or not the condition for the
        feedback was met. """

    def __xor__(self, other):
        if isinstance(other, Feedback):
            self.muted = bool(self) and not bool(other)
            self.unscored = self.muted
            other.muted = bool(other) and not bool(self)
            other.unscored = other.muted
        if isinstance(other, bool):
            self.muted = bool(self) and not bool(other)
            self.unscored = self.muted

    def __rxor__(self, other):
        return self.__xor__(other)

    def __bool__(self):
        return bool(self._met_condition)

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
        if self.parent is not None:
            metadata += ", parent=" + str(self.parent.label)
        return "Feedback({}{})".format(self.label, metadata)

    def update_location(self, location):
        """ Updates both the fields and location attribute.
        TODO: Handle less information intelligently. """
        if isinstance(location, int):
            location = Location(location)
        self.location = location
        self.fields['location'] = location

    def _fields_to_json(self):
        return self.fields.copy()

    def to_json(self):
        return {
            'correct': self.correct,
            'score': self.score,
            'title': self.title,
            'message': self.message,
            'label': self.label,
            'active': bool(self),
            'muted': self.muted,
            'unscored': self.unscored,
            'category': self.category,
            'kind': self.kind,
            'valence': self.valence,
            'version': self.version,
            'fields': self._fields_to_json(),
            'justification': self.justification,
            'priority': self.priority,
            'location': self.location.to_json() if self.location is not None else None
        }


class FeedbackResponse(Feedback):
    """
    An extension of :py:class:`~pedal.core.feedback.Feedback` that is meant
    to indicate that the class should not have any condition behind its
    response.
    """


def CompositeFeedbackFunction(*functions):
    """
    Decorator for functions that return multiple types of feedback functions.

    Args:
        functions (callable): A list of callable functions.

    Returns:
        callable: The decorated function.
    """
    def CompositeFeedbackFunction_with_attrs(function):
        """

        Args:
            function:

        Returns:

        """
        CompositeFeedbackFunction_with_attrs.functions = functions
        return function
    return CompositeFeedbackFunction_with_attrs


class FeedbackGroup(Feedback):
    """
    An extension of :py:class:`~pedal.core.feedback.Feedback` that is meant
    to indicate that this class will start a new Group context within the report
    and do something interesting with any children it gets.
    """


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
