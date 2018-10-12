from pedal.cait.cait_api import parse_program
from pedal.report.imperative import gently, explain


def is_top_level(ast_node):
    ast = parse_program()
    for element in ast.body:
        if element.ast_name == 'Expr':
            if element.value == ast_node:
                return True
        elif element == ast_node:
            return True
    return False


def no_nested_function_definitions():
    ast = parse_program()
    defs = ast.find_all('FunctionDef')
    for a_def in defs:
        if not is_top_level(a_def):
            gently("You have defined a function inside of another block. For instance, you may have placed it inside "
                   "another function definition, or inside of a loop. Do not nest your function definition!"
                   "<br><br><i>(nest_func)<i>")
            return False
    return True


def function_prints():
    ast = parse_program()
    defs = ast.find_all('FunctionDef')
    for a_def in defs:
        all_calls = a_def.find_all('Call')
        for a_call in all_calls:
            if a_call.func.ast_name == 'Name':
                if a_call.func.id == 'print':
                    return True
    return False


def find_function_calls(name):
    ast = parse_program()
    all_calls = ast.find_all('Call')
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
    return len(find_function_calls(name))


def no_nonlist_nums():
    pass


def only_printing_variables():
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
    ast = parse_program()
    exprs = ast.find_all('Expr')
    for expr in exprs:
        if expr.value.ast_name == "Call":
            a_call = expr.value
            if a_call.func.ast_name == 'Attribute':
                if a_call.func.attr == 'append':
                    pass
                elif a_call.func.attr in ('replace', 'strip', 'lstrip', 'rstrip'):
                    gently("Remember! You cannot modify a string directly. Instead, you should assign the result back "
                           "to the string variable.<br><br><i>(str_mutate)<i>")


def prevent_builtin_usage(function_names):
    # Prevent direction calls
    ast = parse_program()
    all_calls = ast.find_all('Call')
    for a_call in all_calls:
        if a_call.func.ast_name == 'Name':
            if a_call.func.id in function_names:
                explain("You cannot use the builtin function <code>{}</code>.<br><br><i>(builtin_use)<i>".format(a_call.func.id))
                return a_call.func.id
    return None


def prevent_literal(*literals):
    ast = parse_program()
    str_values = [s.s for s in ast.find_all("Str")]
    num_values = [n.n for n in ast.find_all("Num")]
    for literal in literals:
        if isinstance(literal, (int, float)):
            if literal in num_values:
                explain("Do not use the literal value <code>{}</code> in your code."
                        "<br><br><i>(hard_code)<i>".format(repr(literal)))
                return literal
        elif isinstance(literal, str):
            if literal in str_values:
                explain("Do not use the literal value <code>{}</code> in your code."
                        "<br><br><i>(hard_code)<i>".format(repr(literal)))
                return literal
    return False


def ensure_literal(*literals):
    ast = parse_program()
    str_values = [s.s for s in ast.find_all("Str")]
    num_values = [n.n for n in ast.find_all("Num")]
    for literal in literals:
        if isinstance(literal, (int, float)):
            if literal not in num_values:
                explain("You need the literal value <code>{}</code> in your code."
                        "<br><br><i>(missing_literal)<i>".format(repr(literal)))
                return literal
        elif isinstance(literal, str):
            if literal not in str_values:
                explain("You need the literal value <code>{}</code> in your code."
                        "<br><br><i>(missing_literal)<i>".format(repr(literal)))
                return literal
    return False


def prevent_advanced_iteration():
    ast = parse_program()
    if ast.find_all('While'):
        explain("You should not use a <code>while</code> loop to solve this problem."
                "<br><br><i>(while_usage)<i>")
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
    # "+=": "UAdd",
    # "-=": "USub",
    "not": "Not",
    "~": "Invert"
}


def ensure_operation(op_name, root=None):
    if root is None:
        root = parse_program()
    result = find_operation(op_name, root)
    if not result:
        gently("You are not using the <code>{}</code> operator.<br><br><i>(missing_op)<i>".format(op_name))
    return result


def prevent_operation(op_name, root=None):
    if root is None:
        root = parse_program()
    result = find_operation(op_name, root)
    if result:
        gently("You may not use the <code>{}</code> operator.<br><br><i>(bad_op)<i>".format(op_name))
    return result


def find_operation(op_name, root):
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

def ensure_recursion(function_name, root):
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