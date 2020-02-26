from pedal.cait.cait_api import parse_program
from pedal.core.commands import gently, explain


def is_top_level(ast_node):
    """

    Args:
        ast_node:

    Returns:

    """
    ast = parse_program()
    for element in ast.body:
        print(element.ast_name, ast_node.ast_name, element == ast_node)
        if element.ast_name == 'Expr':
            if element.value == ast_node:
                return True
        elif element == ast_node:
            return True
    return False


def no_nested_function_definitions():
    """

    Returns:

    """
    ast = parse_program()
    defs = ast.find_all('FunctionDef')
    for a_def in defs:
        if not is_top_level(a_def):
            gently("You have defined a function inside of another block. For instance, you may have placed it inside "
                   "another function definition, or inside of a loop. Do not nest your function definition!",
                   label="no_nested_function_definitions")
            return False
    return True


def function_prints():
    """

    Returns:

    """
    ast = parse_program()
    defs = ast.find_all('FunctionDef')
    for a_def in defs:
        all_calls = a_def.find_all('Call')
        for a_call in all_calls:
            if a_call.func.ast_name == 'Name':
                if a_call.func.id == 'print':
                    return True
    return False


def find_function_calls(name, root=None):
    """

    Args:
        name:
        root:

    Returns:

    """
    if root is None:
        root = parse_program()
    all_calls = root.find_all('Call')
    calls = []
    for a_call in all_calls:
        if a_call.func.ast_name == 'Attribute':
            if a_call.func.attr == name:
                calls.append(a_call)
        elif a_call.func.ast_name == 'Name':
            if a_call.func.id == name:
                calls.append(a_call)
    return calls


def function_is_called(name):
    """

    Args:
        name:

    Returns:

    """
    return len(find_function_calls(name))


def no_nonlist_nums():
    """

    """
    pass


def only_printing_variables():
    """

    Returns:

    """
    ast = parse_program()
    all_calls = ast.find_all('Call')
    for a_call in all_calls:
        if a_call.func.ast_name == 'Name' and a_call.func.id == "print":
            for arg in a_call.args:
                if arg.ast_name != "Name":
                    return False
                elif arg.id in ('True', 'False', 'None'):
                    return False
    return True


def find_prior_initializations(node):
    """

    Args:
        node:

    Returns:

    """
    if node.ast_name != "Name":
        return None
    ast = parse_program()
    assignments = ast.find_all("Assign")
    cur_line_no = node.lineno
    all_assignments = []
    for assignment in assignments:
        if assignment.has(node):
            if assignment.lineno < cur_line_no:
                all_assignments.append(assignment)
    return all_assignments


def prevent_unused_result():
    """

    """
    ast = parse_program()
    exprs = ast.find_all('Expr')
    for expr in exprs:
        if expr.value.ast_name == "Call":
            a_call = expr.value
            if a_call.func.ast_name == 'Attribute':
                if a_call.func.attr == 'append':
                    pass
                elif a_call.func.attr in ('replace', 'strip', 'lstrip', 'rstrip', 'split'):
                    gently("Remember! You cannot modify a string directly. Instead, you should assign the result back "
                           "to the string variable.", label="attempted_string_mutate")


def prevent_builtin_usage(function_names):
    """

    Args:
        function_names:

    Returns:

    """
    message = "You cannot use the builtin function <code>{}</code>."
    label = "builtin_use"
    title = "Builtin Usage"
    # Prevent direction calls
    ast = parse_program()
    all_calls = ast.find_all('Call')
    for a_call in all_calls:
        if a_call.func.ast_name == 'Name':
            if a_call.func.id in function_names:
                explain(message.format(a_call.func.id), label=label, title=title)
                return a_call.func.id
    return None


def find_negatives(root=None):
    """

    Args:
        root:

    Returns:

    """
    if root is None:
        root = parse_program()
    return [-op.operand.n for op in root.find_all("UnaryOp")
            if op.op.ast_name == "USub" and op.operand.ast_name == "Num"]


# TODO: UGLY HACK. This is to avoid muted=False kwargs in the following
#       functions. Apparently skulpt doesn't support this syntax.
muted = False


def prevent_literal(*literals):
    """
    Confirms that the literal is not in the code, returning False if it is not.
    
    Args:
        *literals (Any...): A series of literal values to look for.
    Returns:
        AstNode or False: If the literal is found in the code, then it is returned.
    """
    message = "Do not use the literal value <code>{}</code> in your code."
    label = "hard_code"
    title = "Hard Coding"
    ast = parse_program()
    str_values = [s.s for s in ast.find_all("Str")]
    num_values = [n.n for n in ast.find_all("Num")]
    negative_values = find_negatives(ast)
    name_values = ([name.id for name in ast.find_all("Name")]+
                   [name.value for name in ast.find_all("NameConstant")])
    for literal in literals:
        if isinstance(literal, (int, float)):
            if literal in num_values or literal in negative_values:
                if not muted:
                    explain(message.format(repr(literal)), label=label, title=title)
                return literal
        elif isinstance(literal, str):
            if literal in str_values:
                if not muted:
                    explain(message.format(repr(literal)), label=label, title=title)
                return literal
        elif literal in (True, False, None):
            if str(literal) in name_values:
                if not muted:
                    explain(message.format(repr(literal)), label=label, title=title)
                return literal
    return False


