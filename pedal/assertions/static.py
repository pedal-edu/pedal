"""
Collection of feedback functions related to static checks of student code.
"""
from pedal.assertions.functions import *
from pedal.cait.cait_api import parse_program
from pedal.assertions.feedbacks import AssertionFeedback
from pedal.cait.find_node import find_operation, find_function_calls, find_function_definition
from pedal.core.feedback import CompositeFeedbackFunction
from pedal.core.location import Location
from pedal.core.report import MAIN_REPORT
from pedal.core.commands import compliment as core_compliment, give_partial
from pedal.types.normalize import normalize_type
from pedal.types.operations import are_types_equal
from pedal.utilities.ast_tools import AST_NODE_NAMES


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
            self.update_location(Location.from_ast(calls[-1]))
        return self._check_usage('call_count', calls)


class ensure_function_call(EnsureAssertionFeedback):
    """
    Determine that a function was definitely called by statically checking
    the students' code.

    # TODO: Allow parameter to force this to be a method xor/or function call
    # TODO: Allow set to be passed in for OR, or list for AND, for multiples

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
            self.update_location(Location.from_ast(uses[-1]))
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
            self.update_location(Location.from_ast(uses[-1]))
        return self._check_usage('use_count', uses)


class prevent_literal(PreventAssertionFeedback):
    """ Make sure that the given literal value does not appear in the student's
    code. """
    title = "May Not Use Literal Value"
    message_template = ("You used the literal value {literal_message:python_expression} on line "
                        "{location.line}. You may not use that value"
                        "{capacity}.")

    def __init__(self, literal, at_most=0, root=None, **kwargs):
        report = kwargs.get('report', MAIN_REPORT)
        root = root or parse_program(report=report)
        fields = {'literal': literal, 'at_most': at_most, 'capacity': '',
                  'root': root, 'literal_message': repr(literal)}
        super(AssertionFeedback, self).__init__(fields=fields, **kwargs)

    def condition(self):
        literal = self.fields['literal']
        uses = self.fields['root'].find_matches(repr(literal))
        if uses:
            self.update_location(uses[-1].match_location(False))
        return self._check_usage('use_count', uses)


class ensure_literal(EnsureAssertionFeedback):
    """ Make sure that the given literal value does appear in the student's
        code. """
    title = "Must Use Literal Value"
    message_template = "You must use the literal value {literal_message}{capacity}."

    def __init__(self, literal, at_least=1, root=None, **kwargs):
        report = kwargs.get('report', MAIN_REPORT)
        root = root or parse_program(report=report)
        fields = {'literal': literal, 'at_least': at_least, 'capacity': '',
                  'root': root, 'literal_message': report.format.python_expression(repr(literal))}
        super(AssertionFeedback, self).__init__(fields=fields, **kwargs)

    def condition(self):
        literal = self.fields['literal']
        uses = self.fields['root'].find_matches(repr(literal))
        if uses:
            self.update_location(uses[-1].match_location(False))
        return self._check_usage('use_count', uses)


class prevent_literal_type(PreventAssertionFeedback):
    """ Make sure that the given literal value does not appear in the student's
    code. """
    title = "May Not Use Type of Literal Value"
    message_template = ("You used the literal value type "
                        "{literal_type_message:python_expression} on line {location.line}."
                        " You may not use that type of value{capacity}.")

    def __init__(self, literal_type, at_most=0, root=None, **kwargs):
        report = kwargs.get('report', MAIN_REPORT)
        root = root or parse_program(report=report)
        fields = {'literal_type': literal_type, 'at_most': at_most,
                  'capacity': '', 'root': root,
                  'literal_type_message': literal_type.__name__}
        super(AssertionFeedback, self).__init__(fields=fields, **kwargs)

    def condition(self):
        literal_type = self.fields['literal_type']
        if literal_type == bool:
            uses = (self.fields['root'].find_matches("False") +
                    self.fields['root'].find_matches("True"))
            uses = [match.match_root for match in uses]
        elif literal_type == str:
            uses = self.fields['root'].find_all("Str")
        elif literal_type in (int, float):
            uses = [node for node in self.fields['root'].find_all("Num")
                    if isinstance(node.value, literal_type)]
        elif literal_type == list:
            uses = self.fields['root'].find_all("List")
        elif literal_type == dict:
            uses = self.fields['root'].find_all("Dict")
        else:
            raise ValueError(f"Unknown literal type: {literal_type}")
        if uses:
            self.update_location(uses[-1].lineno)
        return self._check_usage('use_count', uses)


class ensure_literal_type(EnsureAssertionFeedback):
    """ Make sure that the given type of literal value does appear in the
    student's code. """
    title = "Must Use Type of Literal Value"
    message_template = "You must use a literal value of type {literal_type_message:python_expression}{capacity}."

    def __init__(self, literal_type, at_least=1, root=None, **kwargs):
        report = kwargs.get('report', MAIN_REPORT)
        root = root or parse_program(report=report)
        fields = {'literal_type': literal_type, 'at_least': at_least,
                  'capacity': '', 'root': root,
                  'literal_type_message': literal_type.__name__}
        super(AssertionFeedback, self).__init__(fields=fields, **kwargs)

    def condition(self):
        literal_type = self.fields['literal_type']
        if literal_type == bool:
            uses = (self.fields['root'].find_matches("False")+
                    self.fields['root'].find_matches("True"))
            uses = [match.match_root for match in uses]
        elif literal_type == str:
            uses = self.fields['root'].find_all("Str")
        elif literal_type in (int, float):
            uses = [node for node in self.fields['root'].find_all("Num")
                    if isinstance(node.value, literal_type)]
        elif literal_type == list:
            uses = self.fields['root'].find_all("List")
        elif literal_type == dict:
            uses = self.fields['root'].find_all("Dict")
        else:
            raise ValueError(f"Unknown literal type: {literal_type}")
        if uses:
            self.update_location(uses[-1].lineno)
        return self._check_usage('use_count', uses)

