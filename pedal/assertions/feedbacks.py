"""

"""

from pedal.core.feedback import Feedback


class AssertionFeedback(Feedback):
    """ Class for representing constraints asserted by an instructor """
    category = Feedback.CATEGORIES.SPECIFICATION
    valence = Feedback.NEGATIVE_VALENCE
    kind = Feedback.KINDS.CONSTRAINT
