"""
instructions: blah blah blah

settings:
    tifa:
        enabled: True
    unit test by function (bool): Whether to test each function entirely before moving onto the
            next one, or to first check that all functions have been defined, and then
            checking their parameters, etc. Defaults to True.
    show case details (bool): Whether to show the specific args/inputs that caused a test case
            to fail.
rubric:
    functions:
        total: 100
        definition: 10
        signature: 10
        cases: 80
global:
    variables:
        name:
        type:
        value:
    inputs:
    prints:
# Sandbox, type checking
functions:
    documentation: "any" or "google"
    coverage: 100%
    tests: int
    name: do_complicated_stuff
    arity: int
    signature: int, int -> float
    signature: int, int, list[int], (int->str), dict[str:list[int]] -> list[int]
    parameters:
        name: banana
            exactly:
            regex:
            includes:
            within:
        type: int
    cases:
      - arguments (list): 5, 4
        inputs (list):
        returns (Any):
            equals: 27.3
            is:
            is not: _1
        name (str): Meaningful name for tracking purposes? Or possibly separate into label/id/code
        hint (str): Message to display to user
        prints:
            exactly:
            regex:
            startswith:
            endswith:
        plots:
# Cait
syntax:
    prevent:
        ___ + ___
# Override any of our default feedback messages
messages:
    FUNCTION_NOT_DEFINED: "Oops you missed a function"
"""
from pedal.core.commands import set_success, give_partial
from pedal.core.feedback_category import FeedbackCategory
from pedal.questions.constants import TOOL_NAME

from pedal.sandbox.commands import get_sandbox
from pedal.utilities.comparisons import equality_test

SETTING_SHOW_CASE_DETAILS = "show case details"
DEFAULT_SETTINGS = {
    SETTING_SHOW_CASE_DETAILS: True
}

EXAMPLE_DATA = {
    'functions': [{
        'name': 'do_complicated_stuff',
        'signature': 'int, int, [int] -> list[int]',
        'cases': [
            {'arguments': "5, 4, 3", 'returns': "12"},
        ]
    }]
}


class FeedbackException(Exception):
    """

    """
    def __init__(self, category, label, **fields):
        self.category = category
        self.label = label
        self.fields = fields

    def as_message(self):
        """

        Returns:

        """
        return FEEDBACK_MESSAGES[self.category][self.label].format(**self.fields)


def check_function_defined(function, function_definitions, settings=None):
    """

    Args:
        function:
        function_definitions:
        settings:

    Returns:

    """
    # 1. Is the function defined syntactically?
    # 1.1. With the right name?
    function_name = function['name']
    if function_name not in function_definitions:
        raise FeedbackException(FeedbackCategory.SPECIFICATION, 'missing_function', function_name=function_name)
    definition = function_definitions[function_name]
    return definition


def check_function_signature(function, definition, settings=None):
    """

    Args:
        function:
        definition:
        settings:

    Returns:

    """
    function_name = function['name']
    # 1.2. With the right parameters and return type?
    # 1.2.1 'arity' style - simply checks number of parameters
    if 'arity' in function or 'parameters' in function:
        expected_arity = function['arity'] if 'arity' in function else len(function['parameters'])
        actual_arity = len(definition.args.args)
        if actual_arity < expected_arity:
            raise FeedbackException(FeedbackCategory.SPECIFICATION, 'insufficient_args',
                                    function_name=function_name, expected_arity=expected_arity,
                                    actual_arity=actual_arity)
        elif actual_arity > expected_arity:
            raise FeedbackException(FeedbackCategory.SPECIFICATION, 'excessive_args',
                                    function_name=function_name, expected_arity=expected_arity,
                                    actual_arity=actual_arity)
    # 1.2.2 'parameters' style - checks each parameter's name and type
    if 'parameters' in function:
        expected_parameters = function['parameters']
        actual_parameters = definition.args.args
        for expected_parameter, actual_parameter in zip(expected_parameters, actual_parameters):
            actual_parameter_name = get_arg_name(actual_parameter)
            if 'name' in expected_parameter:
                if actual_parameter_name != expected_parameter['name']:
                    raise FeedbackException(FeedbackCategory.SPECIFICATION, 'wrong_parameter_name',
                                            function_name=function_name,
                                            expected_parameter_name=expected_parameter['name'],
                                            actual_parameter_name=actual_parameter_name
                                            )
            if 'type' in expected_parameter:
                actual_parameter_type = parse_type(actual_parameter)
                # TODO: Handle non-string expected_parameter types (dict)
                expected_parameter_type = parse_type_value(expected_parameter['type'], True)
                if not type_check(expected_parameter_type, actual_parameter_type):
                    raise FeedbackException(FeedbackCategory.SPECIFICATION, 'wrong_parameter_type',
                                            function_name=function_name,
                                            parameter_name=actual_parameter_name,
                                            expected_parameter_type=expected_parameter_type,
                                            actual_parameter_type=actual_parameter_type)
    # 1.2.3. 'returns' style - checks the return type explicitly
    if 'returns' in function:
        expected_returns = parse_type_value(function['returns'], True)
        actual_returns = parse_type(definition.returns)
        if actual_returns != "None":
            if not type_check(expected_returns, actual_returns):
                raise FeedbackException(FeedbackCategory.SPECIFICATION, "wrong_returns",
                                        function_name=function_name, expected_returns=expected_returns,
                                        actual_returns=actual_returns)
        elif expected_returns != "None":
            raise FeedbackException(FeedbackCategory.SPECIFICATION, "missing_returns",
                                    function_name=function_name, expected_returns=expected_returns)
    # 1.2.4. 'signature' style - shortcut for specifying the types
    if 'signature' in function:
        expected_signature = function['signature']
        actual_returns = parse_type(definition.returns)
        actual_parameters = ", ".join(parse_type(actual_parameter.annotation)
                                      for actual_parameter in definition.args.args)
        actual_signature = "{} -> {}".format(actual_parameters, actual_returns)
        if not type_check(expected_signature, actual_signature):
            raise FeedbackException(FeedbackCategory.SPECIFICATION, "wrong_signature",
                                    function_name=function_name, expected_signature=expected_signature,
                                    actual_signature=actual_signature)
    # All good here!
    return True


