"""
Resolvers are called at the end of the grading script in order to determine
what pieces of feedback should actually be delivered.
"""

__all__ = ['Resolver']

from pedal.core.report import MAIN_REPORT


class Resolver:
    """
    A resolver is responsible for filtering, ordering, and choosing Feedback.

    Ideally, it is not responsible for transforming - that is a job for the Environment.
    """

    def resolve(self):
        """
        Actually choose the feedback that will be returned
        """

    def _on_pre_resolve(self):
        """
        Hook event that is run before a resolver actually begins its process.

        TODO: This doesn't do anything yet
        """

    def _on_post_resolve(self):
        """
        Hook event that is after a resolver actually begins its process.
        """
