from pedal.core.commands import compliment, explain, gently
from pedal.core.report import MAIN_REPORT
from pedal.sandbox.commands import run
from pedal.assertions.runtime import *
from pedal.assertions.static import ensure_function


class QuestionGrader:
    def _get_functions_with_filter(self, filter='grade_'):
        return [getattr(self, method_name) for method_name in dir(self)
                if method_name.startswith(filter) and
                callable(getattr(self, method_name))]

    def _test(self, question):
        methods = self._get_functions_with_filter()
        for method in methods:
            method(question)


class FunctionGrader(QuestionGrader):
    """

    """
    MAX_POINTS = 10
    DEFINITION_POINTS = 3
    COMPONENTS_POINTS = 1
    MAX_COMPONENTS_POINTS = 2
    UNIT_TEST_TYPE_POINTS = None
    UNIT_TEST_VALUE_POINTS = None
    UNIT_TEST_TOTAL_POINTS = 5
    UNIT_TEST_TYPE_RATIO = .5
    UNIT_TEST_COMPLETION_POINTS = 2

    def __init__(self, function_name, signature, tests):
        super().__init__()
        self.function_name = function_name
        self.signature = signature
        self.tests = tests
        self.points = 0

    def _test(self, question):
        defined = self.grade_definition(question)

        if not defined:
            return self.report_status(question)

        self.grade_components(question)

        passed_tests = self.grade_unit_tests(question)
        if not passed_tests:
            return self.report_status(question)

        self.report_success(question)

    def report_status(self, question):
        """

        Args:
            question:
        """
        pass

    def report_success(self, question):
        """

        Args:
            question:
        """
        question.answer()

    def grade_definition(self, question):
        """

        Args:
            question:

        Returns:

        """
        self.student = run()

        if not ensure_function(self.function_name, *self.signature):
            gently("Function not defined")
            return False

        if self.student.exception:
            return False
        if not assertHasFunction(self.student, self.function_name):
            gently("Function defined incorrectly")
            return False

        self.points += self.DEFINITION_POINTS
        return True

    def grade_components(self, question):
        """

        Args:
            question:
        """
        self.component_points = 0
        components = self._get_functions_with_filter('grade_component_')
        for component in components:
            component(question)
        self.component_points = min(self.component_points, self.MAX_COMPONENTS_POINTS)
        self.points += self.component_points

    def assertEqual(self, *parameters):
        """

        Args:
            *parameters:

        Returns:

        """
        return assertEqual(*parameters)

    def grade_unit_tests(self, question):
        """

        Args:
            question:

        Returns:

        """
        all_good = True
        if self.UNIT_TEST_TOTAL_POINTS is None:
            TYPE_POINT_ADD = self.UNIT_TEST_TYPE_POINTS
            VALUE_POINT_ADD = self.UNIT_TEST_VALUE_POINTS
        else:
            ratio = self.UNIT_TEST_TYPE_RATIO
            TYPE_POINT_ADD = (self.UNIT_TEST_TOTAL_POINTS / len(self.tests) * (ratio))
            VALUE_POINT_ADD = (self.UNIT_TEST_TOTAL_POINTS / len(self.tests) * (1 - ratio))
        for arguments, expected in self.tests:
            # import sys
            # print(repr(arguments), file=sys.stderr)
            result = self.student.call(self.function_name, *arguments, context=False)
            # print(repr(self.student.exception), file=sys.stderr)
            if self.student.exception:
                all_good = False
                continue
            if assertIsInstance(result, type(expected)):
                self.points += TYPE_POINT_ADD
            else:
                all_good = False
                continue
            if self.assertEqual(result, expected):
                self.points += VALUE_POINT_ADD
            else:
                all_good = False
        if all_good:
            self.points += self.UNIT_TEST_COMPLETION_POINTS
        else:
            gently("Failing instructor unit tests")
        return all_good
