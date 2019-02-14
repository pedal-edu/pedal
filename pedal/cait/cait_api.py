from pedal.report import MAIN_REPORT
from pedal.cait.stretchy_tree_matching import StretchyTreeMatcher
from pedal.cait.cait_node import CaitNode
import ast


class CaitException(Exception):
    pass


"""
CaitReport:
    A collection of information from the latest CAIT run.

    Attrs:
        ast: The CaitNode tree that was most recently parsed out.
        cache[str:CaitNode]: A dictionary mapping student code (str) to
            parsed representations.
        success: Whether there have been any errors so far.
        error: The exception that occurred, or None if no exception so far.
"""


def _parse_source(code, cait_report):
    """
    Parses the given code and returns its Cait representation. If the parse was
    unsuccessful, it attaches the error to the report.

    Args:
        code (str): A string of Python code.
        cait_report (dict): A Cait Report to store information in.
    Returns:
        AstNode: The parsed AST reprensetation, or None
    """
    try:
        parsed = ast.parse(code)
    except SyntaxError as e:
        cait_report['success'] = False
        cait_report['error'] = e
        return ast.parse("")
    return parsed


def _load_cait(student_code, report):
    """
    Retrieves the current report for CAIT. If there is no CAIT report, it will
    generate one. If source code is given, that will be used instead of the
    report's source code.

    Args:
        student_code (str): The code to parse into the a CaitNode tree. If
            None, then it will use the code in the report's Source tool.
        report (Report): The report to attach data to.

    Returns:
        dict: Returns the Cait Report
    """
    if 'cait' not in report:
        report['cait'] = {'success': True, 'error': None,
                          'ast': None, 'cache': {}}
    cait = report['cait']
    if student_code is not None:
        if student_code in cait['cache']:
            cait['ast'] = cait['cache'][student_code]
            return cait
        else:
            student_ast = _parse_source(student_code, cait)
    elif report['source']['success']:
        student_code = report['source']['code']
        if student_code in cait['cache']:
            cait['ast'] = cait['cache'][student_code]
            return cait
        else:
            student_ast = report['source']['ast']
    else:
        report.attach("No source code found", tool='cait',
                      category='analyzer')
        cait['success'] = False
        cait['ast'] = CaitNode(ast.parse(""), report=report)
        return cait
    cait['ast'] = cait['cache'][student_code] = CaitNode(student_ast, report=report)
    return cait


def require_tifa(self):
    """
    Confirms that TIFA was run successfully, otherwise raises a
    CaitException.
    """
    if not self.report['tifa']['success']:
        raise CaitException("TIFA was not run prior to CAIT.")


# noinspection PyBroadException
def parse_program(student_code=None, report=None):
    """
    Parses student code and produces a CAIT representation.

    Args:
        student_code (str): The student source code to parse. If None, defaults
            to the code within the Source tool of the given Report.
        report (Report): The report to attach data to. Defaults to MAIN_REPORT.

    Returns:
        CaitNode: A CAIT-enhanced representation of the root Node.
    """
    if report is None:
        report = MAIN_REPORT
    cait_report = _load_cait(student_code, report)
    return cait_report['ast']


def expire_cait_cache(report=None):
    """
    Deletes the most recent CAIT run and any cached CAIT parses.

    Args:
        report (Report): The report to attach data to. Defaults to MAIN_REPORT.
    """
    if report is None:
        report = MAIN_REPORT
    report['cait']['ast'] = None
    report['cait']['cache'] = {}


def def_use_error(node, report=None):
    """
    Checks if node is a name and has a def_use_error

    Args:
        node (str or AstNode or CaitNode): The Name node to look up.
        report (Report): The report to attach data to. Defaults to MAIN_REPORT.
    Returns:
        True if the given name has a def_use_error
    """
    if report is None:
        report = MAIN_REPORT
    if not isinstance(node, str) and node.ast_name != "Name":
        raise TypeError
    try:
        def_use_vars = report['tifa']['issues']['Initialization Problem']
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
    Determines the Tifa State of the given node.

    Args:
        node (str or AstNode or CaitNode): The Name node to look up in TIFA.
        report (Report): The report to attach data to. Defaults to MAIN_REPORT.
    Returns:
        The State of the object (Tifa State) or None if it doesn't exist
    """
    if report is None:
        report = MAIN_REPORT
    if not isinstance(node, str) and node.ast_name != "Name":
        raise TypeError
    if isinstance(node, str):
        node_id = node
    else:
        node_id = node.id
    try:
        return report['tifa']["top_level_variables"][node_id]
    except KeyError:
        return None


def data_type(node, report=None):
    """
    Looks up the type of the node using Tifa's analysis.

    Args:
        node (str or AstNode or CaitNode): The Name node to look up in TIFA.
        report (Report): The report to attach data to. Defaults to MAIN_REPORT.
    Returns:
        The type of the object (Tifa type) or None if a type doesn't exist
    """
    state = data_state(node, report=report)
    if state is not None:
        return state.type
    return None


def find_match(pattern, student_code=None, report=None, cut=False):
    """
    Apply Tree Inclusion and return the first match of the `pattern` in the
    `student_code`.

    Args:
        pattern (str): The CaitExpression to match against.
        student_code (str): The string of student code to check against.
            Defaults to the code of the Source tool in the Report.
        report (Report): The report to attach data to.
        cut (bool): Set to true to trim root to first branch
    Returns:
        CaitNode or None: The first matching node for the given pattern, or
            None if nothing was found.
    """
    matches = find_matches(pattern=pattern, student_code=student_code,
                           report=report, cut=cut)
    if matches:
        return matches[0]
    else:
        return None


def find_matches(pattern, student_code=None, report=None, cut=False):
    """
    Apply Tree Inclusion and return all matches of the `pattern` in the
    `student_code`.

    Args:
        pattern (str): The CaitExpression to match against.
        student_code (str): The string of student code to check against.
        report (Report): The report to attach data to.
        cut (bool): Set to true to trim root to first branch
    Returns:
        List[CaitNode]: All matching nodes for the given pattern.
    """
    if report is None:
        report = MAIN_REPORT
    cait_report = _load_cait(student_code, report)
    if not cait_report['success']:
        return []
    student_ast = cait_report['ast']
    matcher = StretchyTreeMatcher(pattern, report=report)
    return matcher.find_matches(student_ast)


def find_submatches(pattern, student_code, is_mod=False):
    """
    Incomplete.
    """
    return find_expr_sub_matches(pattern, student_code, is_mod)


def find_expr_sub_matches(pattern, student_code, is_mod=False, report=None):
    """
    Finds pattern in student_code
    # TODO: Add code to make pattern accept CaitNodes
    # TODO: Make this function without so much meta knowledge
    Args:
        pattern: the expression to find (str that MUST evaluate to a Module node with a single child or an AstNode)
        student_code: student subtree
        is_mod (bool): currently hack for multiline sub matches
        report: defaults to MAIN_REPORT unless another one exists
    Returns:
        a list of matches or False if no matches found
    """
    if report is None:
        report = MAIN_REPORT
    is_node = isinstance(pattern, CaitNode)
    if not isinstance(pattern, str) and not is_node:
        raise TypeError("pattern expected str or CaitNode, found {0}".format(type(pattern)))
    matcher = StretchyTreeMatcher(pattern, report=report)
    if (not is_node and not is_mod) and len(matcher.root_node.children) != 1:
        raise ValueError("pattern does not evaluate to a singular statement")
    return matcher.find_matches(student_code, check_meta=False)
