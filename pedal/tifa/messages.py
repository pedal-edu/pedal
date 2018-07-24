'''issues': {
                    "Parser Failure": [], # Complete failure to parse the code
                    "Unconnected blocks": [], # Any names with ____
                    "Empty Body": [], # Any use of pass on its own
                    "Malformed Conditional": [], # An if/else with empty else or if
                    "Unnecessary Pass": [], # Any use of pass
                    "Unread variables": [], # A variable was not read after it was defined
                    "Undefined variables": [], # A variable was read before it was defined
                    "Possibly undefined variables": [], # A variable was read but was not defined in every branch
                    "Overwritten variables": [], # A written variable was written to again before being read
                    "Append to non-list": [], # Attempted to use the append method on a non-list
                    "Used iteration list": [], # 
                    "Unused iteration variable": [], # 
                    "Non-list iterations": [], # 
                    "Empty iterations": [], # 
                    "Type changes": [], # 
                    "Iteration variable is iteration list": [], # 
                    "Unknown functions": [], # 
                    "Not a function": [], # Attempt to call non-function as function
                    "Recursive Call": [],
                    "Incorrect Arity": [],
                    "Action after return": [],
                    "Incompatible types": [], # 
                    "Return outside function": [], # 
                    "Read out of scope": [], # 
                    "Write out of scope": [], # Attempted to modify a variable in a higher scope
                    "Aliased built-in": [], # 
                    "Method not in Type": [], # A method was used that didn't exist for that type
                    "Submodule not found": [],
                    "Module not found": [],
                    "Else on loop body": [], # Used an Else on a For or While
                }'''
def _format_message(issue, data):
    if issue == 'Action after return':
        line = data['position']['line']
        return ("You performed an action after already returning from a "
                "function, on line {line}. You can only return on a path "
                "once.").format(line=line)
    else:
        return "Message has not been created yet."
'''
    } else if (!suppress['Return outside function'] && report['Return outside function'].length >= 1) {
        var first = report['Return outside function'][0];
        this.semanticError("Return outside function", "You attempted to return outside of a function on line "+first.position.line+". But you can only return from within a function.", first.position.line)
        return true;
    /*} else if (!suppress['Write out of scope'] && report['Write out of scope'].length >= 1) {
        var first = report['Write out of scope'][0];
        this.semanticError("Write out of scope", "You attempted to write a variable from a higher scope (outside the function) on line "+first.position.line+". You should only use variables inside the function they were declared in.", first.position.line)
        return true;*/
    } else if (!suppress['Unconnected blocks'] && report["Unconnected blocks"].length >= 1) {
        var variable = report['Unconnected blocks'][0];
        this.semanticError("Unconnected blocks", "It looks like you have unconnected blocks on line "+variable.position.line+". Before you run your program, you must make sure that all of your blocks are connected and that there are no unfilled holes.", variable.position.line)
        return true;
    } else if (!suppress['Iteration variable is iteration list'] && report['Iteration variable is iteration list'].length >= 1) {
        var variable = report['Iteration variable is iteration list'][0];
        this.semanticError("Iteration Problem", "The variable <code>"+variable.name+"</code> was iterated on line "+variable.position.line+", but you used the same variable as the iteration variable. You should choose a different variable name for the iteration variable. Usually, the iteration variable is the singular form of the iteration list (e.g., <code>for dog in dogs:</code>).", variable.position.line)
        return true;
    } else if (!suppress["Undefined variables"] && report["Undefined variables"].length >= 1) {
        var variable = report["Undefined variables"][0];
        this.semanticError("Initialization Problem", "The variable <code>"+variable.name+"</code> was used on line "+variable.position.line+", but it was not given a value on a previous line. You cannot use a variable until it has been given a value.", variable.position.line)
        return true;
    } else if (!suppress["Possibly undefined variables"] && report["Possibly undefined variables"].length >= 1) {
        var variable = report["Possibly undefined variables"][0];
        var kindName = 'variable', kindBody = 'value';
        if (variable.name == '*return') {
            return false;
        } else {
            this.semanticError("Initialization Problem", "The variable <code>"+variable.name+"</code> was used on line "+variable.position.line+", but it was possibly not given a value on a previous line. You cannot use a variable until it has been given a value. Check to make sure that this variable was declared in all of the branches of your decision.", variable.position.line);
        }
        return true;
    } else if (!suppress["Unread variables"] && report["Unread variables"].length >= 1) {
        var variable = report["Unread variables"][0];
        var kindName = 'variable', kindBody = 'value';
        if (variable.type && variable.type.name == 'Function') {
            kindName = 'function';
            kindBody = 'definition';
        }
        this.semanticError("Unused Variable", "The "+kindName+" <code>"+variable.name+"</code> was given a "+kindBody+", but was never used after that.", null)
        return true;
    } else if (!suppress["Overwritten variables"] && report["Overwritten variables"].length >= 1) {
        var variable = report["Overwritten variables"][0];
        this.semanticError("Overwritten Variable", "The variable <code>"+variable.name+"</code> was given a value, but <code>"+variable.name+"</code> was changed on line "+variable.position.line+" before it was used. One of the times that you gave <code>"+variable.name+"</code> a value was incorrect.", variable.position.line)
        return true;
    } else if (!suppress["Empty iterations"] && report["Empty iterations"].length >= 1) {
        var variable = report["Empty iterations"][0];
        if (variable.name) {
            this.semanticError("Iterating over empty list", "The variable <code>"+variable.name+"</code> was set as an empty list, and then you attempted to use it in an iteration on line "+variable.position.line+". You should only iterate over non-empty lists.", variable.position.line)
            return true;
        }
    } else if (!suppress["Non-list iterations"] && report["Non-list iterations"].length >= 1) {
        var variable = report["Non-list iterations"][0];
        if (variable.name) {
            this.semanticError("Iterating over non-list", "The variable <code>"+variable.name+"</code> is not a list, but you used it in the iteration on line "+variable.position.line+". You should only iterate over sequences like lists.", variable.position.line)
            return true;
        }
    } else if (!suppress["Incompatible types"] && report["Incompatible types"].length >= 1) {
        var variable = report["Incompatible types"][0];
        var op = this.OPERATION_DESCRIPTION[variable.operation];
        var left = this.TYPE_DESCRIPTION[variable.left.name];
        var right = this.TYPE_DESCRIPTION[variable.right.name];
        this.semanticError("Incompatible types", "You used "+op+" operation with a "+left+" and a "+right+" on line "+variable.position.line+". But you can't do that with that operator. Make sure both sides of the operator are the right type.", variable.position.line)
        return true;
    } else if (!suppress['Read out of scope'] && report['Read out of scope'].length >= 1) {
        var first = report['Read out of scope'][0];
        this.semanticError("Read out of scope", "You attempted to read a variable from a different scope on line "+first.position.line+". You should only use variables inside the function they were declared in.", first.position.line)
        return true;
    }
    return false;
'''