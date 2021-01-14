from pedal.assertions.feedbacks import AssertionFeedback
from pedal.core.report import MAIN_REPORT


class missing_function(AssertionFeedback):
    """ Unconditionally asserts that the function is missing. """
    title = "Missing Function"
    message_template = "No function named {name_message} was found."

    def __init__(self, name, **kwargs):
        report = kwargs.get("report", MAIN_REPORT)
        fields = kwargs.get("fields", {})
        fields['name'] = name
        fields['name_message'] = report.format.name(name)
        super().__init__(fields=fields, **kwargs)


class duplicate_function_definition(AssertionFeedback):
    """ Unconditionally assert that the function is redefined somewhere. """
    title = "Duplicate Function Definition"
    message_template = ("The function {name_message} was defined multiple times, "
                        "on lines {lines_message}.")

    def __init__(self, name, lines, **kwargs):
        report = kwargs.get("report", MAIN_REPORT)
        fields = kwargs.get("fields", {})
        fields['name'] = name
        fields['name_message'] = report.format.name(name)
        lines_message = ", ".join(str(line) for line in lines[:-1])
        lines_message += " and " + str(lines[-1])
        fields['lines'] = lines
        fields['lines_message'] = lines
        super().__init__(fields=fields, **kwargs)


class too_few_parameters(AssertionFeedback):
    """ Too Few Parameters """
    title = "Too Few Parameters"
    message_template = ("The function named {name_message} has fewer "
                        "parameters ({found}) than expected ({expected}).")

    def __init__(self, name, found, expected, **kwargs):
        report = kwargs.get("report", MAIN_REPORT)
        fields = kwargs.get("fields", {})
        fields['name'] = name
        fields['name_message'] = report.format.name(name)
        fields['found'] = found
        fields['expected'] = expected
        super().__init__(fields=fields, **kwargs)


class too_many_parameters(AssertionFeedback):
    """ Too Many Parameters """
    title = "Too Many Parameters"
    message_template = ("The function named {name_message} has more "
                        "parameters ({found}) than expected ({expected}).")

    def __init__(self, name, found, expected, **kwargs):
        report = kwargs.get("report", MAIN_REPORT)
        fields = kwargs.get("fields", {})
        fields['name'] = name
        fields['name_message'] = report.format.name(name)
        fields['found'] = found
        fields['expected'] = expected
        super().__init__(fields=fields, **kwargs)


class invalid_parameter_type(AssertionFeedback):
    """ Invalid parameter type """
    title = "Invalid Parameter Type"
    message_template = ("The function named {name_message} has a parameter "
                        "named {parameter_message} with an invalid type.")

    def __init__(self, name, parameter, invalid_type, expected, **kwargs):
        report = kwargs.get("report", MAIN_REPORT)
        fields = kwargs.get("fields", {})
        fields['name'] = name
        fields['name_message'] = report.format.name(name)
        fields['parameter'] = parameter
        fields['parameter_message'] = report.format.name(parameter)
        fields['invalid_type'] = invalid_type
        fields['expected'] = expected
        super().__init__(fields=fields, **kwargs)


class missing_parameter_type(AssertionFeedback):
    """ Invalid parameter type """
    title = "Missing Parameter Type"
    message_template = ("The function named {name_message} has a parameter "
                        "named {parameter_message}, but that parameter does "
                        "not have a type specified.")

    def __init__(self, name, parameter, expected, **kwargs):
        report = kwargs.get("report", MAIN_REPORT)
        fields = kwargs.get("fields", {})
        fields['name'] = name
        fields['name_message'] = report.format.name(name)
        fields['parameter'] = parameter
        fields['parameter_message'] = report.format.name(parameter)
        fields['expected'] = expected
        super().__init__(fields=fields, **kwargs)


class wrong_parameter_type(AssertionFeedback):
    """ Wrong Parameter Type """
    title = "Wrong Parameter Type"
    message_template = ("The function named {name_message} has a parameter "
                        "named {parameter_message} that is {actual_message},"
                        " but should be {expected_message}.")

    def __init__(self, name, parameter, actual, expected, **kwargs):
        report = kwargs.get("report", MAIN_REPORT)
        fields = kwargs.get("fields", {})
        fields['name'] = name
        fields['name_message'] = report.format.name(name)
        fields['parameter'] = parameter
        fields['parameter_message'] = report.format.name(parameter)
        fields['actual'] = actual
        fields['actual_message'] = actual.precise_description()
        fields['expected'] = expected
        fields['expected_message'] = expected.precise_description()
        super().__init__(fields=fields, **kwargs)


class missing_return_type(AssertionFeedback):
    """ Missing Returns Type """
    title = "Missing Return Type"
    message_template = ("The function named {name_message} does not have a "
                        "return type specified in its header.")

    def __init__(self, name, expected, **kwargs):
        report = kwargs.get("report", MAIN_REPORT)
        fields = kwargs.get("fields", {})
        fields['name'] = name
        fields['name_message'] = report.format.name(name)
        fields['expected'] = expected
        super().__init__(fields=fields, **kwargs)


class invalid_return_type(AssertionFeedback):
    """ Invalid Return Type """
    title = "Invalid Return Type"
    message_template = ("The function named {name_message} has an invalid "
                        "return type in its header.")

    def __init__(self, name, returns, invalid_type, expected, **kwargs):
        report = kwargs.get("report", MAIN_REPORT)
        fields = kwargs.get("fields", {})
        fields['name'] = name
        fields['name_message'] = report.format.name(name)
        fields['returns'] = returns
        fields['invalid_type'] = invalid_type
        fields['expected'] = expected
        super().__init__(fields=fields, **kwargs)


class wrong_return_type(AssertionFeedback):
    """ Wrong Return Type """
    title = "Wrong Return Type"
    message_template = ("The function named {name_message} was expected to "
                        "return {expected_message}, but instead its header "
                        "specifies that it returns {actual_message}. ")

    def __init__(self, name, actual, expected, **kwargs):
        report = kwargs.get("report", MAIN_REPORT)
        fields = kwargs.get("fields", {})
        fields['name'] = name
        fields['name_message'] = report.format.name(name)
        fields['actual'] = actual
        fields['actual_message'] = actual.precise_description()
        fields['expected'] = expected
        fields['expected_message'] = expected.precise_description()
        super().__init__(fields=fields, **kwargs)
