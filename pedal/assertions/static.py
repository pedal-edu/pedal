"""

"""
from pedal.cait.cait_api import parse_program
from pedal.assertions.feedbacks import AssertionFeedback
from pedal.cait.find_node import find_operation, find_function_calls
from pedal.core.location import Location
from pedal.core.report import MAIN_REPORT
from pedal.toolkit.functions import match_signature


class EnsureAssertionFeedback(AssertionFeedback):
    """ Abstract base class for assertions preventing things. """
    def __init__(self, name, at_least=1, root=None, **kwargs):
        root = root or parse_program(report=kwargs.get('report', MAIN_REPORT))
        fields = {'name': name, 'at_least': at_least, 'capacity': '',
                  'root': root}
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
        root = root or parse_program(report=kwargs.get('report', MAIN_REPORT))
        fields = {'name': name, 'at_most': at_most, 'capacity': '',
                  'root': root}
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
    Determine if a function was ever called.

    # TODO: also check the TIFA records to see if the function was read

    Args:
        name (str): The name of the function (e.g., ``'sum'``)
        at_most (int): The maximum number of times you are allowed to call this
            function. Defaults to ``0``.
    """

    title = "May Not Use Function"
    message_template = ("You used the function `{name}` on line "
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
    Determine that a function was definitely called.

    # TODO: also check the TIFA records to see if the function was read

    Args:
        name (str): The name of the function (e.g., ``'sum'``)
        at_most (int): The maximum number of times you are allowed to call this
            function. Defaults to ``0``.
    """

    title = "Must Use Function"
    message_template = "You must use the function `{name}`{capacity}."

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
    message_template = ("You used the operator `{name}` on line "
                        "{location.line}. You may not use that operator"
                        "{capacity}.")

    def condition(self):
        """ Use find_matches to check number of occurrences. """
        name = self.fields['name']
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
    message_template = "You must use the operator `{name}`{capacity}."

    def condition(self):
        """ Use find_matches to check number of occurrences. """
        name = self.fields['name']
        uses = list(find_operation(name, root=self.fields['root']))
        if uses:
            self.fields['location'] = Location.from_ast(uses[-1])
        return self._check_usage('use_count', uses)


class prevent_literal(PreventAssertionFeedback):
    title = "May Not Use Literal Value"
    message_template = ("You used the literal value `{literal!r}` on line "
                        "{location.line}. You may not use that value"
                        "{capacity}.")

    def __init__(self, literal, at_most=0, root=None, **kwargs):
        root = root or parse_program(report=kwargs.get('report', MAIN_REPORT))
        fields = {'literal': literal, 'at_most': at_most, 'capacity': '',
                  'root': root}
        super(AssertionFeedback, self).__init__(fields=fields, **kwargs)

    def condition(self):
        literal = self.fields['literal']
        uses = self.fields['root'].find_matches(repr(literal))
        if uses:
            self.fields['location'] = uses[-1].match_location(False)
        return self._check_usage('use_count', uses)


class ensure_literal(EnsureAssertionFeedback):
    title = "Must Use Literal Value"
    message_template = "You must use the literal value `{literal!r}`{capacity}."

    def __init__(self, literal, at_least=1, root=None, **kwargs):
        root = root or parse_program(report=kwargs.get('report', MAIN_REPORT))
        fields = {'literal': literal, 'at_least': at_least, 'capacity': '',
                  'root': root}
        super(AssertionFeedback, self).__init__(fields=fields, **kwargs)

    def condition(self):
        literal = self.fields['literal']
        uses = self.fields['root'].find_matches(repr(literal))
        if uses:
            self.fields['location'] = uses[-1].match_location(False)
        return self._check_usage('use_count', uses)


"""
New assertions:

TODO: prevent_source_text(code: str, missing=False, minimum=2, maximum=3)
prevent_literal(literal_value: Any)
TODO: prevent_ast(ast_name: str)
prevent_function_call(function_name: str) # Whether it was detected statically 
TODO: prevent_traced_call(function_name: str)# Whether it was detected dynamically
TODO: prevent_name(variable_name: str)
prevent_operation(operator: str)
TODO: prevent_assignment(variable_name: str, type: str, value: Any)
TODO: prevent_import(module_name: str)
TODO: prevent_iteration(style: {"For", "While", "Functional", "Recursion"})
TODO: ensure_function

ensure_prints => ensure_function_call('print')
function_prints => ensure_function_call('print', root=match_signature('name')

"""

def function_prints(function_name):
    return ensure_function_call('print', root=match_signature(function_name))
