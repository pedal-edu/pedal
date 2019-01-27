from pedal.report.imperative import MAIN_REPORT

def resolve_all(report=None):
    if report is None:
        report = MAIN_REPORT
    _setup_assertions(report)
    for function in report['assertions']['functions']:
        function()

def _setup_assertions(report):
    if 'assertions' not in report:
        report['assertions'] = {
            'functions': [],
            'exceptions': False,
            'collected': [],
            # Should we batch up multiple assertion failures?
            #   The grouping mechanism is try_all
            'tabular_output': False,
        }
        report.add_hook('source.next_section.before', resolve_all)
        report.add_hook('pedal.resolvers.resolve', resolve_all)
