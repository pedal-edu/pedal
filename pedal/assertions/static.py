"""
Collection of feedback functions related to static checks of student code.
"""
try:
    import dataclasses
except ImportError:
    dataclasses = None
import ast

from pedal.assertions.classes import (missing_dataclass, dataclass_not_available,
                                      missing_field_type, too_few_fields, too_many_fields,
                                      duplicate_dataclass_definition, invalid_field_type,
                                      wrong_fields_type, name_is_not_a_dataclass, missing_dataclass_annotation,
                                      unknown_field, wrong_field_order)
from pedal.assertions.functions import *
from pedal.cait.cait_api import parse_program, find_match, find_matches
from pedal.assertions.feedbacks import AssertionFeedback
from pedal.cait.find_node import find_operation, find_function_calls, find_function_definition
from pedal.core.feedback import CompositeFeedbackFunction, Feedback, FeedbackResponse
from pedal.core.location import Location
from pedal.core.report import MAIN_REPORT
from pedal.core.commands import compliment as core_compliment, give_partial, explain, gently
from pedal.tifa.commands import tifa_type_check
from pedal.types.normalize import normalize_type
from pedal.types.new_types import is_subtype
from pedal.utilities.ast_tools import AST_NODE_NAMES


class EnsureAssertionFeedback(AssertionFeedback):
    """ Abstract base class for assertions preventing things. """
    def __init__(self, name, at_least=1, root=None, **kwargs):
        report = kwargs.get('report', MAIN_REPORT)
        root = root or parse_program(report=report)
        root_message = "" if not root else " (inside of some other code)"
        fields = {'name': name, 'at_least': at_least, 'capacity': '',
                  'root': root, 'name_message': report.format.name(name),
                  'root_message': root_message}
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
        root_message = "" if not root else " (inside of some other code)"
        fields = {'name': name, 'at_most': at_most, 'capacity': '',
                  'root': root, 'name_message': report.format.name(name),
                  'root_message': root_message}
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


ensure_operator = ensure_operation
prevent_operator = prevent_operation


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


# TODO: ensure_literal does not recognize None?
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
    justification_template = ("Incorrectly found a {name_message}{capacity}{root_message}.",
                              "Correctly found a {name_message}{capacity}{root_message}.")

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
    justification_template = ("Failed to find a {name_message}{capacity}{root_message}.",
                              "Successfully found a {name_message}{capacity}{root_message}.")

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

@CompositeFeedbackFunction(missing_function, duplicate_function_definition,
                           too_few_parameters, too_many_parameters,
                           missing_parameter_type, invalid_parameter_type,
                           wrong_parameter_type, wrong_return_type,
                           missing_return_type)
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
            expected_parameter_type = normalize_type(expected_parameter, tifa_type_check).as_type()
            actual_parameter_name = (actual_parameter.id if actual_parameter.id is not None
                                     else actual_parameter.arg)
            if actual_parameter.annotation is None:
                return missing_parameter_type(name, actual_parameter_name,
                                              expected_parameter_type,
                                              **kwargs)
            try:
                actual_parameter_type = normalize_type(actual_parameter.annotation.ast_node,
                                                       tifa_type_check).as_type()
            except ValueError as e:
                return invalid_parameter_type(name, actual_parameter_name,
                                              actual_parameter.annotation,
                                              expected_parameter_type,
                                              **kwargs)
            if not is_subtype(actual_parameter_type, expected_parameter_type):
                return wrong_parameter_type(name, actual_parameter_name,
                                            actual_parameter_type,
                                            expected_parameter_type, **kwargs)
    # 1.2.3. 'returns' style - checks the return type explicitly
    if returns is not None:
        expected_returns = normalize_type(returns, tifa_type_check).as_type()
        if definition.returns is None:
            return missing_return_type(name, expected_returns, **kwargs)
        try:
            actual_returns = normalize_type(definition.returns.ast_node,
                                            tifa_type_check).as_type()
        except ValueError as e:
            return invalid_return_type(name, definition.returns,
                                       expected_returns, **kwargs)
        if not is_subtype(actual_returns, expected_returns):
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


@CompositeFeedbackFunction(missing_dataclass, duplicate_dataclass_definition,
                           too_few_fields, too_many_fields, invalid_field_type,
                           unknown_field,
                           missing_field_type, wrong_fields_type, name_is_not_a_dataclass,
                           dataclass_not_available, missing_dataclass_annotation)
