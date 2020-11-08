"""
Environments are there to simplify:

* Setting up a submission
* Running "default" tools in a preconfigured way
* Adjusting output as needed

Environments
    BlockPy
    VPL
    Jupyter
    GradeScope
    WebCAT
    ...

"""


'''
def default_pipeline(tifa=False, cait=True, sandbox=True):
    next_section()
    results = []
    if tifa:
        results.append(tifa_analysis())
    if cait:
        results.append(parse_program())
    if sandbox:
        results.append(execute())
    return tuple(results)
'''

from pedal.environments.standard import setup_environment

ALL_ENVIRONMENTS = [
    'blockpy', 'gradescope', 'jupyter', 'standard', 'vpl'
]