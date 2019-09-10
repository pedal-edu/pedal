import sys

from pedal.report.imperative import MAIN_REPORT
from pedal.sandbox.exceptions import SandboxStudentCodeException

class AssertionException(Exception):
    def __str__(self):
        return self.args[0]

def _topological_sort(names, orderings):
    visited = set()
    stack = []
    
    def dfs(name):
        visited.add(name)
        if name in orderings:
            for neighbor in orderings[name]:
                if neighbor not in visited:
                    dfs(neighbor)
        stack.insert(0, name)
    
    for name in names[::-1]:
        if name not in visited:
            dfs(name)
    return stack
    

def resolve_all(set_success=False, report=None):
    from pprint import pprint
    if report is None:
        report = MAIN_REPORT
    _setup_assertions(report)
    orderings = report['assertions']['relationships']
    phase_functions = report['assertions']['phase_functions']
    phase_names = report['assertions']['phases']
    phase_names = _topological_sort(phase_names, orderings)
    #pprint(orderings)
    phase_success = False
    for phase_name in phase_names:
        phase_success = True
        for function in phase_functions[phase_name]:
            try:
                phase_success = phase_success and (function() is not False)
            except AssertionException:
                phase_success = False
            except SandboxStudentCodeException:
                phase_success = False
        if not phase_success:
            break
        
    #for f in report.feedback:
    #    print("\t", f, f.mistake, f.misconception)
    if not report['assertions']['failures'] and phase_success and set_success:
        report.set_success()
    
    _reset_phases(report)
    
def _add_phase(phase_name, function, report=None):
    if report is None:
        report = MAIN_REPORT
    phase_functions = report['assertions']['phase_functions']
    phases = report['assertions']['phases']
    if phase_name not in phase_functions:
        phase_functions[phase_name] = []
        phases.append(phase_name)
    phase_functions[phase_name].append(function)
        
def _add_relationships(befores, afters, report=None):
    if report is None:
        report = MAIN_REPORT
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
