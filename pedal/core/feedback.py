"""
Simple data classes for storing feedback to present to learners.
"""

__all__ = ['Feedback']


class Feedback:
    """
    A class for storing raw feedback.

    Attributes:
        label (str): An internal name for this specific piece of feedback.
        tool (str): An internal name for indicating the tool that created
                    this feedback.
        category (str): A human-presentable name showable to the learner.
                        More than one Feedback will be in a category, most
                        likely.
        priority (str): An indication of how important this feedback is.
                        Might be "high/medium/low" or the name of a
                        category (tool?) to supersede. Exactly how this gets
                        used is up to the resolver. A special kind of priority
                        is "positive" - which indicates that this feedback is
                        positive, and the information is good to convey to the
                        student.
        group (int or str): The group that this piece of feedback should be
            associated with. Some resolvers want to group feedback using this
            identifier.
        result (bool): Whether or not this feedback is associated with the
                       learner completing the task ("Success!").
        performance (float): A relative amount that this feedback contributes
             to the students' performance (think in terms of
             partial credit, like "Triggering this feedback
             is worth 20% (.2)").
        misconceptions (Message): A description of the misconception that
            is believed to be in the student's mind,
            or perhaps the relevant concept from the
            material that should be associated with
            this. ("Variables must be initialized
            before they are used").
        mistakes (Message): A description of the error or bug that the
                              student has created ("NameError on line 5: sum
                              has not been defined").
        hints (Message): A suggestion for what the student can do
                           ("Initialize the sum variable on line 2").
        constraints (Message): A description of the task requirements or
                                 task type that the student has violated
                                 ("You used a for loop, but this question
                                 expected you to use recursion.").
        metacognitives (Message): A suggestion for more regulative
                                    strategies ("You have been working for
                                    5 hours, perhaps it is time to take
                                    a break?").
    """
    MESSAGE_TYPES = ['hint', 'mistake', 'misconception',
                     'constraint', 'metacognitive']

    def __init__(self, label, tool='instructor',
                 category='Instructor feedback', priority=None, group=None,
                 result=None, performance=None, misconception=None,
                 mistake=None, hint=None, constraint=None,
                 metacognitive=None):
        # Metadata
        self.label = label
        self.tool = tool
        self.category = category
        self.priority = priority
        self.group = group
        # Data
        self.result = result
        self.performance = performance
        self.misconception = misconception
        self.mistake = mistake
        self.hint = hint
        self.constraint = constraint
        self.metacognitive = metacognitive

    def __str__(self):
        return "<Feedback ({})>".format(self.label)

    def __repr__(self):
        metadata = ""
        if self.tool is not None:
            metadata += ", tool=" + self.tool
        if self.category is not None:
            metadata += ", category=" + self.category
        if self.priority is not None:
            metadata += ", priority=" + self.priority
        if self.group is not None:
            metadata += ", group=" + str(self.group)
        data = ""
        return "Feedback({}{}{})".format(self.label, metadata, data)


"""
A Message is one of:
    str
    Dict with a `message` field and any other suitable fields, such as:
        html_message: An HTML message instead of a plaintext message.
        line: The line number to highlight
        error: The error message to render
"""
