from pedal.questions import QuestionGrader

from pedal import run, compliment, explain, gently
from pedal.report.imperative import MAIN_REPORT
from pedal.assertions.assertions import *
from pedal.toolkit.functions import *

class FunctionGrader(QuestionGrader):
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
        pass
    
    def report_success(self, question):
        question.answer()
    
    def grade_definition(self, question):
        self.student = run(report_exceptions=True, context=False)
        self.student.report_exceptions_mode=False
        
        self.definition = match_signature_muted(self.function_name, *self.signature)
        if not assertGenerally(self.definition):
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
        self.component_points = 0
        components = self._get_functions_with_filter('grade_component_')
        for component in components:
            component(question)
        self.component_points = min(self.component_points, self.MAX_COMPONENTS_POINTS)
        self.points += self.component_points
    
    def assertEqual(self, *parameters):
        return assertEqual(*parameters)
    
    def grade_unit_tests(self, question):
        all_good = True
        if self.UNIT_TEST_TOTAL_POINTS is None:
            TYPE_POINT_ADD = self.UNIT_TEST_TYPE_POINTS
            VALUE_POINT_ADD = self.UNIT_TEST_VALUE_POINTS
        else:
            ratio = self.UNIT_TEST_TYPE_RATIO
            TYPE_POINT_ADD = (self.UNIT_TEST_TOTAL_POINTS/len(self.tests) * (ratio))
            VALUE_POINT_ADD = (self.UNIT_TEST_TOTAL_POINTS/len(self.tests) * (1-ratio))
        for arguments, expected in self.tests:
            #import sys
            #print(repr(arguments), file=sys.stderr)
            result = self.student.call(self.function_name, *arguments, context=False)
            #print(repr(self.student.exception), file=sys.stderr)
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
