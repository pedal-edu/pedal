__all__ = ['Resolver']


class Resolver:
    """
    A resolver is responsible for filtering, ordering, and choosing Feedback.

    Ideally, it is not responsible for transforming - that is a job for the Environment.
    """
    def resolve(self):
        """
        Actually choose the feedback that will be returned
        """
        pass

    def _on_pre_resolve(self):
        """
        Hook event.
        Returns:

        """

    def _on_post_resolve(self):
        """
        Hook event.
        Returns:

        """
