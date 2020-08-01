"""
Collection of feedback functions related to static checks of student code.
"""
from pedal.cait.cait_api import parse_program
from pedal.assertions.feedbacks import AssertionFeedback
from pedal.cait.find_node import find_operation, find_function_calls
from pedal.core.feedback import CompositeFeedbackFunction
from pedal.core.location import Location
from pedal.core.report import MAIN_REPORT
from pedal.toolkit.functions import match_signature


class EnsureAssertionFeedback(AssertionFeedback):
    """ Abstract base class for assertions preventing things. """
    def __init__(self, name, at_least=1, root=None, **kwargs):
        report = kwargs.get('report', MAIN_REPORT)
        root = root or parse_program(report=report)
        fields = {'name': name, 'at_least': at_least, 'capacity': '',
                  'root': root, 'name_message': report.format.name(name)}
        super().__init__(fields=fields, **kwargs)

    def _check_usage(self, field_name, uses):
        at_least = self.fields['at_least']
        self.fields[field_name] = use_count = len(uses)
        if at_least > use_count:
            if at_least == 1:
                return True
            else:
                self.fields['capacity'] = (f" at least {at_least} times, but"
                                           f" you used it {use_count} times")
                return True
        return False


class PreventAssertionFeedback(AssertionFeedback):
    """ Abstract base class for assertions preventing things. """
    def __init__(self, name, at_most=0, root=None, **kwargs):
        report = kwargs.get('report', MAIN_REPORT)
        root = root or parse_program(report=report)
        fields = {'name': name, 'at_most': at_most, 'capacity': '',
                  'root': root, 'name_message': report.format.name(name)}
        super().__init__(fields=fields, **kwargs)

    def _check_usage(self, field_name, uses):
        at_most = self.fields['at_most']
        self.fields[field_name] = use_count = len(uses)
        if use_count and at_most < use_count:
            if at_most == 0:
                return True
            else:
                self.fields['capacity'] = (f" more than {at_most} times, but"
                                           f" you used it {use_count} times")
                return True
        return False


class prevent_function_call(PreventAssertionFeedback):
    """
    Determine if a function was ever called by statically checking
    the students' code.

    # TODO: also check the TIFA records to see if the function was read

    Args:
        name (str): The name of the function (e.g., ``'sum'``)
        at_most (int): The maximum number of times you are allowed to call this
            function. Defaults to ``0``.
    """

    title = "May Not Use Function"
    message_template = ("You used the function {name_message} on line "
                        "{location.line}. You may not use that function"
                        "{capacity}.")

    def condition(self):
        """ Use find_matches to check number of occurrences. """
        name = self.fields['name']
        calls = find_function_calls(name, root=self.fields['root'])
        if calls:
            self.fields['location'] = Location.from_ast(calls[-1])
        return self._check_usage('call_count', calls)


class ensure_function_call(EnsureAssertionFeedback):
    """
    Determine that a function was definitely called by statically checking
    the students' code.

    # TODO: also check the TIFA records to see if the function was read

    Args:
        name (str): The name of the function (e.g., ``'sum'``)
        at_most (int): The maximum number of times you are allowed to call this
            function. Defaults to ``0``.
    """

    title = "Must Use Function"
    message_template = "You must use the function {name_message}{capacity}."

    def condition(self):
        """ Use find_matches to check number of occurrences. """
        name = self.fields['name']
        calls = find_function_calls(name, root=self.fields['root'])
        return self._check_usage('call_count', calls)


class prevent_operation(PreventAssertionFeedback):
    """
    Determines if the given operator `op_name` is not used anywhere, returning
    the node of it if it is. Otherwise, returns `None`. You can specify the
    operator as a string like `"+"` or `"<<"`. Supports all comparison,
    boolean, binary, and unary operators.

    Args:
        name (str): The name of the function (e.g., ``'sum'``)
        at_most (int): The maximum number of times you are allowed to call this
            function. Defaults to ``0``.
    """
    title = "May Not Use Operator"
    message_template = ("You used the operator {name_message} on line "
                        "{location.line}. You may not use that operator"
                        "{capacity}.")

    def condition(self):
        """ Use find_matches to check number of occurrences. """
        name = self.fields['name']
        self.fields['name_message'] = self.report.format.python_expression(name)
        uses = list(find_operation(name, root=self.fields['root']))
        if uses:
            self.fields['location'] = Location.from_ast(uses[-1])
        return self._check_usage('use_count', uses)


class ensure_operation(EnsureAssertionFeedback):
    """
    Determines if the given operator `op_name` is used somewhere. You can
    specify the operator as a string like `"+"` or `"<<"`. Supports all
    comparison, boolean, binary, and unary operators.

    Args:
        name (str): The name of the function (e.g., ``'sum'``)
        at_least (int): The minimum number of times you must call this
            function. Defaults to ``1``.
    """
    title = "Must Use Operator"
    message_template = "You must use the operator {name_message}{capacity}."

    def condition(self):
        """ Use find_matches to check number of occurrences. """
        name = self.fields['name']
        self.fields['name_message'] = self.report.format.python_expression(name)
        uses = list(find_operation(name, root=self.fields['root']))
        if uses:
            self.fields['location'] = Location.from_ast(uses[-1])
        return self._check_usage('use_count', uses)


