from pedal.core.commands import compliment, explain, gently, give_partial, suppress
from pedal.core.feedback_category import FeedbackCategory
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
        return [method(question) for method in methods]


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

    def __init__(self, function_name, signature, tests, config=None):
        super().__init__()
        self.function_name = function_name
        self.signature = signature
        self.tests = tests
        self.points = 0
        self.config = config or {}
        self.config.setdefault('suppress_function_unused', True)
        self.justification_parts = []

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
        self.justification_parts.append(f"Total: {self.points:.2f}/{self.MAX_POINTS} (+{round(self.points/self.MAX_POINTS * 100)}%)")
        give_partial(self.points/self.MAX_POINTS,
                     title="Function Grader Partial Credit",
                     message="Partial credit from function grader",
                     justification="\n".join(self.justification_parts))

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

        if ensure_function(self.function_name, *self.signature):
            gently("Function not defined")
            return False

        if self.student.exception:
            return False
        if assertHasFunction(self.student, self.function_name):
            gently("Function defined incorrectly")
            return False

        if self.config.get('suppress_function_unused', True):
            suppress(FeedbackCategory.ALGORITHMIC, 'unused_variable', {'name': self.function_name})

        self.points += self.DEFINITION_POINTS
        self.justification_parts.append(f"Function {self.function_name} defined with signature: {self.DEFINITION_POINTS}")
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
        if self.component_points:
            self.justification_parts.append(f"Components: {self.component_points}")

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
            TYPE_POINT_ADD = (self.UNIT_TEST_TOTAL_POINTS / len(self.tests) * ratio)
            VALUE_POINT_ADD = (self.UNIT_TEST_TOTAL_POINTS / len(self.tests) * (1 - ratio))
        test_points = 0
        for index, (arguments, expected) in enumerate(self.tests):
            # import sys
            # print(repr(arguments), file=sys.stderr)
            result = self.student.call(self.function_name, *arguments)
            # print(repr(self.student.exception), file=sys.stderr)
            if self.student.exception:
                all_good = False
                self.justification_parts.append(f"  Test {index}: error occurred")
                continue
            if not assertIsInstance(result, type(expected)):
                self.points += TYPE_POINT_ADD
                test_points += TYPE_POINT_ADD
            else:
                all_good = False
                self.justification_parts.append(f"  Test {index}: wrong return type")
                continue
            if not self.assertEqual(result, expected):
                self.points += VALUE_POINT_ADD
                test_points += VALUE_POINT_ADD
                self.justification_parts.append(f"  Test {index}: correct ({VALUE_POINT_ADD})")
            else:
                all_good = False
                self.justification_parts.append(f"  Test {index}: wrong return value, but correct type ({TYPE_POINT_ADD})")
        if all_good:
            self.points += self.UNIT_TEST_COMPLETION_POINTS
            self.justification_parts.append(f"All tests passed: {self.UNIT_TEST_COMPLETION_POINTS}")
        else:
            gently("Failing instructor unit tests")
            self.justification_parts.append(f"Some tests failed: {test_points}")
        return all_good
