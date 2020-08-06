"""
Helper functions for traversing through the code structure.
"""

from pedal.cait import parse_program
from pedal.core.report import MAIN_REPORT
from pedal.utilities.operators import COMPARE_OP_NAMES, BOOL_OP_NAMES, BIN_OP_NAMES, UNARY_OP_NAMES


def is_top_level(ast_node, report=MAIN_REPORT) -> bool:
    """
    Determines if the `ast_node` is at the top-level of the program.
    Correctly handles expression statements (so a print call on its own will be
    considered a statement, even though its technically an expression).

    Args:
        ast_node (pedal.cait.cait_node.CaitNode): The CaitNode to check
        report (pedal.core.report.Report):

    Returns:
        bool: Whether the node is from the top level
    """
    ast = parse_program(report=report)
    for element in ast.body:
        if element.ast_name == "Expr":
            if element.value == ast_node:
                return True
        elif element == ast_node:
            return True
    return False


def find_operation(op_name, root=None, report=MAIN_REPORT):
    """
    Returns all the occurrences of the operator `op_name` in the source code.
    You can specify the operator as a string like `"+"` or `"<<"`.
    Supports all comparison, boolean, binary, and unary operators.
    """
    root = root or parse_program(report=report)
    found = []
    if op_name in COMPARE_OP_NAMES:
        compares = root.find_all("Compare")
        for compare in compares:
            for op in compare.ops:
                if op.ast_name == COMPARE_OP_NAMES[op_name]:
                    found.append(compare)
    elif op_name in BOOL_OP_NAMES:
        boolops = root.find_all("BoolOp")
        for boolop in boolops:
            if boolop.op_name == BOOL_OP_NAMES[op_name]:
                found.append(boolop)
    elif op_name in BIN_OP_NAMES:
        binops = root.find_all("BinOp")
        for binop in binops:
            if binop.op_name == BIN_OP_NAMES[op_name]:
                found.append(binop)
    elif op_name in UNARY_OP_NAMES:
        unaryops = root.find_all("UnaryOp")
        for unaryop in unaryops:
            if unaryop.op_name == UNARY_OP_NAMES[op_name]:
                found.append(unaryop)
    return found


def find_function_calls(name: str, root=None, report=MAIN_REPORT):
    """
    Returns a list of CaitNodes representing all of the function calls that
    were found. This includes both methods and regular functions.

    Args:
        name (str): The name of the function to search.
        root: A subtree of a parse tree to revert to.
        report (Report): The name of the Report to refer to.

    Returns:
        List[CaitNode]: Relevant call nodes.
    """
    root = root or parse_program(report=report)
    all_calls = root.find_all("Call")
    calls = []
    for a_call in all_calls:
        if a_call.func.ast_name == "Attribute":
            if a_call.func.attr == name:
                calls.append(a_call)
        elif a_call.func.ast_name == "Name":
            if a_call.func.id == name:
                calls.append(a_call)
    return calls


def function_is_called(name: str, report=MAIN_REPORT) -> int:
    """ DEPRECATED """
    return len(find_function_calls(name, report=report))


def find_prior_initializations(node, report=MAIN_REPORT):
    """
    DEPRECATED

    Given a Name node, returns a list of all the assignment
    statements that incorporate that Name node prior to that line. Returns
    None if no Name is given.

    """
    if node.ast_name != "Name":
        return None
    ast = parse_program(report=report)
    assignments = ast.find_all("Assign")
    cur_line_no = node.lineno
    all_assignments = []
    for assignment in assignments:
        if assignment.has(node):
            if assignment.lineno < cur_line_no:
                all_assignments.append(assignment)
    return all_assignments


def find_function_definition(name, root=None, report=MAIN_REPORT):
    """
    Finds the given function definition based on the given ``name``.

    Args:
        name (str): The name of the function.
        root: A subtree of a parse tree to revert to.
        report (Report): The name of the Report to refer to.

    Returns:
        :py:class:`pedal.cait.cait_node.CaitNode`: The first occurrence of a
            function with the given name.
    """
    root = root or parse_program(report=report)
    defs = root.find_all('FunctionDef')
    for a_def in defs:
        if a_def._name == name:
            return a_def
    return None