def ensure_dataclass(name, fields=None, root=None, compliment=False, **kwargs):
    """
    Ensures that the actual definition for the given class exists.
    You can provide either a string and fields, or an instructor-defined version

    Arguments:
        name (str or dataclass): Either the name of the expected dataclass, or a
            dataclass object (not an instance).
        fields (dict):
    """
    if isinstance(name, str):
        # Fields will be a dictionary or class
        if fields is None:
            fields = {}
    # Or assume it is a dataclass provided by the instructor
    else:
        fields = {field.name: field.type for field in dataclasses.fields(name)}
        name = name.__name__
    # Inspect the code for the definition
    report = kwargs.get('report', MAIN_REPORT)
    root = root or parse_program(report=report)
    defs = root.find_all('ClassDef')
    defs = [a_def for a_def in defs if a_def._name == name]
    if not defs:
        return missing_dataclass(name, **kwargs)
    if len(defs) > 1:
        lines = [Location.from_ast(a_def) for a_def in defs]
        return duplicate_dataclass_definition(name, lines, **kwargs)
    definition = defs[0]
    definition_fields = [line for line in definition.body
                         if isinstance(line.ast_node, ast.AnnAssign) and line.simple]
    # TODO: Support ast.Assign nodes for default values
    # 1. Make sure import is present
    missing_import = ensure_import('dataclasses')
    if missing_import:
        return missing_import
    for decorator in definition.decorator_list:
        # TODO: Support the @dataclasses.dataclass style too
        if isinstance(decorator.ast_node, ast.Name) and decorator.id == 'dataclass':
            break
    else:
        return missing_dataclass_annotation(name, **kwargs)
    # 2. Confirm the number of fields
    expected_arity = len(fields)
    actual_arity = len(definition_fields)
    if actual_arity < expected_arity:
        return too_few_fields(name, actual_arity, expected_arity, **kwargs)
    elif actual_arity > expected_arity:
        return too_many_fields(name, actual_arity, expected_arity, **kwargs)
    # 3. checks each field's name and type
    for actual_field in definition_fields:
        actual_field_name = actual_field.target.id
        if actual_field_name not in fields:
            return unknown_field(name, actual_field_name, **kwargs)
        expected_field = fields[actual_field_name]
        expected_field_type = normalize_type(expected_field, tifa_type_check).as_type()
        if actual_field.annotation is None:
            return missing_field_type(name, actual_field_name, expected_field_type, **kwargs)
        try:
            actual_field_type = normalize_type(actual_field.annotation.ast_node,
                                               tifa_type_check).as_type()
        except ValueError as e:
            return invalid_field_type(name, actual_field_name, actual_field.annotation,
                                      expected_field_type, **kwargs)
        if not is_subtype(actual_field_type, expected_field_type):
            return wrong_fields_type(name, actual_field_name, actual_field_type,
                                     expected_field_type, **kwargs)
    for actual_field, expected_field in zip(definition_fields, fields.keys()):
        actual_field_name = actual_field.target.id
        if actual_field_name != expected_field:
            return wrong_field_order(name, actual_field_name, expected_field, **kwargs)
    # Alternatively, returns positive FF?
    if compliment:
        if isinstance(compliment, str):
            core_compliment(compliment, label="dataclass_defined", **kwargs)
        elif compliment is True:
            core_compliment(f"Defined {name}", label="dataclass_defined", **kwargs)
    elif kwargs.get("score"):
        give_partial(kwargs.pop("score"), label="dataclass_defined", **kwargs)

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


class prevent_printing_functions(AssertionFeedback):
    """
    Detects if the user has defined a function with a print statement inside.

    Args:
        exceptions: A set of function names (or a single string) of functions to allow to print (e.g., `'main'`).
    """
    title = "Do Not Print in Function"
    message_template = ("The function {name} is printing on line {location.line:line}."
                        " However, that function is not supposed to print.")

    def __init__(self, exceptions=None, root=None, **kwargs):
        report = kwargs.get('report', MAIN_REPORT)
        root = root or parse_program(report=report)
        fields = {'root': root, 'exceptions': exceptions}
        super().__init__(fields=fields, **kwargs)

    def condition(self, *args, **kwargs):
        exceptions = self.fields['exceptions']
        if exceptions is None:
            exceptions = set()
        elif isinstance(exceptions, str):
            exceptions = {exceptions}
        root = self.fields['root']
        defs = root.find_all("FunctionDef")
        for a_def in defs:
            name = a_def._name
            if name in exceptions:
                continue
            for call in find_function_calls("print", root=a_def, report=self.report):
                location = call.locate()
                self.fields['name'] = name
                self.update_location(location)
                return True
        return False


class ensure_functions_return(AssertionFeedback):
    """
    Detects if the user has defined a function with a print statement inside.

    Args:
        exceptions: A set of function names (or a single string) of functions to allow to print (e.g., `'main'`).
    """
    title = "Must Return in Function"
    message_template = ("The function {name} is not returning."
                        " However, that function is supposed to have a return statement.")

    def __init__(self, exceptions=None, root=None, **kwargs):
        report = kwargs.get('report', MAIN_REPORT)
        root = root or parse_program(report=report)
        fields = {'root': root, 'exceptions': exceptions}
        super().__init__(fields=fields, **kwargs)

    def condition(self, *args, **kwargs):
        exceptions = self.fields['exceptions']
        if exceptions is None:
            exceptions = set()
        elif isinstance(exceptions, str):
            exceptions = {exceptions}
        root = self.fields['root']
        defs = root.find_all("FunctionDef")
        for a_def in defs:
            name = a_def._name
            if name in exceptions:
                continue
            if not a_def.find_match("return"):
                self.fields['name'] = name
                return True
        return False