def check_function_value(function, values, settings):
    """
    2. Does the function exist in the data?

    :param function:
    :param values:
    :param settings:
    :return:
    """
    function_name = function['name']
    # 2.1. Does the name exist in the values?
    if function_name not in values:
        raise FeedbackException(FeedbackCategory.SPECIFICATION, "function_not_available", function_name=function_name)
    function_value = values[function_name]
    # 2.2. Is the name bound to a callable?
    if not callable(function_value):
        raise FeedbackException(FeedbackCategory.SPECIFICATION, "name_is_not_function", function_name=function_name)
    # All good here
    return function_value


class TestCase:
    """

    """
    CASE_COUNT = 0
    def __init__(self, function_name, case_name):
        self.function_name = function_name
        if case_name is None:
            self.case_name = str(TestCase.CASE_COUNT)
            TestCase.CASE_COUNT += 1
        else:
            self.case_name = case_name
        self.arguments, self.has_arguments = [], False
        self.inputs, self.has_inputs = [], False
        self.error, self.has_error = None, False
        self.message, self.has_message = None, False
        self.expected_prints, self.has_expected_prints = None, False
        self.expected_returns, self.has_expected_returns = None, False
        self.prints = []
        self.returns = None
        self.success = True

    def add_message(self, message):
        """

        Args:
            message:
        """
        self.message = message
        self.has_message = True

    def add_inputs(self, inputs):
        """

        Args:
            inputs:
        """
        if not isinstance(inputs, list):
            inputs = [inputs]
        self.inputs = inputs
        self.has_inputs = True

    def add_arguments(self, arguments):
        """

        Args:
            arguments:
        """
        if not isinstance(arguments, list):
            arguments = [arguments]
        self.arguments = arguments
        self.has_arguments = True

    def add_error(self, error):
        """

        Args:
            error:
        """
        self.error = error
        self.has_error = True
        self.success = False

    def add_expected_prints(self, prints):
        """

        Args:
            prints:
        """
        self.expected_prints = prints
        self.has_expected_prints = True

    def add_expected_returns(self, returns):
        """

        Args:
            returns:
        """
        self.expected_returns = returns
        self.has_expected_returns = True

    def add_prints_returns(self, prints, returns):
        """

        Args:
            prints:
            returns:
        """
        self.prints = prints
        self.returns = returns

    def fail(self):
        """

        """
        self.success = False

