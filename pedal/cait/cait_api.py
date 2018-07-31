from pedal.report import Report, MAIN_REPORT
from pedal.source import set_source
from pedal.tifa import tifa_analysis
from pedal.cait.stretchy_tree_matching import *


class Cait:
    def __init__(self, std_code=None, report=None):
        if report is None and std_code is None:
            self.report = MAIN_REPORT
        elif report is not None and std_code is not None:
            raise Exception("New code should generate new reports")
        elif std_code is not None:
            self.report = Report()
            set_source(std_code, self.report)

        if 'cait' not in self.report:
            self._initialize_report()

    def _initialize_report(self):
        '''
        Initialize a successful report with possible set of issues.
        '''
        if self.report["source"]["success"]:
            std_ast = self.report['source']['ast']
            self.report['cait'] = {}
            self.report['cait']['std_ast'] = EasyNode(std_ast)


# noinspection PyBroadException
def parse_program():
    """Parses student code (attempts to retrieve from TIFA?)

    :return: student AST
    """
    try:
        std_easy = MAIN_REPORT['cait']['std_ast']
    except KeyError:
        if MAIN_REPORT["source"]["success"]:
            std_ast = MAIN_REPORT['source']['ast']
            MAIN_REPORT['cait']['matcher'] = None
        else:
            MAIN_REPORT.attach("No source code found", tool='cait', 
                               category='analyzer')
            std_ast = ast.parse('')
        MAIN_REPORT['cait']['std_ast'] = EasyNode(std_ast)
        std_easy = MAIN_REPORT['cait']['std_ast']
    return std_easy


def def_use_error(node, report=None):
    """Checks if node is a name and has a def_use_error

    :param node: student AST name node
    :param report: The report object being used for analysis
    :return: True if the given name has a def_use_error
    """
    cait_obj = Cait(report)
    if not isinstance(node, str) and node.ast_name != "Name":
        raise TypeError
    def_use_vars = cait_obj.report['tifa']['issues']['Initialization Problem']
    if not isinstance(node, str):
        node_id = node
    else:
        node_id = node.id
    has_error = False
    for issue in def_use_vars:
        name = issue['name']
        if name == node_id:
            has_error = True
            break
    return has_error


# noinspection PyBroadException
def data_type(node, report=None):
    """

    :param node: EasyNode/ast node whose type to retrieve
    :param report: The report object to retrieve the information from
    :return: the type of the object (Tifa type) or None if a type doesn't exist
    """
    cait_obj = Cait(report)
    if not isinstance(node, str) and node.ast_name != "Name":
        raise TypeError
    if isinstance(node, str):
        node_id = node
    else:
        node_id = node.id
    return cait_obj.report['tifa']["top_level_variables"][node_id].type


def find_match(ins_code, std_code=None, report=None):
    """Apply Tree Inclusion and return first match

    :param ins_code: Instructor defined pattern
    :param std_code: Student code
    :return: First match of tree inclusion of instructor in student or None
    """
    matches = find_matches(ins_code=ins_code, std_code=std_code, report=report)
    if matches:
        return matches[0]
    else:
        return None


def find_matches(ins_code, std_code=None, report=None):
    """Apply Tree Inclusion and return all matches

    :param ins_code: Instructor pattern
    :param std_code: Student Code
    :return: All matches of tree inclusion of instructor in student
    """
    cait_obj = Cait(std_code=std_code, report=report)
    std_code = cait_obj.report['source']['code']
    matcher = StretchyTreeMatcher(ins_code)
    cait_obj.report['cait']['matcher'] = matcher
    matches = cait_obj.report['cait']['matcher'].find_matches(std_code)
    return matches
