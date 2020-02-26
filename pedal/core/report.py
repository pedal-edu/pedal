__all__ = ['Report', 'MAIN_REPORT']

from pedal.core.feedback_category import FeedbackCategory


class Report:
    """
    A class for storing Feedback generated by Tools, along with any auxiliary
    data that the Tool might want to provide for other tools.

    Attributes:
        submission (:py:class:`~pedal.core.submission.Submission`): The contextualized submission information.
        feedback (list of :py:class:`~pedal.core.feedback.Feedback`): The raw feedback generated for
            this Report so far.
        suppressions (list of tuple(str, str)): The categories and labels that have been suppressed so far.
        group (int or str): The label for the current group. Feedback given
            by a Tool will automatically receive the current `group`. This
            is used by the Source tool, for example, in order to group feedback
            by sections.
        group_names (dict[group:str]): A printable, student-facing name for the
            group. When a group needs to be rendered out to the user, this
            will override whatever label was going to be presented instead.
        group_order (sequence or callable or None): The mechanism to use to
            order groups. If a sequence, the order will be inferred based on
            the order of elements in the sequence. If a callable, the callable
            will be used as a key function for `sort`. If `None`, then defaults
            to the natural ordering of the groups. Defaults to `None`.
        hooks (dict[str: list[callable]): A dictionary mapping events to
            a list of callable functions. Tools can register functions on
            hooks to have them executed when the event is triggered by another
            tool. For example, the Assertions tool has hooks on the Source tool
            to trigger assertion resolutions before advancing to next sections.
        _tool_data (dict of str => any): Maps tool names to their data. The
                                       namespace for a tool can be used to
                                       store whatever they want, but will
                                       probably be in a dictionary itself.
    """
    group_order = None

    TOOLS = {}

    def __init__(self):
        """
        Creates a new Report instance.
        """
        self.clear()

    def clear(self):
        """

        """
        self.feedback = []
        self.suppressions = {}
        self.suppressed_labels = []
        self._tool_data = {}
        self.group = None
        self.group_names = {}
        self.hooks = {}
        self.submission = None

    def contextualize(self, submission):
        """

        Args:
            submission:
        """
        self.submission = submission

    def hide_correctness(self):
        """

        """
        self.suppressions[FeedbackCategory.RESULT] = []

    def add_feedback(self, feedback):
        """
        Attaches the given feedback object to this report.

        Args:
            feedback:

        Returns:
            :py:class:`~pedal.core.feedback.Feedback`: The attached feedback
        """
        self.feedback.append(feedback)
        return feedback

    def suppress(self, category=None, label=True, where=True):
        """
        Args:
            category (str): The category of feedback to suppress.
            label (bool or str): A specific label to match against and suppress.
            where (bool or group): Which group of report to localize the
                suppression to. If instead `True` is passed, the suppression
                occurs in every group globally.
                TODO: Currently, only global suppression is supported.
        """
        if category is None:
            self.suppressed_labels.append(label)
        else:
            category = category.lower()
            if isinstance(label, str):
                label = label.lower()
            if category in FeedbackCategory.ALIASES:
                category = FeedbackCategory.ALIASES[category]
            if category not in self.suppressions:
                self.suppressions[category] = []
            self.suppressions[category].append(label)

    def add_hook(self, event, function):
        """
        Register the `function` to be executed when the given `event` is
        triggered.
        
        Args:
            event (str): An event name. Multiple functions can be triggered for
                the same `event`. The format is as follows: `"namespace.function.extra"`
                The `".extra"` component is optional to add further nuance, but
                the general idea is that you are referring to functions that,
                when called, should trigger other functions to be called first.
                The namespace is typically a tool or module.
            function (callable): A callable function. This function should
                accept a keyword parameter named `report`; this report will be passed
                as as that argument.
        """
        if event not in self.hooks:
            self.hooks[event] = []
        self.hooks[event].append(function)

    def execute_hooks(self, tool, event_name):
        """
        Trigger the functions for all of the associated hooks.
        Hooks will be called with this report as a keyword `report` argument.

        Args:
            tool (str): The name of the tool, to namespace events by.
            event_name (str): The event name (separate words with periods).
        """
        event = tool + '.' + event_name
        if event in self.hooks:
            for function in self.hooks[event]:
                function(report=self)

    def __getitem__(self, tool_name):
        if tool_name not in self._tool_data:
            self.TOOLS[tool_name]['reset'](report=self)
        return self._tool_data[tool_name]

    def __setitem__(self, tool_name, value):
        self._tool_data[tool_name] = value

    def __contains__(self, tool_name):
        return tool_name in self._tool_data

    @classmethod
    def register_tool(cls, tool_name: str, reset_function):
        """
        Identifies that the given Tool should be made available.
        Args:
            tool_name: A unique string identifying this tool.
            reset_function: The function to call to reset the Tool.

        Returns:

        """
        if tool_name in cls.TOOLS:
            # TODO: More sophisticated exceptions
            raise Exception("Tool namespace {} already registered.")
        cls.TOOLS[tool_name] = {
            'reset': reset_function
        }


#: The global Report object. Meant to be used as a default singleton
#: for any tool, so that instructors do not have to create their own Report.
#: Of course, all APIs are expected to work with a given Report, and only
#: default to this Report when no others are given.
#: Ideally, the average instructor will never know this exists.
MAIN_REPORT = Report()
