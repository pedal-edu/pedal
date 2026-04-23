import re
from pedal.assertions.functions import *
from pedal.cait.cait_api import parse_program, find_match, find_matches
from pedal.assertions.feedbacks import AssertionFeedback
from pedal.cait.find_node import find_operation, find_function_calls, find_function_definition
from pedal.core.feedback import CompositeFeedbackFunction, Feedback, FeedbackResponse
from pedal.core.location import Location
from pedal.source import get_program
from pedal.core.report import MAIN_REPORT
from pedal.core.commands import compliment as core_compliment, give_partial, explain, gently
from pedal.tifa.commands import tifa_type_check
from pedal.types.normalize import normalize_type
from pedal.types.new_types import is_subtype
from pedal.utilities.ast_tools import AST_NODE_NAMES


class RequireAssertionFeedback(AssertionFeedback):
    """ Abstract base class for assertions requiring things. """
    priority = 'syntax'
    safe_field_names = ['code', 'at_least', 'capacity', 'code_message']

    def __init__(self, code, at_least=1, root=None, **kwargs):
        report = kwargs.get('report', MAIN_REPORT)
        fields = {'code': code, 'at_least': at_least, 'capacity': '',
                  'root': root, 'code_message': report.format.python_expression(code)}
        self.specifier = code
        super().__init__(fields=fields, **kwargs)

    def _check_usage(self, field_name, uses):
        at_least = self.fields['at_least']
        self.fields[field_name] = use_count = uses
        if at_least > use_count:
            if at_least == 1:
                return True
            else:
                self.fields['capacity'] = (f" at least {at_least} times, but"
                                           f" you used it {use_count} times")
                return True
        return False


class RejectAssertionFeedback(AssertionFeedback):
    """ Abstract base class for assertions preventing things. """
    priority = 'syntax'
    safe_field_names = ['code', 'at_most', 'capacity', 'code_message']

    def __init__(self, code, at_most=0, root=None, **kwargs):
        report = kwargs.get('report', MAIN_REPORT)
        fields = {'code': code, 'at_most': at_most, 'capacity': '',
                  'root': root, 'code_message': report.format.python_expression(code)}
        self.specifier = code
        super().__init__(fields=fields, **kwargs)

    def _check_usage(self, field_name, uses):
        at_most = self.fields['at_most']
        self.fields[field_name] = use_count = uses
        if use_count and at_most < use_count:
            if at_most == 0:
                return True
            else:
                self.fields['capacity'] = (f" more than {at_most} times, but"
                                           f" you used it {use_count} times")
                return True
        return False


class reject_code(RejectAssertionFeedback):
    """
    Determines if the string of code is present in the source.
    If so, then this becomes negative feedback warning against it.

    Note that this does NOT parse the code, so it may easily detect
    code that is present in a comment or string. If you want to check
    syntactically valid code, then use the ``prevent_`` assertions instead.

    # TODO: Make it report WHERE in the strings the text was found.

    Args:
        code (str): The snippet of code to find
        at_most (int): The maximum number of times you can find this code
            snippet.
    """
    title = "May Not Use Code"
    message_template = ("You used the code {code_message}. You may not use that code"
                        "{capacity}.")

    def condition(self):
        """ Use find_matches to check number of occurrences. """
        code = self.fields['code']
        self.fields['code_message'] = self.report.format.python_expression(code)
        uses = (get_program(self.report) or "").count(code)
        return self._check_usage('use_count', uses)


class require_code(RequireAssertionFeedback):
    """
    Determines if the string of code is missing in the source.
    If so, then this becomes negative feedback warning against it.

    Args:
        code (str): The snippet of code to find.
        at_least (int): The minimum number of times you must call this
            function. Defaults to ``1``.
    """
    title = "Must Use Code"
    message_template = "You must use the code {code_message}{capacity}."

    def condition(self):
        """ Use find_matches to check number of occurrences. """
        code = self.fields['code']
        self.fields['code_message'] = self.report.format.python_expression(code)
        uses = (get_program(self.report) or "").count(code)
        return self._check_usage('use_count', uses)


