"""
Commands related to navigating TIFA data.
"""
import ast
from pedal.core.report import MAIN_REPORT
from pedal.tifa.constants import TOOL_NAME as TIFA_TOOL_NAME
from pedal.types.new_types import ImpossibleType, ModuleType


def tifa_analysis(code=None, report=MAIN_REPORT):
    """
    Perform the TIFA analysis and attach the results to the Report.

    Args:
        code (str or None): The code to evaluate with TIFA. If ``code`` is not
            given, then it will default to the student's main file.
        report (:class:`pedal.core.report.Report`): The Report object to
            attach results to.
    Returns:
        :py:class:`pedal.tifa.tifa_core.TifaAnalysis`: A TifaAnalysis data
            bundle containing all the information that TIFA learned.
    """
    if code is None:
        code = report.submission.main_code
    if code in report[TIFA_TOOL_NAME]['analyses']:
        return report[TIFA_TOOL_NAME]['analyses'][code]
    result = report[TIFA_TOOL_NAME]['instance'].process_code(code)
    report[TIFA_TOOL_NAME]['analyses'][code] = result
    report[TIFA_TOOL_NAME]['latest'] = result
    return result


def tifa_type_check(name: str, report=MAIN_REPORT):
    tifa_instance = report[TIFA_TOOL_NAME]['instance']
    variable = tifa_instance.find_variable_scope(name)
    return variable.state.type if variable.exists else ImpossibleType()


def get_issues(category, report=MAIN_REPORT):
    """

    Args:
        category (str or Feedback): The category of Issues to retrieve.
        report: The report to get feedback from (defaults to the MAIN_REPORT).

    Returns:
        list[Feedback]: The feedback functions triggered for this issue.
    """
    if not isinstance(category, str):
        category = category.__name__
    if not report[TIFA_TOOL_NAME]['latest']:
        tifa_analysis(report=report)
    latest = report[TIFA_TOOL_NAME]['latest']
    return latest.issues.get(category, [])


def tifa_provide_module_type(name: str, fields, report=MAIN_REPORT):
    """
    Gives TIFA the type definition for a module.

    Args:
        name: The name of the module to provide a type for.
        fields: A `ModuleType` or `dict` of fields to provide.
        report: The report to attach this feedback to (defaults to the MAIN_REPORT).

    Returns:

    """
    if not isinstance(fields, ModuleType):
        fields = ModuleType(name, fields)
    report[TIFA_TOOL_NAME]['types']['modules'][name] = fields

