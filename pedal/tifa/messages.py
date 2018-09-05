import ast

OPERATION_DESCRIPTION = {
    ast.Pow: "an exponent",
    ast.Add: "an addition",
    ast.Mult: "a multiplication",
    ast.Sub: "a subtraction",
    ast.Div: "a division",
    ast.FloorDiv: "a division",
    ast.Mod: "a modulo",
    ast.LShift: "a left shift",
    ast.RShift: "a right shift",
    ast.BitOr: "a bit or",
    ast.BitAnd: "a bit and",
    ast.BitXor: "a bit xor",
    ast.And: "an and",
    ast.Or: "an or",
    ast.Eq: "an ==",
    ast.NotEq: "a !=",
    ast.Lt: "a <",
    ast.LtE: "a <=",
    ast.Gt: "a >",
    ast.GtE: "a >=",
    ast.Is: "an is",
    ast.IsNot: "an is not",
    ast.In: "an in",
    ast.NotIn: "an not in",
}

def _format_message(issue, data):
    if issue == 'Action after return':
        # A path had a statement after a return.
        return ("You performed an action after already returning from a "
                "function, on line {line}. You can only return on a path "
                "once.").format(line=data['position']['line'])
    elif issue == 'Return outside function':
        # Attempted to return outside of a function
        return ("You attempted to return outside of a function on line {line}."
                " But you can only return from within a function."
                ).format(line=data['position']['line'])
    elif issue == 'Write out of scope':
        # DEPRECATED
        # Attempted to modify a variable in a higher scope
        return False
        return ("You attempted to write a variable from a higher scope "
                "(outside the function) on line {line}. You should only "
                "use variables inside the function they were declared in."
                ).format(line=data['position']['line'])
    elif issue == 'Unconnected blocks':
        # Any names with ____
        return ("It looks like you have unconnected blocks on line {line}. "
                "Before you run your program, you must make sure that all "
                "of your blocks are connected that there are no unfilled "
                "holes.").format(line=data['position']['line'])
    elif issue == 'Iteration Problem':
        # Iteration list is the iteration variable
        return ("The variable <code>{name}</code> was iterated on line "
                "{line} but you used the same variable as the iteration "
                "variable. You should choose a different variable name "
                "for the iteration variable. Usually, the iteration variable "
                "is the singular form of the iteration list (e.g., "
                "<code>for a_dog in dogs:</code>).").format(
                    line=data['position']['line'],
                    name=data['name'])
    elif issue == 'Initialization Problem':
        # A variable was read before it was defined
        return ("The variable <code>{name}</code> was used on line {line}, "
                "but it was not given a value on a previous line. "
                "You cannot use a variable until it has been given a value."
                ).format(line=data['position']['line'], name=data['name'])
    elif issue == 'Possible Initialization Problem':
        # A variable was read but was not defined in every branch
        if data['name'] == '*return':
            return False
        return ("The variable <code>{name}</code> was used on line {line}, "
                "but it was possibly not given a value on a previous "
                "line. You cannot use a variable until it has been given "
                "a value. Check to make sure that this variable was "
                "declared in all of the branches of your decision."
                ).format(line=data['position']['line'], name=data['name'])
    elif issue == 'Unused Variable':
        # A variable was not read after it was defined
        name = data['name']
        if data['type'].is_equal('function'):
            kind = 'function'
            body = 'definition'
        else:
            kind = 'variable'
            body = 'value'
        return ("The {kind} <code>{name}</code> was given a {body}, but "
                "was never used after that."
                ).format(name=name, kind=kind, body=body)
    elif issue == 'Overwritten Variable':
        return ("The variable <code>{name}</code> was given a value, but "
                "<code>{name}</code> was changed on line {line} before it "
                "was used. One of the times that you gave <code>{name}</code> "
                "a value was incorrect."
                ).format(line=data['position']['line'], name=data['name'])
    elif issue == 'Iterating over non-list':
        if 'name' not in data or data['name'] is None:
            expression = "expression"
        else:
            expression = "variable <code>{}</code>".format(data['name'])
        return ("The {expression} is not a list, but you used "
                "it in the iteration on line {line}. You should only iterate "
                "over sequences like lists."
                ).format(line=data['position']['line'], expression=expression)
    elif issue == 'Iterating over empty list':
        if 'name' not in data or data['name'] is None:
            expression = "expression"
        else:
            expression = "variable <code>{}</code>".format(data['name'])
        return ("The {expression} was set as an empty list, "
                "and then you attempted to use it in an iteration on line "
                "{line}. You should only iterate over non-empty lists."
                ).format(line=data['position']['line'], expression=expression)
    elif issue == 'Incompatible types':
        op = OPERATION_DESCRIPTION.get(data['operation'].__class__, 
                                       str(data['operation']))
        left = data['left'].singular_name
        right = data['right'].singular_name
        line = data['position']['line']
        return ("You used {op} operation with {left} and {right} on line "
                "{line}. But you can't do that with that operator. Make "
                "sure both sides of the operator are the right type."
                ).format(op=op, left=left, right=right, line=line)
    elif issue == 'Read out of scope':
        return ("You attempted to read a variable from a different scope on "
                "line {line}. You should only use variables inside the "
                "function they were declared in."
                ).format(line=data['position']['line'])
    return False

'''
TODO: Finish these checks
"Empty Body": [], # Any use of pass on its own
"Malformed Conditional": [], # An if/else with empty else or if
"Unnecessary Pass": [], # Any use of pass
"Append to non-list": [], # Attempted to use the append method on a non-list
"Used iteration list": [], # 
"Unused iteration variable": [], # 
"Type changes": [], # 
"Unknown functions": [], # 
"Not a function": [], # Attempt to call non-function as function
"Recursive Call": [],
"Incorrect Arity": [],
"Aliased built-in": [], # 
"Method not in Type": [], # A method was used that didn't exist for that type
"Submodule not found": [],
"Module not found": [],
"Else on loop body": [], # Used an Else on a For or While
'''
