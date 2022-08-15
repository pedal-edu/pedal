from pedal.assertions.feedbacks import AssertionFeedback
from pedal.core.report import MAIN_REPORT


class missing_dataclass(AssertionFeedback):
    """ Unconditionally asserts that the dataclass is missing. """
    title = "Missing Dataclass"
    message_template = "No dataclass named {name_message} was found."

    def __init__(self, name, **kwargs):
        report = kwargs.get("report", MAIN_REPORT)
        fields = kwargs.get("fields", {})
        fields['name'] = name
        fields['name_message'] = report.format.name(name)
        super().__init__(fields=fields, **kwargs)


class duplicate_dataclass_definition(AssertionFeedback):
    """ Unconditionally assert that the dataclass is redefined somewhere. """
    title = "Duplicate Dataclass Definition"
    message_template = ("The dataclass {name_message} was defined multiple times, "
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


class too_few_fields(AssertionFeedback):
    """ Too Few Fields """
    title = "Too Few Fields"
    message_template = ("The dataclass named {name_message} has fewer "
                        "fields ({found}) than expected ({expected}).")

    def __init__(self, name, found, expected, **kwargs):
        report = kwargs.get("report", MAIN_REPORT)
        fields = kwargs.get("fields", {})
        fields['name'] = name
        fields['name_message'] = report.format.name(name)
        fields['found'] = found
        fields['expected'] = expected
        super().__init__(fields=fields, **kwargs)


class too_many_fields(AssertionFeedback):
    """ Too Many Fields """
    title = "Too Many Fields"
    message_template = ("The dataclass named {name_message} has more "
                        "fields ({found}) than expected ({expected}).")

    def __init__(self, name, found, expected, **kwargs):
        report = kwargs.get("report", MAIN_REPORT)
        fields = kwargs.get("fields", {})
        fields['name'] = name
        fields['name_message'] = report.format.name(name)
        fields['found'] = found
        fields['expected'] = expected
        super().__init__(fields=fields, **kwargs)


class invalid_field_type(AssertionFeedback):
    """ Invalid field type """
    title = "Invalid Field Type"
    message_template = ("The dataclass named {name_message} has a field "
                        "named {field_message} with an invalid type.")

    def __init__(self, name, field, invalid_type, expected, **kwargs):
        report = kwargs.get("report", MAIN_REPORT)
        fields = kwargs.get("fields", {})
        fields['name'] = name
        fields['name_message'] = report.format.name(name)
        fields['field'] = field
        fields['field_message'] = report.format.name(field)
        fields['invalid_type'] = invalid_type
        fields['expected'] = expected
        super().__init__(fields=fields, **kwargs)


class missing_field_type(AssertionFeedback):
    """ Invalid field type """
    title = "Missing Field Type"
    message_template = ("The dataclass named {name_message} has a field "
                        "named {field_message}, but that field does "
                        "not have a type specified.")

    def __init__(self, name, field, expected, **kwargs):
        report = kwargs.get("report", MAIN_REPORT)
        fields = kwargs.get("fields", {})
        fields['name'] = name
        fields['name_message'] = report.format.name(name)
        fields['field'] = field
        fields['field_message'] = report.format.name(field)
        fields['expected'] = expected
        super().__init__(fields=fields, **kwargs)


class unknown_field(AssertionFeedback):
    """ Unknown Field """
    title = "Unknown Field"
    message_template = ("The dataclass named {name_message} had a field named {field_message} "
                        "but that field is not supposed to be there. Are you sure you got "
                        "the name right?")

    def __init__(self, name, field, **kwargs):
        report = kwargs.get("report", MAIN_REPORT)
        fields = kwargs.get("fields", {})
        fields['name'] = name
        fields['name_message'] = report.format.name(name)
        fields['field'] = field
        fields['field_message'] = report.format.name(field)
        super().__init__(fields=fields, **kwargs)


class wrong_fields_type(AssertionFeedback):
    """ Wrong Fields Type """
    title = "Wrong Fields Type"
    message_template = ("The dataclass named {name_message} has a field "
                        "named {field_message} that is {actual_message},"
                        " but should be {expected_message}.")

    def __init__(self, name, field, actual, expected, **kwargs):
        report = kwargs.get("report", MAIN_REPORT)
        fields = kwargs.get("fields", {})
        fields['name'] = name
        fields['name_message'] = report.format.name(name)
        fields['field'] = field
        fields['field_message'] = report.format.name(field)
        fields['actual'] = actual
        fields['actual_message'] = actual.precise_description()
        fields['expected'] = expected
        fields['expected_message'] = expected.precise_description()
        super().__init__(fields=fields, **kwargs)


class name_is_not_a_dataclass(AssertionFeedback):
    """ The name is not a dataclass """
    title = "Name Is Not a Dataclass"
    message_template = "You defined `{name_message}`, but did not define it as a dataclass."

    def __init__(self, name, **kwargs):
        report = kwargs.get("report", MAIN_REPORT)
        fields = kwargs.get("fields", {})
        fields['name'] = name
        fields['name_message'] = report.format.name(name)
        super().__init__(fields=fields, **kwargs)


class dataclass_not_available(AssertionFeedback):
    """ The name is not a dataclass """
    title = "Dataclass Not Available"
    message_template = ("You may have defined `{name_message}`, but it was not available"
                        " to be called in the top-level scope. Perhaps you mistakenly defined"
                        " it inside another dataclass or scope?")

    def __init__(self, name, **kwargs):
        report = kwargs.get("report", MAIN_REPORT)
        fields = kwargs.get("fields", {})
        fields['name'] = name
        fields['name_message'] = report.format.name(name)
        super().__init__(fields=fields, **kwargs)


class missing_dataclass_annotation(AssertionFeedback):
    """ The dataclass is missing the annotation """
    title = "Dataclass Annotation Missing"
    message_template = ("You have defined {name_message}, but you did not include"
                        " the {dc_annotation} annotation. Make sure you import and include"
                        " the {dc_annotation} annotation directly before the class definition.")

    def __init__(self, name, **kwargs):
        report = kwargs.get("report", MAIN_REPORT)
        fields = kwargs.get("fields", {})
        fields['name'] = name
        fields['name_message'] = report.format.name(name)
        fields['dc_annotation'] = report.format.code('@dataclass')
        super().__init__(fields=fields, **kwargs)
