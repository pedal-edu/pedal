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
./pedal command line interface
    simple example (single ICS, single student file)
    unit test a given curriculum
    regrade some assignments, spit out subject/assignment/context
    get summary stats from ProgSnap file
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