class only_printing_variables(AssertionFeedback):
    """
    Determines whether the user is only printing variables, as opposed to
    literal values.

    """
    title="Print Variables, Not Values"
    message_template=("You printed something other than a variable on"
                      " line {location.line:line}. Although that is not a"
                      " normally an issue, we want you to practice printing"
                      " variables in this problem.")

    def __init__(self, root=None, **kwargs):
        fields = kwargs.setdefault('fields', {})
        report = kwargs.setdefault('report', MAIN_REPORT)
        fields['root'] = root or parse_program(report=report)
        super().__init__(**kwargs)

    def condition(self):
        """ Uses find_all to detect matches, ignoring named values. """
        print_calls = find_function_calls('print', root=self.fields['root'],
                                          report=self.report)
        for print_call in print_calls:
            for arg in print_call.args:
                if arg.ast_name != "Name":
                    self.update_location(print_call.lineno)
                    return True
                elif arg.id in ("True", "False", "None"):
                    self.update_location(print_call.lineno)
                    return True
        return False


ADVANCED_ITERATION_FUNCTIONS = [
    "sum", "map", "filter", "reduce",
    "len", "max", "min", "max",
    "sorted", "all", "any",
    "getattr", "setattr",
    "eval", "exec", "iter", "next"
]


@CompositeFeedbackFunction()
def prevent_advanced_iteration(allow_while=False, allow_for=False,
                               allow_function=None, **kwargs):
    """ Prevents the student from using certain advanced iteration functions
    and constructs. Does not currently support blocking recursion. """
    if isinstance(allow_function, str):
        allow_function = {allow_function}
    elif allow_function is None:
        allow_function = set()
    if not allow_while:
        prevent_ast("While")
    if not allow_for:
        prevent_ast("For")
    for function_name in ADVANCED_ITERATION_FUNCTIONS:
        if function_name not in allow_function:
            prevent_function_call(function_name, **kwargs)


class open_without_arguments(FeedbackResponse):
    """
    Detects if the user has called the `open` function without any arguments.
    """
    muted = False
    title = "Opened Without Arguments"
    message_template = ("You have called the `open` function "
                        "without any arguments. It needs a filename.")
    category = Feedback.CATEGORIES.INSTRUCTOR


@CompositeFeedbackFunction(open_without_arguments, ensure_literal)
def files_not_handled_correctly(*filenames, muted=False):
    """
    Statically detect if files have been opened and closed correctly.
    This is only useful in the case of very simplistic file handling.

    TODO: This could be vastly improved with line numbers and other information.
    """
    if filenames and isinstance(filenames[0], int):
        num_filenames = filenames[0]
        actual_filenames = False
    else:
        num_filenames = len(filenames)
        actual_filenames = True
    ast = parse_program()
    calls = ast.find_all("Call")
    called_open = []
    closed = []
    for a_call in calls:
        if a_call.func.ast_name == 'Name':
            if a_call.func.id == 'open':
                if not a_call.args:
                    open_without_arguments(muted)
                    return True
                called_open.append(a_call)
            elif a_call.func.id == 'close':
                explain("You have attempted to call `close` as a "
                        "function, but it is actually a method of the "
                        "file object.", label="used_close_as_function", title="Close Is a Method", priority='syntax')
                return True
        elif a_call.func.ast_name == 'Attribute':
            if a_call.func.attr == 'open':
                # TODO: Make these feedback functions
                explain("You have attempted to call `open` as a "
                        "method, but it is actually a built-in function.", label="used_open_as_method",
                        title="Open Is a Function")
                return True
            elif a_call.func.attr == 'close':
                closed.append(a_call)
    if len(called_open) < num_filenames:
        explain("You have not opened all the files you were supposed to.", label="unopened_files", title="Unopened Files")
        return True
    elif len(called_open) > num_filenames:
        explain("You have opened more files than you were supposed to.", label="extra_open_files", title="Extra Opened Files")
        return True
    withs = ast.find_all("With")
    if len(withs) + len(closed) < num_filenames:
        explain("You have not closed all the files you were supposed to.", label="unclosed_files", title="Unclosed Files")
        return True
    elif len(withs) + len(closed) > num_filenames:
        explain("You have closed more files than you were supposed to.", label="extra_closed_files", title="Extra Closed Files")
        return True
    if actual_filenames:
        for filename in filenames:
            ensured = ensure_literal(filename)
            if ensured:
                return ensured
    return False