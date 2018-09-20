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
        """
        Initialize a successful report with possible set of issues.
        """
        if self.report["source"]["success"]:
            std_ast = self.report['source']['ast']
            self.report['cait'] = {}
            self.report['cait']['std_ast'] = EasyNode(std_ast)
            tifa_analysis(report=self.report)


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
    try:
        def_use_vars = cait_obj.report['tifa']['issues']['Initialization Problem']
    except KeyError:
        return False
    if not isinstance(node, str):
        node_id = node.id
    else:
        node_id = node
    has_error = False
    for issue in def_use_vars:
        name = issue['name']
        if name == node_id:
            has_error = True
            break
    return has_error


# noinspection PyBroadException
def data_state(node, report=None):
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
    return cait_obj.report['tifa']["top_level_variables"][node_id]


def data_type(node, report=None):
    return data_state(node, report=report).type


def find_match(ins_code, std_code=None, report=None, cut=False):
    """Apply Tree Inclusion and return first match

    :param ins_code: Instructor defined pattern
    :param std_code: Student code
    :param report: The report associated with the find_match function
    :param cut: set to true to trim root to first branch
    :return: First match of tree inclusion of instructor in student or None
    """
    matches = find_matches(ins_code=ins_code, std_code=std_code, report=report, cut=cut)
    if matches:
        return matches[0]
    else:
        return None


def find_matches(ins_code, std_code=None, report=None, cut=False):
    """Apply Tree Inclusion and return all matches

    :param ins_code: Instructor pattern
    :param std_code: Student Code
    :param report: the report to use for finding matches
    :param cut: set to true to trim root to first branch
    :return: All matches of tree inclusion of instructor in student
    """
    cait_obj = Cait(std_code=std_code, report=report)
    # TODO: Check to make sure the code actually parsed
    try:
        std_code = cait_obj.report['cait']['std_ast']
        matcher = StretchyTreeMatcher(ins_code)
        cait_obj.report['cait']['matcher'] = matcher
        matches = cait_obj.report['cait']['matcher'].find_matches(std_code, cut=cut)
        return matches
    except KeyError:
        return False


def find_expr_sub_matches(ins_expr, std_expr, as_expr=True, is_mod=False, cut=False):
    """Finds ins_expr in std_expr
    # TODO: Add code to make ins_expr accept EasyNodes
    # TODO: Make this function without so much meta knowledge
    :param ins_expr: the expression to find (str that MUST evaluate to a Module node with a single child)
    :param std_expr: student subtree
    :param as_expr: whether it's an expression match or not, experimental
    :param is_mod: currently hack for multiline sub matches
    :param cut: flag for cutting off root until a branch occurs
    :return: a list of matches or False if no matches found
    """
    if not isinstance(ins_expr, str):
        raise TypeError("ins_expr expected str, found {0}".format(type(ins_expr)))
    matcher = StretchyTreeMatcher(ins_expr)
    if not is_mod and len(matcher.rootNode.children) != 1:
        raise ValueError("ins_expr does not evaluate to a singular statement")
    else:
        if not is_mod:
            new_root = matcher.rootNode.children[0]
            if as_expr and new_root.ast_name != "Expr":
                raise ValueError("ins_expr does not evaluate to an Expr node or singular statement")
            else:
                matcher.rootNode = new_root
    return matcher.find_matches(std_expr, check_meta=False, cut=cut)
