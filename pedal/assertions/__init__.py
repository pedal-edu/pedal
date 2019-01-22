from pedal.report.imperative import MAIN_REPORT

from pedal.assertions.assertions import *
from pedal.assertions.organizers import *


def resolve_all(report=None):
    if report is None:
        report = MAIN_REPORT


def _setup_assertions(report=None):
    if report is None:
        report = MAIN_REPORT
    if 'assertions' not in report:
        report['assertions'] = {
            'functions': [],
            'exceptions': False
        }
        report.add_hook('source.next_section.before', resolve_all)
        report.add_hook('pedal.resolvers.resolve', resolve_all)
