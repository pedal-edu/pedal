from pedal.cait.cait_api import parse_program
from pedal.cait.cait_node import CaitNode
from pedal.core.commands import gently, explain
from pedal.core.feedback import AtomicFeedbackFunction, CompositeFeedbackFunction
from pedal.core.location import Location
from pedal.core.report import MAIN_REPORT
from pedal.utilities.operators import COMPARE_OP_NAMES, BIN_OP_NAMES, BOOL_OP_NAMES, UNARY_OP_NAMES


def is_top_level(ast_node: CaitNode, report=MAIN_REPORT) -> bool:
    """
    Determines if the `ast_node` is at the top-level of the program.
    Correctly handles expression statements (so a print call on its own will be
    considered a statement, even though its technically an expression).

    Args:
        ast_node (CaitNode): The CaitNode to check

    Returns:
        bool: Whether the node is from the top level
    """
    ast = parse_program(report=MAIN_REPORT)
    for element in ast.body:
        if element.ast_name == "Expr":
            if element.value == ast_node:
                return True
        elif element == ast_node:
            return True
    return False


@AtomicFeedbackFunction(
    message_template="You have defined a function inside of another block. For instance, you may "
    "have placed it inside another function definition, or inside of a loop. Do not nest your function "
    "definition!",
    title="Don't Nest Functions",
    justification="Found a FunctionDef that was not at the top-level.",
)
def no_nested_function_definitions(muted=False, report=MAIN_REPORT) -> bool:
    """
    Returns `True` if there are any functions defined inside of other functions.
    Also attaches feedback, although that can be muted.

    Returns:
        bool: Returns whether there is a nested definition
    """
    ast = parse_program(report=MAIN_REPORT)
    defs = ast.find_all("FunctionDef")
    for a_def in defs:
        if not is_top_level(a_def):
            gently(
                no_nested_function_definitions.text_template,
                label="no_nested_function_definitions",
                muted=muted,
                report=MAIN_REPORT,
            )
            return False
    return True


def function_prints(function_name: str = None, report=MAIN_REPORT) -> bool:
    """
    Determines if there is a print statement inside of any functions. If `function_name` is given,
    then only that function will be checked.

    Returns:
        bool: Whether there is a print inside the function.
    """
    ast = parse_program(report=report)
    defs = ast.find_all("FunctionDef")
    for a_def in defs:
        if function_name is not None and a_def.name != function_name:
            continue
        all_calls = a_def.find_all("Call")
        for a_call in all_calls:
            if a_call.func.ast_name == "Name":
                if a_call.func.id == "print":
                    return True
    return False


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
    if root is None:
        root = parse_program(report=report)
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
    """
    Returns the number of times that the given function name is called.
    """
    return len(find_function_calls(name, report=report))


def only_printing_variables(report=MAIN_REPORT) -> bool:
    """
    Determines whether the user is only printing variables, as opposed to
    literal values.

    """
    ast = parse_program(report=report)
    all_calls = ast.find_all("Call")
    for a_call in all_calls:
        if a_call.func.ast_name == "Name" and a_call.func.id == "print":
            for arg in a_call.args:
                if arg.ast_name != "Name":
                    return False
                elif arg.id in ("True", "False", "None"):
                    return False
    return True


