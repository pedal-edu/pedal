"""
Helper functions and basic setup routines for the entire module.
"""

from pedal.core.report import MAIN_REPORT
from pedal.core.commands import set_success
from pedal.sandbox.exceptions import SandboxStudentCodeException
from pedal.utilities.sorting import topological_sort


def resolve_all(set_successful=False, no_phases_is_success=False, report=MAIN_REPORT):
    """

    Args:
        set_success:
        report:
    """
    _setup_assertions(report)
    orderings = report['assertions']['relationships']
    phase_functions = report['assertions']['phase_functions']
    phase_names = report['assertions']['phases']
    phase_names = topological_sort(phase_names, orderings)
    #pprint(orderings)
    phase_success = no_phases_is_success
    for phase_name in phase_names:
        phase_success = True
        for function in phase_functions[phase_name]:
            try:
                phase_success = phase_success and (function() is not False)
            except AssertionBreak:
                phase_success = False
            except SandboxStudentCodeException:
                phase_success = False
        if not phase_success:
            break
        
    #for f in report.feedback:
    #    print("\t", f, f.mistake, f.misconception)
    if not report['assertions']['failures'] and phase_success and set_successful:
        set_success()
    
    _reset_phases(report)


def _add_phase(phase_name, function, report=MAIN_REPORT):
    phase_functions = report['assertions']['phase_functions']
    phases = report['assertions']['phases']
    if phase_name not in phase_functions:
        phase_functions[phase_name] = []
        phases.append(phase_name)
    phase_functions[phase_name].append(function)


def _add_relationships(befores, afters, report=MAIN_REPORT):
    relationships = report['assertions']['relationships']
    if None in (befores, afters):
        return
    if not isinstance(befores, (list, tuple)):
        befores = [befores]
    if not isinstance(afters, (list, tuple)):
        afters = [afters]
    for before in befores:
        if not isinstance(before, str):
            before = before.__name__
        if before not in relationships:
            relationships[before] = []
        for after in afters:
            if not isinstance(after, str):
                after = after.__name__
            relationships[before].append(after)
            
            
def _reset_phases(report=None):
    if report is None:
        report = MAIN_REPORT
    report['assertions']['relationships'].clear()
    report['assertions']['phases'].clear()
    report['assertions']['phase_functions'].clear()
    report['assertions']['failures'] = 0


def _setup_assertions(report):
    if 'assertions' not in report:
        report['assertions'] = {
            'phases': [],
            'phase_functions': {},
            'relationships': {},
            'exceptions': False,
            'failures': 0,
            'collected': [],
            # Should we batch up multiple assertion failures?
            #   The grouping mechanism is try_all
            'tabular_output': False,
        }
        report.add_hook('source.next_section.before', resolve_all)
        report.add_hook('pedal.resolvers.resolve', resolve_all)
