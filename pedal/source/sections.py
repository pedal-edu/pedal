from pedal.report import MAIN_REPORT
import ast


#def move_to_section(section_number, name, report=None):
#    pass

def _calculate_section_number(section_index):
    return int((section_index+1)/2)

def next_section(name="", report=None):
    if report is None:
        report = MAIN_REPORT
    source = report['source']
    if not report['source']['success']:
        return False
    source['section'] += 2
    section_index = source['section']
    section_number = _calculate_section_number(section_index)
    sections = source['sections']
    found = len(source['sections'])
    if section_index < found:
        if source['independent']:
            source['code'] = ''.join(sections[section_index])
            old_code = ''.join(sections[:section_index])
            source['line_offset'] = len(old_code.split("\n"))-1
        else:
            source['code'] = ''.join(sections[:section_index + 1])
        report.group = section_index
    else:
        report.attach('Syntax error', category='Syntax', tool='Source',
                      mistake=("Tried to advance to next section but the "
                               "section was not found. Tried to load section "
                               "{count}, but there were only {found} sections."
                               ).format(count=section_number, found=found))

def check_section_exists(section_number, report=None):
    """
    Checks that the right number of sections exist. The prologue before the
    first section is 0, while subsequent ones are 1, 2, 3, etc. 
    So if you have 3 sections in your code plus the prologue,
    you should pass in 3 and not 4 to verify that all of them exist.
    """
    if report is None:
        report = MAIN_REPORT
    if not report['source']['success']:
        return False
    found = int((len(report['source']['sections']) - 1) / 2)
    if section_number > found:
        report.attach('Syntax error', category='Syntax', tool='Source',
                      group=report['source']['section'],
                      mistake=("Incorrect number of sections in your file. "
                               "Expected {count}, but only found {found}"
                               ).format(count=section_number, found=found))


def verify_section(report=None):
    if report is None:
        report = MAIN_REPORT
    source = report['source']
    if not source['success']:
        return False
    code = source['code']
    try:
        parsed = ast.parse(code, source['filename'])
        source['ast'] = parsed
    except SyntaxError as e:
        report.attach('Syntax error', category='Syntax', tool='Source',
                      group=source['section'],
                      mistake={'message': "Invalid syntax on line "
                                          + str(e.lineno+source['line_offset']),
                               'error': e,
                               'position': {"line": e.lineno}})
        source['success'] = False
        if 'ast' in source:
            del source['ast']
    return source['success']


class _finish_section:
    def __init__(self, number, *functions):
        if isinstance(number, int):
            self.number = number
        else:
            self.number = -1
            functions = [number] + list(functions)
        self.functions = functions
        for function in functions:
            self(function, False)

    def __call__(self, f=None, quiet=True):
        if f is not None:
            f()
        if quiet:
            print("\tNEXT SECTION")

    def __enter__(self):
        pass

    def __exit__(self, x, y, z):
        print("\tNEXT SECTION")
        # return wrapped_f


def finish_section(number, *functions, **kwargs):
    if 'next_section' in kwargs:
        next_section = kwargs['next_section']
    else:
        next_section = False
    if len(functions) == 0:
        x = _finish_section(number, *functions)
        x()
    else:
        result = _finish_section(number, *functions)
        if next_section:
            print("\tNEXT SECTION")
        return result


def section(number):
    """
    """
    pass


def precondition(function):
    pass


def postcondition(function):
    pass