def find_prior_initializations(node, report=MAIN_REPORT) -> [CaitNode]:
    """

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


# TODO: Fill in other returning methods, add in returning funtions
RETURNING_METHODS = (
    "replace",
    "strip",
    "lstrip",
    "rstrip",
    "split",
    "upper",
    "lower",
    "title",
)


@AtomicFeedbackFunction(
    title="Did Not Use Function's Return Value",
    message_template="It looks like you called the {kind} `{name}` on {location.line}, but failed to store the result in a variable or use it in an expression. You should remember to use the result!",
)
def prevent_unused_result(
    muted=False, report=MAIN_REPORT, returning_methods=RETURNING_METHODS
) -> [CaitNode]:
    """

    Returns a list of any function calls where the function being called
    typically has a return value that should be assigned or used in an
    expression, but was instead thrown away.

    """
    ast = parse_program(report=report)
    exprs = ast.find_all("Expr")
    returns = []
    for expr in exprs:
        if expr.value.ast_name == "Call":
            kind = "function"
            continue
        else:
            kind = "method"
        a_call = expr.value
        if a_call.func.ast_name != "Attribute":
            continue
        method_name = a_call.func.attr
        if method_name == "append":
            pass
        elif method_name in prevent_unused_result.methods:
            fields = {
                "location": Location.from_ast(expr),
                "kind": kind,
                "name": a_call.func.attr,
            }
            gently(
                prevent_unused_result.message_template.format(**fields),
                label=prevent_unused_result.label,
                title=prevent_unused_result.title,
                fields=fields,
                muted=muted, report=report
            )
            returns.append(a_call)
    return returns


@AtomicFeedbackFunction(
    title="Builtin Usage",
    message_template="You cannot use the builtin function `{name}`.",
)
def prevent_builtin_usage(function_names: [str], muted: bool = False, report=MAIN_REPORT) -> str:
    """

    Determines the name of the first function in `function_names` that is
    called, or returns `None`; also attaches feedback.

    """
    # Prevent direction calls
    ast = parse_program(report=report)
    all_calls = ast.find_all("Call")
    for a_call in all_calls:
        if a_call.func.ast_name == "Name":
            if a_call.func.id in function_names:
                fields = {"location": Location.from_ast(a_call), "name": a_call.func.id}
                explain(
                    prevent_builtin_usage.message_template.format(**fields),
                    fields=fields,
                    muted=muted,
                    label=prevent_builtin_usage.label,
                    title=prevent_builtin_usage.title,
                )
                return a_call.func.id
    return None


def find_negatives(root=None, report=MAIN_REPORT):
    """

    Returns all the occurrences of the given literal negative number in the source
    code. Can optionally filter at the given subtree.

    """
    if root is None:
        root = parse_program(report=report)
    return [
        -op.operand.n
        for op in root.find_all("UnaryOp")
        if op.op.ast_name == "USub" and op.operand.ast_name == "Num"
    ]


@AtomicFeedbackFunction(title="Do Not Use Literal Value")
def prevent_literal(*literals, muted=False, report=MAIN_REPORT):
    """
    Confirms that the literal is not in the code, returning False if it is not.
    
    Args:
        *literals (Any...): A series of literal values to look for.
    Returns:
        AstNode or False: If the literal is found in the code, then it is returned.
    """
    message = "Do not use the literal value <code>{}</code> in your code."
    ast = parse_program(report=report)
    str_values = [s.s for s in ast.find_all("Str")]
    num_values = [n.n for n in ast.find_all("Num")]
    negative_values = find_negatives(ast, report=report)
    name_values = [name.id for name in ast.find_all("Name")] + [
        name.value for name in ast.find_all("NameConstant")
    ]
    for literal in literals:
        if isinstance(literal, (int, float)):
            if literal in num_values or literal in negative_values:
                if not muted:
                    explain(message.format(repr(literal)), label=prevent_literal.label, title=prevent_literal.title, muted=muted, report=report)
                return literal
        elif isinstance(literal, str):
            if literal in str_values:
                if not muted:
                    explain(message.format(repr(literal)), label=prevent_literal.label, title=prevent_literal.title, muted=muted, report=report)
                return literal
        elif literal in (True, False, None):
            if str(literal) in name_values:
                if not muted:
                    explain(message.format(repr(literal)), label=prevent_literal, title=prevent_literal.title, muted=muted, report=report)
                return literal
    return False


@AtomicFeedbackFunction(title="Missing Literal")
def ensure_literal(*literals, muted=False, report=MAIN_REPORT):
    """
    Confirms that the literal IS in the code, returning False if it is not.
    
    Args:
        *literals (Any...): A series of literal values to look for.
    Returns:
        AstNode or False: If the literal is found in the code, then it is returned.
    """
    message = "You need the literal value <code>{}</code> in your code."
    ast = parse_program(report=report)
    str_values = [s.s for s in ast.find_all("Str")]
    num_values = [n.n for n in ast.find_all("Num")]
    negative_values = find_negatives(ast, report=report)
    name_values = [str(name.id) for name in ast.find_all("Name")] + [
        str(name.value) for name in ast.find_all("NameConstant")
    ]
    for literal in literals:
        if literal in (True, False, None):
            if str(literal) not in name_values:
                if not muted:
                    explain(message.format(repr(literal)), label=ensure_literal.label, title=ensure_literal.title, muted=muted, report=report)
                return True
        elif isinstance(literal, (int, float)):
            if literal not in num_values and literal not in negative_values:
                if not muted:
                    explain(message.format(repr(literal)), label=ensure_literal.label, title=ensure_literal.title, muted=muted, report=report)
                return literal
        elif isinstance(literal, str):
            if literal not in str_values:
                if not muted:
                    explain(message.format(repr(literal)), label=ensure_literal.label, title=ensure_literal.title, muted=muted, report=report)
                return literal
    return False


def prevent_advanced_iteration(muted=False, report=MAIN_REPORT):
    """

    """
    message = "You should not use a <code>while</code> loop to solve this problem."
    label = "while_usage"
    title = "Usage of <code>while</code>"
    ast = parse_program()
    if ast.find_all("While"):
        explain(message, label=label, title=title, muted=muted, report=report)
    return prevent_builtin_usage(
        [
            "sum",
            "map",
            "filter",
            "reduce",
            "len",
            "max",
            "min",
            "max",
            "sorted",
            "all",
            "any",
            "getattr",
            "setattr",
            "eval",
            "exec",
            "iter",
        ], muted=muted, report=report
    )


@AtomicFeedbackFunction(title="Missing Operator")
def ensure_operation(op_name, root=None, muted=False, report=MAIN_REPORT):
    """

    Determines if the given operator `op_name` is used anywhere, returning the
    node of it if it is. Otherwise, returns `None`. You can specify the operator
    as a string like `"+"` or `"<<"`. Supports all comparison, boolean, binary, and unary operators.

    """
    message = "You are not using the `{name}` operator.".format(name=op_name)
    if root is None:
        root = parse_program()
    result = find_operation(op_name, root)
    if not result:
        gently(message, label=ensure_operation.label,
               title=ensure_operation.title, muted=muted, report=report)
    return result


@AtomicFeedbackFunction(title="May Not Use Operator",
                        message_template="You may not use the `{name}` operator.")
def prevent_operation(op_name, root=None, muted=False, report=MAIN_REPORT):
    """

    Determines if the given operator `op_name` is not used anywhere, returning the
    node of it if it is. Otherwise, returns `None`. You can specify the operator
    as a string like `"+"` or `"<<"`. Supports all comparison, boolean, binary, and unary operators.

    """
    root = root or parse_program()
    result = find_operation(op_name, root)
    if result:
        fields = {'name': op_name, 'location': Location.from_ast(result)}
        gently(prevent_operation.message_template.format(**fields),
               label=prevent_operation.label, title=prevent_operation.title,
               fields=fields,
               muted=muted, report=report)
    return result


def find_operation(op_name, root=None, report=MAIN_REPORT):
    """

    Returns the first occurrence of the operator `op_name` in the source code.
    Otherwise returns `False`. You can specify the operator
    as a string like `"+"` or `"<<"`. Supports all comparison, boolean, binary, and unary operators.

    """
    root = root or parse_program()
    if op_name in COMPARE_OP_NAMES:
        compares = root.find_all("Compare")
        for compare in compares:
            for op in compare.ops:
                if op.ast_name == COMPARE_OP_NAMES[op_name]:
                    return compare
    elif op_name in BOOL_OP_NAMES:
        boolops = root.find_all("BoolOp")
        for boolop in boolops:
            if boolop.op_name == BOOL_OP_NAMES[op_name]:
                return boolop
    elif op_name in BIN_OP_NAMES:
        binops = root.find_all("BinOp")
        for binop in binops:
            if binop.op_name == BIN_OP_NAMES[op_name]:
                return binop
    elif op_name in UNARY_OP_NAMES:
        unaryops = root.find_all("UnaryOp")
        for unaryop in unaryops:
            if unaryop.op_name == UNARY_OP_NAMES[op_name]:
                return unaryop
    return False


@CompositeFeedbackFunction()
def ensure_assignment(variable_name, type=None, value=None, root=None, muted=False, report=MAIN_REPORT):
    """

    Consumes a variable name
    TODO: Implement the value parameter

    :param variable_name: The variable name the student is expected to define.
    :type variable_name: str
    :param type: The string type of the node on the right side of the
                 assignment. Check GreenTreeSnakes (e.g., "Num", or "Str").
    :type type: str
    :return: False or str

    Args:
        root:
        value:
    """
    if root is None:
        root = parse_program()
    assignments = root.find_all("Assign")
    potentials = []
    for assign in assignments:
        if assign.targets[0].ast_name != "Name":
            continue
        if assign.targets[0].id == variable_name:
            potentials.append(assign)
            if type is None:
                return assign
            elif (
                type == "Bool"
                and assign.value.ast_name == "Name"
                and assign.value.id in ("True", "False")
            ):
                return assign
            elif (
                type == "Bool"
                and assign.value.ast_name == "NameConstant"
                and assign.value.value in (True, False)
            ):
                return assign
            elif assign.value.ast_name == type:
                return assign
    if potentials and potentials[0].value.ast_name not in (
        "Str",
        "Bool",
        "Num",
        "List",
        "Tuple",
    ):
        explain(
            (
                "You needed to assign a literal value to {variable}, but you "
                "created an expression instead."
            ).format(variable=variable_name),
            label="exp_vs_lit",
            title="Expression Instead of Literal",
            report=report, muted=muted
        )
    elif type is None:
        explain(
            (
                "You have not properly assigned anything to the variable " "{variable}."
            ).format(variable=variable_name),
            label="no_assign",
            title="No Proper Assignment",
            report=report, muted=muted
        )
    else:
        explain(
            ("You have not assigned a {type} to the variable {variable}." "").format(
                type=type, variable=variable_name
            ),
            label="type_assign",
            title="Unexpected Variable Type",
            report=report, muted=muted
        )
    return False
