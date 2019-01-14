from pedal.report import MAIN_REPORT
import ast

def next_section(name="", report=None):
    if report is None:
        report = MAIN_REPORT
    if not report['source']['success']:
        return False
    report['source']['section'] += 2
    section = report['source']['section']
    found = len(report['source']['sections'])
    if section < found:
        report['source']['code'] = ''.join(report['source']['sections'][:section + 1])
        report.group = report['source']['section']
    else:
        report.attach('Syntax error', category='Syntax', tool='Source',
                      mistake=("Tried to advance to next section but the "
                               "section was not found. Tried to load section "
                               "{count}, but there were only {found} sections."
                               ).format(count=int(section / 2), found=found))


def count_sections(count, report=None):
    '''
    Checks that the right number of sections exist. This is not counting the
    prologue, before the first section. So if you have 3 sections in your code,
    you should pass in 3 and not 4.
    '''
    if report is None:
        report = MAIN_REPORT
    if not report['source']['success']:
        return False
    found = int((len(report['source']['sections']) - 1) / 2)
    if count != found:
        report.attach('Syntax error', category='Syntax', tool='Source',
                      group=report['source']['section'],
                      mistake=("Incorrect number of sections in your file. "
                               "Expected {count}, but only found {found}"
                               ).format(count=count, found=found))


def verify_section(report=None):
    if report is None:
        report = MAIN_REPORT
    if not report['source']['success']:
        return False
    code = report['source']['code']
    try:
        parsed = ast.parse(code, report['source']['filename'])
        report['source']['ast'] = parsed
    except SyntaxError as e:
        report.attach('Syntax error', category='Syntax', tool='Source',
                      group=report['source']['section'],
                      mistake={'message': "Invalid syntax on line "
                                          + str(e.lineno),
                               'error': e,
                               'position': {"line": e.lineno}})
        report['source']['success'] = False
        if 'ast' in report['source']:
            del report['source']['ast']
    return report['source']['success']