class prevent_literal(PreventAssertionFeedback):
    """ Make sure that the given literal value does not appear in the student's
    code. """
    title = "May Not Use Literal Value"
    message_template = ("You used the literal value `{literal!r}` on line "
                        "{location.line}. You may not use that value"
                        "{capacity}.")

    def __init__(self, literal, at_most=0, root=None, **kwargs):
        report = kwargs.get('report', MAIN_REPORT)
        root = root or parse_program(report=report)
        fields = {'literal': literal, 'at_most': at_most, 'capacity': '',
                  'root': root, 'literal_message': report.format.python_expression(literal)}
        super(AssertionFeedback, self).__init__(fields=fields, **kwargs)

    def condition(self):
        literal = self.fields['literal']
        uses = self.fields['root'].find_matches(repr(literal))
        if uses:
            self.fields['location'] = uses[-1].match_location(False)
        return self._check_usage('use_count', uses)


class ensure_literal(EnsureAssertionFeedback):
    """ Make sure that the given literal value does appear in the student's
        code. """
    title = "Must Use Literal Value"
    message_template = "You must use the literal value `{literal!r}`{capacity}."

    def __init__(self, literal, at_least=1, root=None, **kwargs):
        report = kwargs.get('report', MAIN_REPORT)
        root = root or parse_program(report=report)
        fields = {'literal': literal, 'at_least': at_least, 'capacity': '',
                  'root': root, 'literal_message': report.format.python_expression(literal)}
        super(AssertionFeedback, self).__init__(fields=fields, **kwargs)

    def condition(self):
        literal = self.fields['literal']
        uses = self.fields['root'].find_matches(repr(literal))
        if uses:
            self.fields['location'] = uses[-1].match_location(False)
        return self._check_usage('use_count', uses)


def function_prints(function_name):
    """
    Determine that the print function is called within this function, by
    tracing its code statically. Does not actually verify that the function
    was ever called in practice.

    Args:
        function_name (str): The name of the function to search.

    Returns:

    """
    return ensure_function_call('print', root=match_signature(function_name))


def has_import(ast, name):
    """
    Determine if the given module name is in the code.

    Args:
        ast (:py:class:`pedal.cait.cait_node.CaitNode`): The starting point
            to search.
        name (str): The name of the module to match against.

    Returns:
        bool: Whether or not the module name was matched.
    """
    imports = ast.find_all("Import")
    import_froms = ast.find_all("ImportFrom")
    # What about ``import <name>``
    if imports and any(alias._name == name for i in imports for alias in i.names):
        return True
    # What about ``from <name> import *``
    if import_froms and any(i.module == name for i in import_froms):
        return True
    return False


class ensure_import(EnsureAssertionFeedback):
    """
    Verify that the given ``module`` has been imported, by statically
    checking the import statements in the code. The ``at_least`` parameter
    is ignored.
    """
    title = "Must Import Module"
    message_template = "You must import the module {name_message}."

    def condition(self):
        """ Traverse the AST to find matches. """
        name = self.fields['name']
        ast = self.fields['root']
        return not has_import(ast, name)


class prevent_import(PreventAssertionFeedback):
    """
    Verify that the given ``module`` has not been imported, by statically
    checking the import statements in the code. The ``at_most`` parameter
    is ignored.
    """
    title = "May Not Import Module"
    message_template = "You may not import the module {name_message}."

    def condition(self):
        """ Traverse the AST to find matches. """
        name = self.fields['name']
        ast = self.fields['root']
        return has_import(ast, name)


class ensure_documented_functions(AssertionFeedback):
    """ Checks that all of the functions in the source code are documented. """
    title = "Must Document Functions"
    message_template = ("You must document the following function{plural}:"
                        ": {names_message}.")

    def __init__(self, root=None, **kwargs):
        report = kwargs.get('report', MAIN_REPORT)
        root = root or parse_program(report=report)
        fields = {'root': root}
        super().__init__(fields=fields, **kwargs)

    def condition(self):
        """ Traverse the AST to find matches. """
        defs = self.fields['root'].find_all('FunctionDef')
        names = []
        for a_def in defs:
            # Don't have to document constructors (happens in Class Def)
            if a_def.name == "__init__":
                continue
            if (a_def.body and (a_def.body[0].ast_name != "Expr" or
                                a_def.body[0].value.ast_name != "Str")):
                names.append(a_def.name)
        self.fields['names'] = names
        self.fields['names_message'] = ", ".join(self.report.format.name(name)
                                                 for name in names)
        self.fields['plural'] = 's' if names else ''
        return bool(names)

"""
New assertions:

prevent_literal(literal_value: Any)
prevent_function_call(function_name: str) # Whether it was detected statically
prevent_operation(operator: str)
prevent_import(module_name: str)

TODO: prevent_source_text(code: str, missing=False, minimum=2, maximum=3)
TODO: prevent_ast(ast_name: str) 
TODO: prevent_traced_call(function_name: str)# Whether it was detected dynamically
TODO: prevent_name(variable_name: str)
TODO: prevent_assignment(variable_name: str, type: str, value: Any)
TODO: prevent_iteration(style: {"For", "While", "Functional", "Recursion"})
TODO: ensure_function

ensure_prints(count)
    ensure_function_call('print', at_least=count)
    ensure_function_call('print', at_most=count)
function_prints => ensure_function_call('print', root=match_signature('name')

"""


@CompositeFeedbackFunction(prevent_function_call, ensure_function_call)
def ensure_prints_exactly(count, **kwargs):
    """
    DEPRECATED.

    Used to ensure that the student's code calls the print function a certain
    number of times.

    Args:
        count (int): The minimum and maximum number of times you can call print.

    Returns:
        bool: Whether or not both the maximum and minimum was met.
    """
    return (ensure_function_call('print', at_least=count, **kwargs) and
            prevent_function_call('print', at_most=count, **kwargs))
