from pedal.core.report import MAIN_REPORT


def make_resolver(func, report=None):
    '''
    Decorates the given function as a Resolver. This means that when the
    function is executed, the `"pedal.resolver.resolve"` event will be
    triggered.
    
    Args:
        func (callable): The function to decorate.
        report (Report): The Report to trigger the event on. If None, then use
            the `MAIN_REPORT`.
    '''
    if report is None:
        report = MAIN_REPORT

    def resolver_wrapper():
        """

        Returns:

        """
        report.execute_hooks('resolvers', 'resolve')
        return func()

    return resolver_wrapper
