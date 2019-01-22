
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
