"""
Collection of commonly reusable positive feedback. Let's all be a little better!
"""
from pedal.core.commands import compliment


class correct_output(compliment):
    """ Signals that the student's output looks correct. """
    message = "Your output looks correct."
    title = "Correct Output"

    def __init__(self, **kwargs):
        super().__init__(self.message, **kwargs)


class close_output(compliment):
    message = "Your output is close to being correct!"
    title = "Output Is Close"

    def __init__(self, reason, **kwargs):
        fields = kwargs.setdefault('fields', {})
        fields['reason'] = reason
        super().__init__(self.message, **kwargs)