def ensure_literal(*literals):
    """
    Confirms that the literal IS in the code, returning False if it is not.
    
    Args:
        *literals (Any...): A series of literal values to look for.
    Returns:
        AstNode or False: If the literal is found in the code, then it is returned.
    """
    message = "You need the literal value <code>{}</code> in your code."
    label = "missing_literal"
    title = "Missing Literal"
    ast = parse_program()
    str_values = [s.s for s in ast.find_all("Str")]
    num_values = [n.n for n in ast.find_all("Num")]
    negative_values = find_negatives(ast)
    name_values = ([str(name.id) for name in ast.find_all("Name")]+
                   [str(name.value) for name in ast.find_all("NameConstant")])
    for literal in literals:
        if literal in (True, False, None):
            if str(literal) not in name_values:
                if not muted:
                    explain(message.format(repr(literal)), label=label, title=title)
                return True
        elif isinstance(literal, (int, float)):
            if literal not in num_values and literal not in negative_values:
                if not muted:
                    explain(message.format(repr(literal)), label=label, title=title)
                return literal
        elif isinstance(literal, str):
            if literal not in str_values:
                if not muted:
                    explain(message.format(repr(literal)), label=label, title=title)
                return literal
    return False


def prevent_advanced_iteration():
    """

    """
    message = "You should not use a <code>while</code> loop to solve this problem."
    label = "while_usage"
    title = "Usage of <code>while</code>"
    ast = parse_program()
    if ast.find_all('While'):
        explain(message, label=label, title=title)
    prevent_builtin_usage(['sum', 'map', 'filter', 'reduce', 'len', 'max', 'min',
                           'max', 'sorted', 'all', 'any', 'getattr', 'setattr',
                           'eval', 'exec', 'iter'])


COMPARE_OP_NAMES = {
    "==": "Eq",
    "<": "Lt",
    "<=": "Lte",
    ">=": "Gte",
    ">": "Gt",
    "!=": "NotEq",
    "is": "Is",
    "is not": "IsNot",
    "in": "In",
    "not in": "NotIn"}
BOOL_OP_NAMES = {
    "and": "And",
    "or": "Or"}
BIN_OP_NAMES = {
    "+": "Add",
    "-": "Sub",
    "*": "Mult",
    "/": "Div",
    "//": "FloorDiv",
    "%": "Mod",
    "**": "Pow",
    ">>": "LShift",
    "<<": "RShift",
    "|": "BitOr",
    "^": "BitXor",
    "&": "BitAnd",
    "@": "MatMult"}
UNARY_OP_NAMES = {
    # "+": "UAdd",
    # "-": "USub",
    "not": "Not",
    "~": "Invert"
}


def ensure_operation(op_name, root=None):
    """

    Args:
        op_name:
        root:

    Returns:

    """
    message = "You are not using the <code>{}</code> operator.".format(op_name)
    label = "missing_op"
    title = "Missing <code>{}</code> Operator".format(op_name)
    if root is None:
        root = parse_program()
    result = find_operation(op_name, root)
    if not result:
        gently(message, label=label, title=title)
    return result


def prevent_operation(op_name, root=None):
    """

    Args:
        op_name:
        root:

    Returns:

    """
    message = "You may not use the <code>{}</code> operator.".format(op_name)
    label = "bad_op"
    title = "Bad Operator".format(op_name)
    if root is None:
        root = parse_program()
    result = find_operation(op_name, root)
    if result:
        gently(message, label=label, title=title)
    return result


def find_operation(op_name, root):
    """

    Args:
        op_name:
        root:

    Returns:

    """
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


def ensure_recursion(function_name, root=None):
    """

    Args:
        function_name:
        root:

    Returns:

    """
    if root is None:
        root = parse_program()
    all_calls = root.find_all('Call')
    calls = []
    for a_call in all_calls:
        if a_call.func.ast_name == 'Attribute':
            if a_call.func.attr == function_name:
                calls.append(a_call)
        elif a_call.func.ast_name == 'Name':
            if a_call.func.id == function_name:
                calls.append(a_call)
    return calls


def ensure_assignment(variable_name, type=None, value=None, root=None):
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
            elif (type == 'Bool' and
                  assign.value.ast_name == 'Name' and
                  assign.value.id in ('True', 'False')):
                return assign
            elif (type == 'Bool' and
                  assign.value.ast_name == 'NameConstant' and
                  assign.value.value in (True, False)):
                return assign
            elif assign.value.ast_name == type:
                return assign
    if potentials and potentials[0].value.ast_name not in ("Str", "Bool", "Num", "List", "Tuple"):
        explain(("You needed to assign a literal value to {variable}, but you "
                   "created an expression instead.").format(variable=variable_name), label="exp_vs_lit",
                  title="Expression Instead of Literal")
    elif type is None:
        explain(("You have not properly assigned anything to the variable "
                   "{variable}.").format(variable=variable_name), label="no_assign", title="No Proper Assignment")
    else:
        explain(("You have not assigned a {type} to the variable {variable}."
                   "").format(type=type, variable=variable_name), label="type_assign", title="Unexpected Variable Type")
    return False
