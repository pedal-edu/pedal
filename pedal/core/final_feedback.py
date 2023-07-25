import json
from pedal.core.feedback import Feedback
from pedal.core.commands import set_correct
from pedal.core.report import Report
from pedal.core.scoring import Score, combine_scores


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
    DEFAULT_NO_FEEDBACK_LABEL = "set_correct_no_errors"

    # TODO: Change all these so that FinalFeedback also logs considered feedback

    def __init__(self, correct=None, score=None, category=None, label=None, title=None,
                 message=None, data=None, hide_correctness=None,
                 suppressions=None, suppressed_labels=None, success=None):
        """

        Args:
            correct:
            score:
            category:
            label:
            title:
            message:
            data:
            hide_correctness:
            suppressions:
            suppressed_labels:
            success (bool): DEPRECATED. This field is now set by `correct`. The alternative parameter name is
                kept around for backwards compatibility.
        """
        self.success = self.correct = correct if correct is not None else success
        self.score = score
        self._scores = []
        self._scores_feedback = []
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
        self.considered = []
        self.used = []

    def merge(self, feedback):
        self.considered.append(feedback)
        category = feedback.category.lower()
        if category in self.suppressions:
            if True in self.suppressions[category]:
                return
            else:
                looking_for = feedback.label.lower()
                if looking_for in self.suppressions[category]:
                    list_of_fields = self.suppressions[category][looking_for]
                    # Go through each of the sets of fields
                    for fields in list_of_fields:
                        # Do any of them NOT match?
                        for field, value in fields.items():
                            if feedback.fields.get(field, None) != value:
                                break
                        else:
                            # Oh hey, a match, let's skip this guy
                            return
        if feedback.label in self.suppressed_labels:
            list_of_fields = self.suppressed_labels[feedback.label]
            # Go through each of the sets of fields
            for fields in list_of_fields:
                # Do any of them not match?
                for field, value in fields.items():
                    if feedback['fields'].get(field, None) != value:
                        break
                else:
                    return
        correct, partial, message, title, data = parse_feedback(feedback)
        if feedback and feedback.category == Feedback.CATEGORIES.SYSTEM:
            self.systems.append(feedback)
        if not feedback.unscored and feedback.score is not None:
            # Triggered Negative leads to opposite behavior for operator
            # Also untriggered positive feedback
            invert_logic = ((feedback.valence != feedback.NEGATIVE_VALENCE) == (not feedback))
            inversion = "!" if invert_logic else ""
            self._scores.append(f"{inversion}{partial}")
            feedback.resolved_score = Score.parse(f"{inversion}{partial}").to_percent_string()
        if not feedback and feedback.else_message:
            self.positives.append(feedback)
            return feedback
        if not feedback or feedback.muted:
            return
        if feedback.kind == Feedback.KINDS.COMPLIMENT:
            self.positives.append(feedback)
            return feedback
        if feedback.kind == Feedback.KINDS.INSTRUCTIONAL:
            self.instructions.append(feedback)
        self.success = self.correct = correct and self.correct
        if message is not None and self.message is None:
            self.message = message
            self.title = title
            self.category = feedback.category
            self.label = feedback.label
            self.data = data
            self.used.append(feedback)
        return feedback

    def finalize(self):
        if self.message is None:
            self.title = self.DEFAULT_NO_FEEDBACK_TITLE
            self.message = self.DEFAULT_NO_FEEDBACK_MESSAGE
        self.hide_correctness = self.suppressions.get('correct', self.suppressions.get('success', False))
        if (not self.hide_correctness and
                self.label == self.DEFAULT_NO_FEEDBACK_LABEL and
                self.category == Feedback.CATEGORIES.COMPLETE):
            # TODO: Promote to be its own atomic feedback function
            self.title = set_correct.title
            self.message = set_correct.message_template
            self.score = 1
            self.success = self.correct = True
        else:
            self.score = combine_scores(self._scores)
        self.success = self.correct = bool(self.correct)
        return self

    def __str__(self) -> str:
        return "FinalFeedback({label!r}, {title!r}, {message!r})".format(label=self.label,
                                                                         title=self.title,
                                                                         message=self.message[:50])

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
            'correct': self.correct,
            'success': self.correct,
            'score': self.score,
            "scores": self._scores,
            'category': self.category,
            'label': self.label,
            'title': self.title,
            'message': self.message,
            'data': self.data,
            'hide_correctness': self.hide_correctness,
            'location': self.data.get('location', None) if self.data else None
        }

    def to_file(self, path, format='json'):
        with open(path, 'w') as f:
            if format == 'json':
                json.dump(self.to_json(), f)
            else:
                f.write(self.for_console())

def set_correct_no_errors(report: Report) -> FinalFeedback:
    return FinalFeedback(correct=True, score=0,
                         title=None, message=None,
                         category=Feedback.CATEGORIES.COMPLETE,
                         label=FinalFeedback.DEFAULT_NO_FEEDBACK_LABEL,
                         data=[], hide_correctness=False,
                         suppressions=report.suppressions,
                         suppressed_labels=report.suppressed_labels)
