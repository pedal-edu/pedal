"""
The Tag class.
"""


class Tag:
    """
    Tags are used to store additional metadata for a piece of feedback
    in a semi-structured way.

    TODO: These currently are just placeholders until we make up a design!

    """
    def __init__(self, kind, name, explanation, weight):
        self.kind = kind
        self.name = name
        self.explanation = explanation
        self.weight = weight
