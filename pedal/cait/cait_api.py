"""

.. csv-table:: Cait Report Data
    :header: "Field", "Type", "Initial", "Description"
    :widths: 20, 20, 20, 40

    "ast", "CaitNode", "None", "The CaitNode tree that was most recently parsed out."
    "cache", "{str: CaitNode}", "{}", "A dictionary mapping previously parsed code to CaitNode trees."
    "success", "bool", "True", "Whether the most recent parsing was successful."
    "error", "Exception", "None", "The most recent exception, or None."

"""
from pedal.cait.constants import TOOL_NAME
from pedal.core.commands import system_error
from pedal.core.report import Report, MAIN_REPORT
from pedal.cait.stretchy_tree_matching import StretchyTreeMatcher
from pedal.cait.cait_node import CaitNode
import ast

# TODO: Decide if we want the imports; seems like overkill?
SOURCE_TOOL_NAME = 'source'
TIFA_TOOL_NAME = 'tifa'


class CaitException(Exception):
    pass


def _parse_source(code, report=MAIN_REPORT):
    """
    Parses the given code and returns its Cait representation. If the parse was
    unsuccessful, it attaches the error to the report.

    Args:
        code (str): A string of Python code.
        report (Report): A Report to store information in.
    Returns:
        AstNode: The parsed AST reprensetation, or None
    """
    try:
        parsed = ast.parse(code)
        report[TOOL_NAME]['success'] = True
        report[TOOL_NAME]['error'] = None
    except SyntaxError as e:
        system_error(TOOL_NAME, "Could not parse code:" + str(e), report=report)
        report[TOOL_NAME]['success'] = False
        report[TOOL_NAME]['error'] = e
        return ast.parse("")
    return parsed


def reparse_if_needed(student_code=None, report=MAIN_REPORT):
    """
    Retrieves the current report for CAIT. If there is no CAIT report, it will
    generate one. If source code is given, that will be used instead of the
    report's submission.

    Args:
        student_code (str): The code to parse into the a CaitNode tree. If
            None, then it will use the code in the report's submission.
        report (Report): The report to attach data to.

    Returns:
        dict: Returns the Cait Report
    """
    cait = report[TOOL_NAME]
    if student_code is not None:
        if student_code in cait['cache']:
            cait['ast'] = cait['cache'][student_code]
            return cait
        else:
            student_ast = _parse_source(student_code, report=report)
    else:
        student_code = report.submission.main_code
        # Have we already parsed this code?
        if student_code in cait['cache']:
            cait['ast'] = cait['cache'][student_code]
            return cait
        # Try to steal parse from Source module, if available
        if report[SOURCE_TOOL_NAME]['success']:
            student_ast = report[SOURCE_TOOL_NAME]['ast']
        else:
            student_ast = _parse_source(student_code, report=report)
    cait['ast'] = cait['cache'][student_code] = CaitNode(student_ast, report=report)
    return cait


def require_tifa(self):
    """
    Confirms that TIFA was run successfully, otherwise raises a
    CaitException.

    TODO: Is this deprecated?
    """
    if not self.report[TIFA_TOOL_NAME]['success']:
        system_error(TOOL_NAME, "TIFA was not successfully run prior to CAIT.")
        raise CaitException("TIFA was not run prior to CAIT.")


# noinspection PyBroadException
def parse_program(student_code=None, report=MAIN_REPORT):
    """
    Parses student code and produces a CAIT representation.

    Args:
        student_code (str): The student source code to parse. If None, defaults
            to the code within the Source tool of the given Report.
        report (Report): The report to attach data to. Defaults to MAIN_REPORT.

    Returns:
        CaitNode: A CAIT-enhanced representation of the root Node.
    """
    cait_report = reparse_if_needed(student_code, report=report)
    return cait_report['ast']


def expire_cait_cache(report=MAIN_REPORT):
    """
    Deletes the most recent CAIT run and any cached CAIT parses.

    Args:
        report (Report): The report to attach data to. Defaults to MAIN_REPORT.
    """
    report['cait']['ast'] = None
    report['cait']['cache'] = {}


def def_use_error(node, report=MAIN_REPORT):
    """
    Checks if node is a name and has a def_use_error

    Args:
        node (str or AstNode or CaitNode): The Name node to look up.
        report (Report): The report to attach data to. Defaults to MAIN_REPORT.
    Returns:
        True if the given name has a def_use_error
    """
    if not isinstance(node, str) and node.ast_name != "Name":
        raise TypeError
    from pedal.tifa.commands import get_issues
    from pedal.tifa.feedbacks import initialization_problem
    def_use_issues = get_issues(initialization_problem)
    if not isinstance(node, str):
        node_id = node.id
    else:
        node_id = node
    has_error = False
    for issue in def_use_issues:
        name = issue.fields['name']
        if name == node_id:
            has_error = True
            break
    return has_error


