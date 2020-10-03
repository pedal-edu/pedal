import re

from pedal.core.feedback import Feedback
from pedal.core.commands import set_success


def parse_feedback(feedback):
    """

    Args:
        feedback:

    Returns:

    """
    message = feedback.message
    title = feedback.title or feedback.label
    return feedback.correct, feedback.score, message, title, feedback.fields


class FinalFeedback:
    """
    Internal class used for organizing the feedback into one place.
    Dumpable into a simple dictionary.
    """

    DEFAULT_NO_FEEDBACK_TITLE = "No Errors"
    DEFAULT_NO_FEEDBACK_MESSAGE = "No errors reported."

    SCORE_PATTERN = re.compile(r"(\!*)([\+\-\/\*])?([\d\.]+)(\%)?(.*)")

    def __init__(self, success=None, score=None, category=None, label=None, title=None,
                 message=None, data=None, hide_correctness=None,
                 suppressions=None, suppressed_labels=None):
        self.success = success
        self.score = score
        self._scores = []
        self.category = category
        self.label = label
        self.title = title
        self.message = message
        self.data = data
        self.hide_correctness = hide_correctness
        self.positives = []
        self.instructions = []
        self.systems = []
        self.suppressions = suppressions
        self.suppressed_labels = suppressed_labels

    def merge(self, feedback):
        category = feedback.category.lower()
        if category in self.suppressions:
            if True in self.suppressions[category]:
                return
            elif feedback.label.lower() in self.suppressions[category]:
                return
        if feedback.label in self.suppressed_labels:
            return
        success, partial, message, title, data = parse_feedback(feedback)
        if feedback and feedback.category == Feedback.CATEGORIES.SYSTEM:
            self.systems.append(feedback)
        if not feedback.unscored and feedback.score is not None:
            # Triggered Negative leads to opposite behavior for operator
            # Also untriggered positive feedback
            invert_logic = ((feedback.valence != feedback.NEGATIVE_VALENCE) == (not feedback))
            inversion = "!" if invert_logic else ""
            self._scores.append(f"{inversion}{partial}")
        if not feedback and feedback.else_message:
            self.positives.append(feedback)
            return
        if not feedback or feedback.muted:
            return
        if feedback.kind == Feedback.KINDS.COMPLIMENT:
            self.positives.append(feedback)
            return
        if feedback.kind == Feedback.KINDS.INSTRUCTIONAL:
            self.instructions.append(feedback)
        self.success = success and self.success
        if message is not None and self.message is None:
            self.message = message
            self.title = title
            self.category = feedback.category
            self.label = feedback.label
            self.data = data

    def finalize(self):
        if self.message is None:
            self.title = self.DEFAULT_NO_FEEDBACK_TITLE
            self.message = self.DEFAULT_NO_FEEDBACK_MESSAGE
        self.hide_correctness = self.suppressions.get('success', False)
        if (not self.hide_correctness and
                self.label == 'set_success_no_errors' and
                self.category == Feedback.CATEGORIES.COMPLETE):
            # TODO: Promote to be its own atomic feedback function
            self.title = set_success.title
            self.message = set_success.message_template
            self.score = 1
            self.success = True
        else:
            self.score = self.combine_scores(self._scores)
        self.success = bool(self.success)
        return self

    def __str__(self) -> str:
        return "FinalFeedback({label!r}, {title!r}, {message!r})".format(label=self.label,
                                                                         title=self.title,
                                                                         message=self.message[:50])

    def combine_scores(self, scores) -> float:
        total = 0
        for score in scores:
            if isinstance(score, (int, float)):
                total += score
            elif isinstance(score, str):
                total = self.parse_score(score, total)
        return round(total, 2)

    def parse_score(self, score, current) -> float:
        match = self.SCORE_PATTERN.match(score)
        if not match:
            # TODO: Add context of feedback being processed
            raise ValueError(f"Invalid Score string: {score}")
        invert = bool(len(match.group(1)) % 2)
        operator = match.group(2)
        value = float(match.group(3))
        percentage = bool(match.group(4) == "%")
        leftovers = match.group(5)
        if percentage:
            value = value / 100.0
        if operator in ("+", None) and not invert:
            current += value
        elif operator == "-" and not invert:
            current -= value
        elif operator == "*" and not invert:
            current *= value
        elif operator == "/" and not invert:
            current /= value
        return current


    def for_console(self) -> str:
        return "{label}\n{score}\n{title}\n{message}".format(label=self.label,
                                                             score=self.score,
                                                             title=self.title,
                                                             message=self.message)

    def to_json(self) -> dict:
        """

        Returns:

        """
        return {
            'success': self.success,
            'score': self.score,
            "scores": self._scores,
            'category': self.category,
            'label': self.label,
            'title': self.title,
            'message': self.message,
            'data': self.data,
            'hide_correctness': self.hide_correctness
        }