class reject_code_regex(RejectAssertionFeedback):
    """
    Determines if the regex is present in the source.
    If so, then this becomes negative feedback warning against it.
    This checks for all occurrences using `re.findall`.

    Note that this does NOT parse the code, so it may easily detect
    code that is present in a comment or string. If you want to check
    syntactically valid code, then use the ``prevent_`` assertions instead.

    # TODO: Make it report WHERE in the strings the text was found.

    Args:
        pattern (str): The regex of the pattern to find
        flags (int): The regex flags to use.
        at_most (int): The maximum number of times you can find this code
            snippet.
    """
    title = "May Not Use Pattern"
    message_template = ("You used the code {first_match_message}. You may not use that code"
                        "{capacity}.")
    safe_field_names = ['pattern', 'flags', 'at_most', 'capacity', 'code_message', 'matches',
                        'first_match', 'first_match_message']

    def __init__(self, pattern, at_most=0, flags=0, **kwargs):
        fields = {'pattern': pattern, 'at_most': at_most, 'capacity': '',
                  'pattern_message': repr(pattern), 'flags': flags}
        self.specifier = pattern
        super(AssertionFeedback, self).__init__(fields=fields, **kwargs)

    def condition(self):
        """ Use find_matches to check number of occurrences. """
        pattern = self.fields['pattern']
        flags = self.fields['flags']
        self.fields['pattern_message'] = self.report.format.python_expression(pattern)
        try:
            regex = re.compile(pattern, flags)
        except Exception as e:
            # TODO: Do something better in this case
            raise e
        source = (get_program(self.report) or "")
        matches = re.findall(regex, source)
        # TODO: Might need to convert inner tuples to lists for safe JSON
        self.fields['matches'] = matches
        uses = len(matches)
        if matches:
            first_match = matches[0]
            self.fields['first_match'] = first_match
            if isinstance(first_match, tuple):
                first_match = first_match[0]
            self.fields['first_match_message'] = self.report.format.python_expression(first_match)
        else:
            self.fields['first_match'] = None
            self.fields['first_match_message'] = ""
        return self._check_usage('use_count', uses)


class require_code_regex(RequireAssertionFeedback):
    """
    Determines if the regex is present in the source.
    If so, then this becomes negative feedback warning against it.
    This checks for all occurrences using `re.findall`.

    Note that this does NOT parse the code, so it may easily detect
    code that is present in a comment or string. If you want to check
    syntactically valid code, then use the ``prevent_`` assertions instead.

    Args:
        pattern (str): The regex of the pattern to find
        flags (int): The regex flags to use.
        at_least (int): The minimum number of times you can find this
            code snippet. Defaults to ``1``.
    """
    title = "Must Use Pattern"
    message_template = "You must use the pattern {pattern}{capacity}.{first_match_message}"

    safe_field_names = ['pattern', 'flags', 'at_least', 'capacity', 'code_message', 'matches',
                        'first_match', 'first_match_message']

    def __init__(self, pattern, at_least=1, flags=0, **kwargs):
        fields = {'pattern': pattern, 'at_least': at_least, 'capacity': '',
                  'pattern_message': repr(pattern), 'flags': flags}
        self.specifier = pattern
        super(AssertionFeedback, self).__init__(fields=fields, **kwargs)

    def condition(self):
        """ Use find_matches to check number of occurrences. """
        pattern = self.fields['pattern']
        flags = self.fields['flags']
        self.fields['pattern_message'] = self.report.format.python_expression(pattern)
        try:
            regex = re.compile(pattern, flags)
        except Exception as e:
            # TODO: Do something better in this case
            raise e
        source = (get_program(self.report) or "")
        matches = re.findall(regex, source)
        # TODO: Might need to convert inner tuples to lists for safe JSON
        self.fields['matches'] = matches
        uses = len(matches)
        if matches:
            first_match = matches[0]
            self.fields['first_match'] = first_match
            if isinstance(first_match, tuple):
                first_match = first_match[0]
            self.fields['first_match_message'] = " You did use the pattern at least once, where you wrote " + self.report.format.python_expression(first_match)
        else:
            self.fields['first_match'] = None
            self.fields['first_match_message'] = ""
        return self._check_usage('use_count', uses)