# noinspection PyBroadException
def data_state(node, report=MAIN_REPORT):
    """
    Determines the Tifa State of the given node.

    Args:
        node (str or AstNode or CaitNode): The Name node to look up in TIFA.
        report (Report): The report to attach data to. Defaults to MAIN_REPORT.
    Returns:
        The State of the object (Tifa State) or None if it doesn't exist
    """
    if not isinstance(node, str) and node.ast_name != "Name":
        raise TypeError
    if isinstance(node, str):
        node_id = node
    else:
        node_id = node.id
    try:
        return report[TIFA_TOOL_NAME]["latest"].top_level_variables[node_id]
    except KeyError:
        return None


def data_type(node, report=MAIN_REPORT):
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


def find_match(pattern, student_code=None, report=MAIN_REPORT, cut=False, use_previous=None):
    """
    Apply Tree Inclusion and return the first match of the `pattern` in the
    `student_code`.

    Args:
        pattern (str): The CaitExpression to match against.
        student_code (str): The string of student code to check against.
            Defaults to the code of the Source tool in the Report.
        report (Report): The report to attach data to.
        cut (bool): Set to true to trim root to first branch
        use_previous (AstMap): If user wants to continue off of a previously found match
    Returns:
        CaitNode or None: The first matching node for the given pattern, or
            None if nothing was found.
    """
    matches = find_matches(pattern=pattern, student_code=student_code,
                           report=report, cut=cut, use_previous=use_previous)
    if matches:
        return matches[0]
    else:
        return None


def find_matches(pattern, student_code=None, cut=False, report=MAIN_REPORT, use_previous=None):
    """
    Apply Tree Inclusion and return all matches of the `pattern` in the
    `student_code`.

    Args:
        pattern (str): The CaitExpression to match against.
        student_code (str): The string of student code to check against.
        report (Report): The report to attach data to.
        cut (bool): Set to true to trim root to first branch
        use_previous (AstMap): If user wants to continue off of a previously found match
    Returns:
        list[pedal.cait.ast_map.AstMap]: All matching nodes for the given pattern.
    """
    cait_report = reparse_if_needed(student_code, report)
    if not cait_report['success']:
        return []
    student_ast = cait_report['ast']
    matcher = StretchyTreeMatcher(pattern, report=report)
    return matcher.find_matches(student_ast, use_previous=use_previous)


def find_submatches(pattern, student_code, is_mod=False, report=MAIN_REPORT):
    """
    Incomplete.
    """
    return find_expr_sub_matches(pattern, student_code, is_mod, report=report)


def find_expr_sub_matches(pattern, student_code, is_mod=False, report=MAIN_REPORT):
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
    is_node = isinstance(pattern, CaitNode)
    if not isinstance(pattern, str) and not is_node:
        raise TypeError("pattern expected str or CaitNode, found {0}".format(type(pattern)))
    matcher = StretchyTreeMatcher(pattern, report=report)
    if (not is_node and not is_mod) and len(matcher.root_node.children) != 1:
        raise ValueError("pattern does not evaluate to a singular statement")
    return matcher.find_matches(student_code, check_meta=False)


def find_asts(node_name: str, student_code=None, report=MAIN_REPORT):
    """
    Find all occurrences of the given AST node, based on the name of the AST
    node (e.g., `"For"` or `"FunctionDef"`).

    Args:
        node_type: the string representing the "type" of node to look for
        student_code (str): Optionally, different code to parse and search.
        report: defaults to MAIN_REPORT unless another one is given.

    Returns:
        a list of Ast Nodes (cait_nodes) of self that are of the specified type (including self if self
                meets that criteria)

    Returns:

    """
    cait_report = reparse_if_needed(student_code, report)
    if not cait_report['success']:
        return []
    student_ast = cait_report['ast']
    return student_ast.find_all(node_name)


def reset(report=MAIN_REPORT):
    """

    Args:
        report:

    Returns:

    """
    report[TOOL_NAME] = {
        'success': True,
        'error': None,
        'ast': None,
        'cache': {}
    }
    return report[TOOL_NAME]


Report.register_tool(TOOL_NAME, reset)
