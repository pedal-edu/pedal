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
        """
        Process a single piece of feedback, and modify ourselves based on the
        data found there. This includes updating the correctness, the message,
        the title, and any other attributes.

        Also keep track of the feedback that was considered, any positive
        feedback, instructional feedback, and system messages.

        If the feedback was ultimately not meant to be used, we return None.
        Otherwise, we return the feedback object to indicate that we have
        incorporated it into our final feedback.
        """
        self.considered.append(feedback)
        # Check if we should suppress this feedback based on its
        # category and label (and also potentially fields)
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
        # Check if this label has been suppressed specifically
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
        # Parse the feedback for its settings
        correct, partial, message, title, data = parse_feedback(feedback)
        # If it's a system message, just add it to the systems feedback list
        if feedback and feedback.category == Feedback.CATEGORIES.SYSTEM:
            self.systems.append(feedback)
        # Resolve the score, if present, making sure to handle valence
        if not feedback.unscored and feedback.score is not None:
            # Triggered Negative leads to opposite behavior for operator
            # Also untriggered positive feedback
            invert_logic = ((feedback.valence != feedback.NEGATIVE_VALENCE) == (not feedback))
            inversion = "!" if invert_logic else ""
            self._scores.append(f"{inversion}{partial}")
            feedback.resolved_score = Score.parse(f"{inversion}{partial}").to_percent_string()
        # If this is was not triggered but had an else message, then add it to the positives list
        if not feedback and feedback.else_message:
            self.positives.append(feedback)
            return feedback
        # If this feedback was not activated, or was muted, then don't do anything with it
        if not feedback or feedback.muted:
            return
        # If this is explicitly a positive feedback, add it to the positives list and stop
        if feedback.kind == Feedback.KINDS.COMPLIMENT:
            self.positives.append(feedback)
            return feedback
        # If this is explicitly instructional, add it to the instructions list
        if feedback.kind == Feedback.KINDS.INSTRUCTIONAL:
            self.instructions.append(feedback)
        # If this feedback was correct, then update the correctness
        # Once we have a single incorrect feedback, the whole thing is incorrect
        self.success = self.correct = correct and self.correct
        # If we don't have a message yet, then use this one
        if message is not None and self.message is None:
            self.message = message
            self.title = title
            self.category = feedback.category
            self.label = feedback.label
            self.data = data
            self.used.append(feedback)
        # All done, return the feedback out of politeness
        return feedback

    def finalize(self):
        """
        Finalize the feedback object, setting the title and message to
        defaults if they are not already set. Also, combine the scores
        into a single score.
        """
        # If we don't have a message yet, then use the default message
        if self.message is None:
            self.title = self.DEFAULT_NO_FEEDBACK_TITLE
            self.message = self.DEFAULT_NO_FEEDBACK_MESSAGE
        # If we have suppressed correctness, then update that flag
        self.hide_correctness = self.suppressions.get('correct', self.suppressions.get('success', False))
        # As long as we are allowed, change the default message to the "correct" message
        if (not self.hide_correctness and
                self.label == self.DEFAULT_NO_FEEDBACK_LABEL and
                self.category == Feedback.CATEGORIES.COMPLETE):
            # TODO: Promote to be its own atomic feedback function
            self.title = set_correct.title
            self.message = set_correct.message_template
            self.score = 1
            self.success = self.correct = True
        else:
            # If they weren't correct, we need to combine the scores
            self.score = combine_scores(self._scores)
        # Update the success/correct flags
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
