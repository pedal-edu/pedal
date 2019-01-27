from pedal.report.imperative import MAIN_REPORT

from pedal.assertions.setup import _setup_assertions, resolve_all
from pedal.assertions.assertions import *
from pedal.assertions.organizers import *

def set_assertion_mode(exceptions=True, report=None):
    if report is None:
        report = MAIN_REPORT
    _setup_assertions(report)
    
    report['assertions']['exceptions'] = exceptions
