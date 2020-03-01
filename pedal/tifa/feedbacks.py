from pedal.utilities.operators import OPERATION_DESCRIPTION

from pedal.core.commands import feedback
from pedal.core.feedback import AtomicFeedbackFunction
from pedal.core.report import MAIN_REPORT


def _generic_tifa_feedback_function(feedback_function, fields: dict, muted=False, report=MAIN_REPORT):
    return feedback(feedback_function.__name__, category=feedback.CATEGORIES.ALGORITHMIC,
                    message=feedback_function.message_template.format(**fields),
                    text=feedback_function.text_template.format(**fields),
                    fields=fields, kind=feedback.KINDS.MISTAKE, justification=feedback_function.justification,
                    tags=feedback_function.tags,
                    title=feedback_function.title, locations=fields['location'],
                    muted=muted or feedback_function.muted,
                    version=feedback_function.version, report=report)


@AtomicFeedbackFunction(title="Action after Return",
                        text_template=("You performed an action after already returning from a "
                                       "function, on line {location.line}. You can only return on a path "
                                       "once."),
                        justification=("TIFA visited a node not in the top scope when its "
                                       "*return variable was definitely set in this scope."))
def action_after_return(location, report=MAIN_REPORT):
    """

    Args:
        location:
        report:

    Returns:

    """
    fields = {'location': location}
    return _generic_tifa_feedback_function(action_after_return, fields, report)


@AtomicFeedbackFunction(title="Return outside Function",
                        text_template=("You attempted to return outside of a function on line {location.line}."
                                       " But you can only return from within a function."),
                        justification="TIFA visited a return node at the top level.")
def return_outside_function(location, report=MAIN_REPORT):
    """

    Args:
        location:
        report:

    Returns:

    """
    fields = {'location': location}
    return _generic_tifa_feedback_function(return_outside_function, fields, report)


@AtomicFeedbackFunction(title="Multiple Return Types",
                        text_template=(
                                "Your function returned {actual} on line {location.line}, even though you defined it to"
                                " return {expected}. Your function should return values consistently."
                        ),
                        justification="TIFA visited a function definition with multiple returns that unequal types.")
def multiple_return_types(location, expected, actual, report=MAIN_REPORT):
    """

    Args:
        location:
        expected:
        actual:
        report:

    Returns:

    """
    fields = {'location': location, 'expected': expected, 'actual': actual}
    return _generic_tifa_feedback_function(multiple_return_types, fields, report)


@AtomicFeedbackFunction(title="Write Out of Scope",
                        message_template=("You attempted to write the variable `{name}` from a higher scope "
                                          "(outside the function) on line {location.line}. You should only "
                                          "use variables inside the function they were declared in."
                                          ),
                        justification="TIFA stored to an existing variable not in this scope")
def write_out_of_scope(location, name, report=MAIN_REPORT):
    """

    Args:
        location:
        name:
        report:

    Returns:

    """
    fields = {'location': location, 'name': name}
    return _generic_tifa_feedback_function(write_out_of_scope, fields, report=report, muted=True)


@AtomicFeedbackFunction(title="Unconnected Blocks",
                        text_template=("It looks like you have unconnected blocks on line {location.line}. "
                                       "Before you run your program, you must make sure that all "
                                       "of your blocks are connected that there are no unfilled "
                                       "holes."),
                        justification="TIFA found a name equal to ___")
def unconnected_blocks(location, report=MAIN_REPORT):
    """

    Args:
        location:
        report:

    Returns:

    """
    fields = {'location': location}
    return _generic_tifa_feedback_function(unconnected_blocks, fields, report=report)


@AtomicFeedbackFunction(title="Iteration Problem",
                        message_template=("The variable `{name}` was iterated on line "
                                          "{location.line} but you used the same variable as the iteration "
                                          "variable. You should choose a different variable name "
                                          "for the iteration variable. Usually, the iteration variable "
                                          "is the singular form of the iteration list (e.g., "
                                          "`for a_dog in dogs:`)."),
                        justification="TIFA visited a loop where the iteration list and target were the same.")
def iteration_problem(location, name, report=MAIN_REPORT):
    """

    Args:
        location:
        name:
        report:

    Returns:

    """
    fields = {'location': location, 'name': name}
    return _generic_tifa_feedback_function(iteration_problem, fields, report=report)


@AtomicFeedbackFunction(title="Initialization Problem",
                        message_template=("The variable `{name}` was used on line {location.line}, "
                                          "but it was not given a value on a previous line. "
                                          "You cannot use a variable until it has been given a value."
                                          ),
                        justification="TIFA read a variable that did not exist or was not previously set in this branch.")
def initialization_problem(location, name, report=MAIN_REPORT):
    """

    Args:
        location:
        name:
        report:

    Returns:

    """
    fields = {'location': location, 'name': name}
    return _generic_tifa_feedback_function(initialization_problem, fields, report=report)