def check_case(function, case, student_function):
    """

    :param function:
    :param case:
    :param student_function:
    :return: status, arg, input, error, output, return, message
    """
    function_name = function['name']
    test_case = TestCase(function_name, case.get('name'))
    # Get callable
    sandbox = get_sandbox(MAIN_REPORT)
    sandbox.clear_output()
    # Potential bonus message
    if 'message' in case:
        test_case.add_message(case['message'])
    # Queue up the the inputs
    if 'inputs' in case:
        test_case.add_inputs(case['inputs'])
        sandbox.set_input(test_case.inputs)
    else:
        sandbox.clear_input()
    # Pass in the arguments and call the function
    if 'arguments' in case:
        test_case.add_arguments(case['arguments'])
    result = sandbox.call(function_name, *test_case.arguments)
    # Store actual values
    test_case.add_prints_returns(sandbox.output, result)
    # Check for errors
    if sandbox.exception:
        test_case.add_error(sandbox.exception)
    # 4. Check out the output
    if 'prints' in case:
        test_case.add_expected_prints(case['prints'])
        if not output_test(sandbox.output, case['prints'], False, .0001):
            test_case.fail()
    # 5. Check the return value
    if 'returns' in case:
        test_case.add_expected_returns(case['returns'])
        if not equality_test(result, case['returns'], True, .0001):
            test_case.fail()
    # TODO: Check the plots
    # Return results
    return test_case


# TODO: blockpy-feedback-unit => pedal-test-cases in BlockPy Client
TEST_TABLE_TEMPLATE = """<table class='pedal-test-cases table table-sm table-bordered table-hover'>
    <tr class='table-active'>
        <th></th>
        <th>Arguments</th>
        <th>Expected</th>
        <th>Returned</th>
    </tr>
    {body}
</table>"""
TEST_TABLE_FOOTER = "</table>"
TEST_TABLE_ROW_HEADER = "<tr class='table-active'>"
TEST_TABLE_ROW_NORMAL = "<tr>"
TEST_TABLE_ROW_FOOTER = "</tr>"
TEST_TABLE_ROW_INFO = "<tr class='table-info'>"
GREEN_CHECK = "        <td class='green-check-mark'>&#10004;</td>"
RED_X = "        <td>&#10060;</td>"
CODE_CELL = "        <td><code>{}</code></td>"
COLUMN_TITLES = ["", "Arguments", "Inputs", "Errors", "Expected", "Expected", "Returned", "Printed"]


def make_table(cases):
    """

    Args:
        cases:

    Returns:

    """
    body = []
    for case in cases:
        body.append("    <tr>")
        body.append(GREEN_CHECK if case.success else RED_X)
        body.append(CODE_CELL.format(", ".join(repr(arg) for arg in case.arguments)))
        if case.has_error:
            body.append("        <td colspan='2'>Error: <code>{}</code></td>".format(str(case.error)))
        else:
            body.append(CODE_CELL.format(repr(case.expected_returns)))
            body.append(CODE_CELL.format(repr(case.returns)))
        if not case.success and case.has_message:
            body.append("    </tr><tr><td colspan='4'>{}</td>".format(case.message))
        body.append("    </tr>")
    body = "\n".join(body)
    return TEST_TABLE_TEMPLATE.format(body=body)
    #if ((any(args) and any(inputs)) or
    #        (any(expected_outputs) and any(expected_returns)) or
    #        (any(actual_outputs) and any(actual_returns))):
    #    # Complex cells
    #    pass
    #else:
    # Simple table
    # Make header

    # row_mask = [True, any(args), any(inputs), False,
    #             any("returns" in reason for reason in reasons),
    #             any("prints" in reason for reason in reasons),
    #             any("returns" in reason for reason in reasons),
    #             any("prints" in reason for reason in reasons)]
    # header_cells = "".join("<th>{}</th>".format(title) for use, title in zip(row_mask, COLUMN_TITLES) if use)
    # body = [TEST_TABLE_ROW_HEADER.format(header_cells)]
    # for case in zip(
    #         statuses, args, inputs, errors, actual_outputs, actual_returns,
    #         expected_outputs, expected_returns):
    #     status, case = case[0], case[1:]
    #     print(row_mask[1:], case)
    #     def make_code(values):
    #         if values == None:
    #             return "<code>None</code>"
    #         elif isinstance(values, int):
    #             return "<code>{!r}</code>".format(values)
    #         else:
    #             return ", ".join("<code>{}</code>".format(repr(value)) for value in values)
    #     body.append(
    #         TEST_TABLE_ROW_NORMAL+
    #         (GREEN_CHECK if case[0] else RED_X)+
    #         "\n".join("    <td>{}</td>".format(make_code(values))
    #                   for use, values in zip(row_mask[1:], case) if use)+
    #         "</tr>\n"
    #     )
    # # Make each row
    # table = "{}\n{}\n{}".format(TEST_TABLE_HEADER, "\n    ".join(body), TEST_TABLE_FOOTER)
    # return table


