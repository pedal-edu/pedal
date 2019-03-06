from pedal.report.imperative import MAIN_REPORT

class AssertionException(Exception):
    pass

def resolve_all(set_success=False, report=None):
    if report is None:
        report = MAIN_REPORT
    _setup_assertions(report)
    for function in report['assertions']['functions']:
        try:
            function()
        except AssertionException:
            break
    #for f in report.feedback:
    #    print("\t", f, f.mistake, f.misconception)
    if not report['assertions']['failures'] and set_success:
        report.set_success()

def _setup_assertions(report):
    if 'assertions' not in report:
        report['assertions'] = {
            'functions': [],
            'exceptions': False,
            'failures': 0,
            'collected': [],
            # Should we batch up multiple assertion failures?
            #   The grouping mechanism is try_all
            'tabular_output': False,
        }
        report.add_hook('source.next_section.before', resolve_all)
        report.add_hook('pedal.resolvers.resolve', resolve_all)