@AtomicFeedbackFunction(title="Possible Initialization Problem",
                        message_template=("The variable `{name}` was used on line {location.line}, "
                                          "but it was possibly not given a value on a previous "
                                          "line. You cannot use a variable until it has been given "
                                          "a value. Check to make sure that this variable was "
                                          "declared in all of the branches of your decision."
                                          ),
                        justification="TIFA read a variable that was maybe set but not definitely set in this branch.")
def possible_initialization_problem(location, name, report=MAIN_REPORT):
    """

    Args:
        location:
        name:
        report:

    Returns:

    """
    fields = {'location': location, 'name': name}
    return _generic_tifa_feedback_function(possible_initialization_problem, fields, report=report)


@AtomicFeedbackFunction(title="Unused Variable",
                        message_template=("The {kind} `{name}` was given a {initialization} on line {location.line}, but "
                                          "was never used after that."
                                          ),
                        justification="TIFA stored a variable but it was not read any other time in the program.")
def unused_variable(location, name, type, report=MAIN_REPORT):
    """

    Args:
        location:
        name:
        type:
        report:

    Returns:

    """
    if type.is_equal('function'):
        kind, initialization = 'function', 'definition'
    else:
        kind, initialization = 'variable', 'value'
    fields = {'location': location, 'name': name, 'type': type,
              'kind': kind, 'initialization': initialization}
    return _generic_tifa_feedback_function(unused_variable, fields, report=report)


@AtomicFeedbackFunction(title="Overwritten Variable",
                        message_template=("The variable `{name}` was given a value, but "
                                          "`{name}` was changed on line {location.line} before it "
                                          "was used. One of the times that you gave `{name}` "
                                          "a value was incorrect."
                                          ),
                        justification="TIFA attempted to store to a variable that was previously stored but not read.")
def overwritten_variable(location, name, report=MAIN_REPORT):
    """

    Args:
        location:
        name:
        report:

    Returns:

    """
    fields = {'location': location, 'name': name}
    return _generic_tifa_feedback_function(overwritten_variable, fields, report=report)


@AtomicFeedbackFunction(title="Iterating over Non-list",
                        message_template=("The {iter} is not a list, but you used "
                                          "it in the iteration on line {location.line}. You should only iterate "
                                          "over sequences like lists."
                                          ),
                        justification="TIFA visited a loop's iteration list whose type was not indexable.")
def iterating_over_non_list(location, iter_name, report=MAIN_REPORT):
    """

    Args:
        location:
        iter_name:
        report:

    Returns:

    """
    if iter_name is None:
        iter_list = "expression"
    else:
        iter_list = "variable `{}`".format(iter_name)
    fields = {'location': location, 'name': iter_name, 'iter': iter_list}
    return _generic_tifa_feedback_function(iterating_over_non_list, fields, report=report)


@AtomicFeedbackFunction(title="Iterating over empty list",
                        message_template=("The {iter} was set as an empty list, "
                                          "and then you attempted to use it in an iteration on line "
                                          "{location.line}. You should only iterate over non-empty lists."
                                          ),
                        justification="TIFA visited a loop's iteration list that was empty.")
def iterating_over_empty_list(location, iter_name, report=MAIN_REPORT):
    """

    Args:
        location:
        iter_name:
        report:

    Returns:

    """
    if iter_name is None:
        iter_list = "expression"
    else:
        iter_list = "variable `{}`".format(iter_name)
    fields = {'location': location, 'name': iter_name, 'iter': iter_list}
    return _generic_tifa_feedback_function(iterating_over_empty_list, fields, report=report)


@AtomicFeedbackFunction(title="Incompatible types",
                        text_template=("You used {op_name} operation with {left_name} and {right_name} on line "
                                       "{location.line}. But you can't do that with that operator. Make "
                                       "sure both sides of the operator are the right type."
                                       ),
                        justification="TIFA visited an operation with operands of the wrong type.")
def incompatible_types(location, operation, left, right, report=MAIN_REPORT):
    """

    Args:
        location:
        operation:
        left:
        right:
        report:

    Returns:

    """
    op_name = OPERATION_DESCRIPTION.get(operation.__class__,
                                        str(operation))
    left_name = left.singular_name
    right_name = right.singular_name
    fields = {'location': location,
              'operation': operation, 'left': left, 'right': right,
              'op_name': op_name, 'left_name': left_name, 'right_name': right_name}
    return _generic_tifa_feedback_function(incompatible_types, fields, report=report)


@AtomicFeedbackFunction(title="Parameter Type Mismatch",
                        message_template=("You defined the parameter `{parameter_name}` on line {location.line} "
                                          "as {parameter_type_name}. However, the argument passed to that parameter "
                                          "was {argument_type_name}. The formal parameter type must match the argument's type."
                                          ),
                        justification="TIFA visited a function definition where a parameter type and argument type were not equal.")