def check_cases(function, student_function, settings):
    """

    Args:
        function:
        student_function:
        settings:
    """
    function_name = function['name']
    if 'cases' in function:
        cases = function['cases']
        test_cases = [check_case(function, case, student_function) for case in cases]
        success_cases = sum(test.success for test in test_cases)
        if success_cases < len(cases):
            if settings[SETTING_SHOW_CASE_DETAILS]:
                table = make_table(test_cases)
                raise FeedbackException(FeedbackCategory.SPECIFICATION, "failed_test_cases",
                                        function_name=function_name,
                                        cases_count=len(cases), failure_count=len(cases)-success_cases,
                                        table=table)
            else:
                raise FeedbackException(FeedbackCategory.SPECIFICATION, "failed_test_cases_count",
                                        function_name=function_name,
                                        cases_count=len(cases), failure_count=len(cases) - success_cases)


def get_arg_name(node):
    """

    Args:
        node:

    Returns:

    """
    name = node.id
    if name is None:
        return node.arg
    else:
        return name


def load_question(data):
    """

    :param data:
    :return:
    """
    ast = parse_program()
    student_data = commands.get_student_data()
    # Check that there aren't any invalid syntactical structures
    # Get all of the function ASTs in a dictionary
    function_definitions = {definition._name: definition
                            for definition in ast.find_all("FunctionDef")}
    settings = DEFAULT_SETTINGS.copy()
    settings.update(data.get('settings', {}))
    rubric = settings.get('rubric', {})
    function_points = 0
    if 'functions' in data:
        function_rubric = rubric.get('functions', {})
        successes = []
        for function in data['functions']:
            success = False
            try:
                definition = check_function_defined(function, function_definitions, settings)
                function_points += function_rubric.get('definition', 10)
                check_function_signature(function, definition, settings)
                function_points += function_rubric.get('signature', 10)
                student_function = check_function_value(function, student_data, settings)
                function_points += function_rubric.get('value', 0)
            except FeedbackException as fe:
                yield fe.as_message(), fe.label
            else:
                try:
                    check_cases(function, student_function, settings)
                except FeedbackException as fe:
                    success_ratio = (1.0 - fe.fields['failure_count'] / fe.fields['cases_count'])
                    function_points += function_rubric.get('cases', 80*success_ratio)
                    yield fe.as_message(), fe.label
                else:
                    function_points += function_rubric.get('cases', 80)
                    success = True
            successes.append(success)
        function_points /= len(data['functions'])
        if all(successes):
            set_success()
        else:
            give_partial(function_points, tool=TOOL_NAME,
                         justification="Passed some but not all unit tests")


def check_question(data):
    """

    Args:
        data:
    """
    results = list(load_question(data))
    if results:
        message, label = results[0]
        gently(message, label=label)


def check_pool(questions):
    """

    Args:
        questions:
    """
    pass


def load_file(filename):
    """

    Args:
        filename:
    """
    pass


FEEDBACK_MESSAGES = {
    FeedbackCategory.SPECIFICATION: {
        "missing_function": "No function named `{function_name}` was found.",
        "insufficient_args": ("The function named `{function_name}` "
                              "has fewer parameters ({actual_arity}) "
                              "than expected ({expected_arity})."),
        "excessive_args": ("The function named `{function_name}` "
                           "has more parameters ({actual_arity}) "
                           "than expected ({expected_arity})."),
        # TODO: missing_parameter that checks if parameter name exists, but is in the wrong place
        "wrong_parameter_name": ("Error in definition of `{function_name}`. "
                                 "Expected a parameter named `{expected_parameter_name}`, "
                                 "instead found `{actual_parameter_name}`."),
        "wrong_parameter_type": ("Error in definition of function `{function_name}` "
                                 "parameter `{parameter_name}`. Expected `{expected_parameter_type}`, "
                                 "instead found `{actual_parameter_type}`."),
        "missing_returns": ("Error in definition of function `{function_name}` return type. "
                            "Expected `{expected_returns}`, but there was no return type specified."),
        "wrong_returns": ("Error in definition of function `{function_name}` return type. "
                          "Expected `{expected_returns}`, instead found `{actual_returns}`."),
        "wrong_signature": ("Error in definition of function `{function_name}` signature. "
                            "Expected `{expected_signature}`, instead found `{actual_signature}`."),
        "name_is_not_function": "You defined `{function_name}`, but did not define it as a function.",
        "function_not_available": ("You defined `{function_name}` somewhere in your code, "
                                   "but it was not available in the top-level scope to be called. "
                                   "Perhaps you defined it inside another function or scope?"),
        "failed_test_cases": ("I ran your function <code>{function_name}</code> on my own test cases. "
                              "It failed {failure_count}/{cases_count} of my tests.\n{table}"),
        "failed_test_cases_count": ("I ran your function <code>{function_name}</code> on my own test cases. "
                                    "It failed {failure_count}/{cases_count} of my tests."),
    }
}