class prevent_ast(PreventAssertionFeedback):
    """
    Determines if the given ast `name` is not used anywhere, returning
    the node of it if it is. You can refer to Green Tree Snakes documentation
    for more information about AST Names:

        https://greentreesnakes.readthedocs.io/en/latest/nodes.html

    Args:
        name (str): The name of the function (e.g., ``'sum'``)
        at_most (int): The maximum number of times you are allowed to use this
            AST. Defaults to ``0``.
    """
    title = "May Not Use Code"
    message_template = ("You used {name_message} on line "
                        "{location.line}. You may not use that"
                        "{capacity}.")

    def condition(self):
        """ Use find_all to check number of occurrences. """
        name = self.fields['name']
        self.fields['name_message'] = AST_NODE_NAMES.get(name, name)
        uses = list(self.fields['root'].find_all(name))
        if uses:
            self.update_location(Location.from_ast(uses[-1]))
        return self._check_usage('use_count', uses)


class ensure_ast(EnsureAssertionFeedback):
    """
    Determines if the given ast `name` is used anywhere, returning
    the node of it if it is. You can refer to Green Tree Snakes documentation
    for more information about AST Names:

        https://greentreesnakes.readthedocs.io/en/latest/nodes.html

    Args:
        name (str): The name of the node.
        at_least (int): The minimum number of times you must use this
            node. Defaults to ``1``.
    """
    title = "Must Use Code"
    message_template = "You must use {name_message}{capacity}."

    def condition(self):
        """ Use find_all to check number of occurrences. """
        name = self.fields['name']
        self.fields['name_message'] = AST_NODE_NAMES.get(name, name)
        uses = list(self.fields['root'].find_all(name))
        if uses:
            self.update_location(Location.from_ast(uses[-1]))
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
    return ensure_function_call('print',
                                root=find_function_definition(function_name))


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
                        " {names_message}.")

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
                                a_def.body[0].value.ast_name not in ("Str", "Constant"))):
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
prevent_ast(ast_name: str)

TODO: prevent_source_text(code: str, missing=False, minimum=2, maximum=3)
TODO: prevent_traced_call(function_name: str)# Whether it was detected dynamically
TODO: prevent_name(variable_name: str)
TODO: prevent_assignment(variable_name: str, type: str, value: Any)
TODO: ensure_function

ensure_prints(count)
    ensure_function_call('print', at_least=count)
    ensure_function_call('print', at_most=count)