def parameter_type_mismatch(location, parameter_name, parameter, argument, report=MAIN_REPORT):
    """

    Args:
        location:
        parameter_name:
        parameter:
        argument:
        report:

    Returns:

    """
    parameter_type_name = parameter.singular_name
    argument_type_name = argument.singular_name
    fields = {'location': location,
              'parameter_name': parameter_name,
              'parameter_type': parameter,
              'argument_type': argument,
              'parameter_type_name': parameter_type_name,
              'argument_type_name': argument_type_name}
    return _generic_tifa_feedback_function(parameter_type_mismatch, fields, report=report)


@AtomicFeedbackFunction(title="Read out of Scope",
                        message_template=("You attempted to read the variable `{name}` from a different scope on "
                                          "line {location.line}. You should only use variables inside the "
                                          "function they were declared in."
                                          ),
                        justification="TIFA read a variable that did not exist in this scope but existed in another.")
def read_out_of_scope(location, name, report=MAIN_REPORT):
    """

    Args:
        location:
        name:
        report:

    Returns:

    """
    fields = {'location': location, 'name': name}
    return _generic_tifa_feedback_function(read_out_of_scope, fields, report=report)


# TODO: Complete these
@AtomicFeedbackFunction(title="Type Changes",
                        message_template="",
                        justification="",
                        muted=True)
def type_changes(location, name, old, new, report=MAIN_REPORT):
    """

    Args:
        location:
        name:
        old:
        new:
        report:

    Returns:

    """
    fields = {'location': location, 'name': name, 'old': old, 'new': new}
    return _generic_tifa_feedback_function(type_changes, fields, report=report)


@AtomicFeedbackFunction(title="Unnecessary Second Branch",
                        message_template="",
                        justification="")
def unnecessary_second_branch(location, report=MAIN_REPORT):
    """

    Args:
        location:
        report:

    Returns:

    """
    fields = {'location': location}
    return _generic_tifa_feedback_function(unnecessary_second_branch, fields, report=report, muted=True)


@AtomicFeedbackFunction(title="Else on Loop Body",
                        message_template="",
                        justification="")
def else_on_loop_body(location, report=MAIN_REPORT):
    """

    Args:
        location:
        report:

    Returns:

    """
    fields = {'location': location}
    return _generic_tifa_feedback_function(else_on_loop_body, fields, report=report, muted=True)


@AtomicFeedbackFunction(title="Recursive Call",
                        message_template="",
                        justification="")
def recursive_call(location, name, report=MAIN_REPORT):
    """

    Args:
        location:
        name:
        report:

    Returns:

    """
    fields = {'location': location, 'name': name}
    return _generic_tifa_feedback_function(recursive_call, fields, report=report, muted=True)


@AtomicFeedbackFunction(title="Not a Function",
                        message_template="",
                        justification="")
def not_a_function(location, name, report=MAIN_REPORT):
    """

    Args:
        location:
        name:
        report:

    Returns:

    """
    fields = {'location': location, 'name': name}
    return _generic_tifa_feedback_function(not_a_function, fields, report=report, muted=True)


@AtomicFeedbackFunction(title="Incorrect Arity",
                        message_template="",
                        justification="")
def incorrect_arity(location, function_name, report=MAIN_REPORT):
    """

    Args:
        location:
        function_name:
        report:

    Returns:

    """
    fields = {'location': location, 'function_name': function_name}
    return _generic_tifa_feedback_function(incorrect_arity, fields, report=report, muted=True)


@AtomicFeedbackFunction(title="Multiple Return Types",
                        message_template="",
                        justification="")
def multiple_return_types(location, expected, actual, report=MAIN_REPORT):
    """

    Args:
        location:
        expected:
        actual:
        report:

    Returns:

    """
    fields = {"location": location, "expected": expected, "actual": actual}
    return _generic_tifa_feedback_function(multiple_return_types, fields, report=report, muted=True)


@AtomicFeedbackFunction(title="Module Not Found",
                        text_template="",
                        justification="")
def module_not_found(location, name, is_dynamic=False, error=None, report=MAIN_REPORT):
    """

    Args:
        location:
        name:
        is_dynamic:
        error:
        report:

    Returns:

    """
    fields = {"location": location, "name": name, "is_dynamic": is_dynamic, "error": error}
    return _generic_tifa_feedback_function(module_not_found, fields, report=report, muted=True)


@AtomicFeedbackFunction(title="Append to non-list",
                        text_template="",
                        justification="",
                        muted=True)
def append_to_non_list(location, name, type, report=MAIN_REPORT):
    """

    Args:
        location:
        name:
        type:
        report:

    Returns:

    """
    fields = {'location': location, "name": name, "type": type }
    return _generic_tifa_feedback_function(append_to_non_list, fields, report=report)

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

# TODO: Equality instead of assignment
