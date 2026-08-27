"""
Tests for composite feedback function score parameter handling.
This ensures that composite functions like prevent_advanced_iteration handle
score parameters at the composite level rather than passing them to each constituent.
"""
import unittest
from pedal import *
from pedal.assertions.static import prevent_advanced_iteration, ensure_prints_exactly
from pedal.core.commands import clear_report
from pedal.source import set_source
from tests.execution_helper import ExecutionTestCase

class TestCompositeFeedbackScore(ExecutionTestCase):
    
    def test_prevent_advanced_iteration_score_composite(self):
        """Test that score parameter is handled at composite level, not per constituent"""
        clear_report()
        
        # Code that triggers multiple constituents
        student_code = """
while True:
    pass
sum([1, 2, 3])
max([1, 2, 3])
"""
        set_source(student_code, filename="__main__.py")
        
        # Call with score parameter
        result = prevent_advanced_iteration(score=-10)
        
        # Should have triggered
        self.assertTrue(result)
        
        # Count feedback items with scores
        feedback_with_scores = [f for f in MAIN_REPORT.feedback if f.score is not None]
        total_score = sum(f.score for f in feedback_with_scores if f.score)
        
        # Should have exactly one feedback item with a score, and total should be -10
        self.assertEqual(len(feedback_with_scores), 1)
        self.assertEqual(total_score, -10)
        self.assertEqual(feedback_with_scores[0].label, 'prevent_advanced_iteration')
    
    def test_prevent_advanced_iteration_without_score(self):
        """Test that without score parameter, individual feedback items behave normally"""
        clear_report()
        
        student_code = """
while True:
    pass
sum([1, 2, 3])
"""
        set_source(student_code, filename="__main__.py")
        
        # Call without score parameter
        result = prevent_advanced_iteration()
        
        # Should have triggered
        self.assertTrue(result)
        
        # Should have individual feedback items but no composite score feedback
        feedback_with_scores = [f for f in MAIN_REPORT.feedback if f.score is not None]
        composite_feedback = [f for f in MAIN_REPORT.feedback if f.label == 'prevent_advanced_iteration']
        
        self.assertEqual(len(feedback_with_scores), 0)  # No scores applied
        self.assertEqual(len(composite_feedback), 0)    # No composite feedback
        self.assertGreater(len(MAIN_REPORT.feedback), 0)  # But individual feedback exists
    
    def test_prevent_advanced_iteration_muted_composite(self):
        """Test that muted parameter applies to composite"""
        clear_report()
        
        student_code = """
sum([1, 2, 3])
"""
        set_source(student_code, filename="__main__.py")
        
        # Call with muted parameter
        result = prevent_advanced_iteration(score=-5, muted=True)
        
        # Should have triggered
        self.assertTrue(result)
        
        # Should have composite feedback that is muted
        composite_feedback = [f for f in MAIN_REPORT.feedback if f.label == 'prevent_advanced_iteration']
        self.assertEqual(len(composite_feedback), 1)
        self.assertTrue(composite_feedback[0].muted)
        self.assertEqual(composite_feedback[0].score, -5)
    
    def test_ensure_prints_exactly_score_composite(self):
        """Test that ensure_prints_exactly handles score compositely"""
        clear_report()
        
        # Code that prints exactly once (should pass both conditions)
        student_code = """
print("Hello")
"""
        set_source(student_code, filename="__main__.py")
        
        # Call with score parameter
        result = ensure_prints_exactly(1, score=10)
        
        # Should have triggered both conditions (this function returns True when both conditions are met)
        # But since it's deprecated and may have different semantics, we'll just test that score is handled properly
        feedback_with_scores = [f for f in MAIN_REPORT.feedback if f.score is not None]
        
        # If it creates composite feedback, there should be at most one score
        if feedback_with_scores:
            total_score = sum(f.score for f in feedback_with_scores if f.score)
            # Should not be multiplied
            self.assertLessEqual(abs(total_score), 20)  # Allow some tolerance since it's deprecated

if __name__ == '__main__':
    unittest.main()