function_prints => ensure_function_call('print', root=match_signature('name')

"""


# TODO: wait, is this a positive feedback group waiting to happen?

@CompositeFeedbackFunction(missing_function, duplicate_function_definition)
def ensure_function(name, arity=None, parameters=None,
                    returns=None, root=None, compliment=False, **kwargs):
    """ Checks that the function exists and has the right signature. """
    report = kwargs.get('report', MAIN_REPORT)
    root = root or parse_program(report=report)
    defs = root.find_all('FunctionDef')
    defs = [a_def for a_def in defs if a_def._name == name]
    if not defs:
        return missing_function(name, **kwargs)
    if len(defs) > 1:
        lines = [Location.from_ast(a_def) for a_def in defs]
        return duplicate_function_definition(name, lines, **kwargs)
    definition = defs[0]
    # Actual logic
    # 1.2.1 'arity' style - simply checks number of parameters
    if arity is not None or parameters is not None:
        expected_arity = arity if arity is not None else len(parameters)
        actual_arity = len(definition.args.args)
        if actual_arity < expected_arity:
            return too_few_parameters(name, actual_arity, expected_arity, **kwargs)
        elif actual_arity > expected_arity:
            return too_many_parameters(name, actual_arity, expected_arity, **kwargs)
    # 1.2.2 'parameters' style - checks each parameter's name and type
    if parameters is not None:
        actual_parameters = definition.args.args
        for expected_parameter, actual_parameter in zip(parameters, actual_parameters):
            expected_parameter_type = normalize_type(expected_parameter)
            actual_parameter_name = (actual_parameter.id if actual_parameter.id is not None
                                     else actual_parameter.arg)
            if actual_parameter.annotation is None:
                return missing_parameter_type(name, actual_parameter_name,
                                              expected_parameter_type,
                                              **kwargs)
            try:
                actual_parameter_type = normalize_type(actual_parameter.annotation.ast_node)
            except ValueError as e:
                return invalid_parameter_type(name, actual_parameter_name,
                                              actual_parameter.annotation,
                                              expected_parameter_type,
                                              **kwargs)
            if not are_types_equal(actual_parameter_type, expected_parameter_type):
                return wrong_parameter_type(name, actual_parameter_name,
                                            actual_parameter_type,
                                            expected_parameter_type, **kwargs)
    # 1.2.3. 'returns' style - checks the return type explicitly
    if returns is not None:
        expected_returns = normalize_type(returns)
        if definition.returns is None:
            return missing_return_type(name, expected_returns, **kwargs)
        try:
            actual_returns = normalize_type(definition.returns.ast_node)
        except ValueError as e:
            return invalid_return_type(name, definition.returns,
                                       expected_returns, **kwargs)
        if not are_types_equal(actual_returns, expected_returns):
            return wrong_return_type(name, actual_returns, expected_returns,
                                     **kwargs)
    # Alternatively, returns positive FF?
    if compliment:
        if isinstance(compliment, str):
            core_compliment(compliment, label="function_defined", **kwargs)
        elif compliment is True:
            core_compliment(f"Defined {name}", label="function_defined", **kwargs)
    elif kwargs.get("score"):
        give_partial(kwargs.pop("score"), label="function_defined", **kwargs)

    return None


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


class ensure_starting_code(AssertionFeedback):
    """Detects if the given code is missing."""
    title = "Don't Change Starting Code"
    message_template = "You have changed or removed the starting code. "

    def __init__(self, code, root=None, **kwargs):
        report = kwargs.get('report', MAIN_REPORT)
        root = root or parse_program(report=report)
        fields = {'code': code, 'root': root}
        super().__init__(fields=fields, **kwargs)

    def condition(self):
        """ Traverse the AST to find matches. """
        code = self.fields['code']
        ast = self.fields['root']
        return not ast.find_match(code)


class prevent_embedded_answer(AssertionFeedback):
    """ Detects if the given code is present. """
    title = "Don't Write Answer Directly"
    message_template = ("You have embedded the answer directly in your code, "
                        "instead of writing code to compute the answer.")

    def __init__(self, code, root=None, **kwargs):
        report = kwargs.get('report', MAIN_REPORT)
        root = root or parse_program(report=report)
        fields = {'code': code, 'root': root}
        super().__init__(fields=fields, **kwargs)

    def condition(self):
        """ Traverse the AST to find matches. """
        code = self.fields['code']
        ast = self.fields['root']
        return ast.find_match(code)
