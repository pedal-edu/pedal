"""
Test the Pygame mock integration with the sandbox system.
"""
import unittest
from textwrap import dedent
from tests.execution_helper import Execution, ExecutionTestCase, SUCCESS_MESSAGE


# Sample pygame code that might be used in educational settings  
sample_pygame_code = dedent('''
import pygame

# Initialize pygame
pygame.init()

# Set up display
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("My Pygame Game")

# Create clock
clock = pygame.time.Clock()

# Fill screen with white
screen.fill((255, 255, 255))

# Draw some shapes
pygame.draw.rect(screen, (255, 0, 0), (100, 100, 200, 150))
pygame.draw.circle(screen, (0, 255, 0), (400, 300), 50)
pygame.draw.line(screen, (0, 0, 255), (0, 0), (100, 100), 5)

# Update display
pygame.display.flip()

# Load and play sound
sound = pygame.mixer.Sound("coin.wav")
sound.play()

# Tick clock
clock.tick(60)

# Get events
events = pygame.event.get()
keys = pygame.key.get_pressed()

# Use variables to avoid unused warnings
print(len(events), len(keys))

# Don't call pygame.quit() so we can inspect the state
''').strip()


class TestPygameIntegration(ExecutionTestCase):
    """Test Pygame mock integration with pedal sandbox"""

    def test_pygame_basic_execution(self):
        """Test that basic pygame code executes without errors"""
        with Execution(sample_pygame_code) as e:
            # Should execute without error
            pass
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_pygame_mock_captures_data(self):
        """Test that the pygame mock captures game data"""
        with Execution(sample_pygame_code) as e:
            student = e.student
            # Access the mocked pygame module
            pygame_mock = student.modules.pygame
            
            # Check initialization
            self.assertTrue(pygame_mock.display_info['initialized'])
            
            # Check display setup
            self.assertEqual(pygame_mock.display_info['width'], 800)
            self.assertEqual(pygame_mock.display_info['height'], 600)
            self.assertEqual(pygame_mock.display_info['caption'], "My Pygame Game")
            
            # Check drawing commands were captured
            self.assertGreater(len(pygame_mock.draw_calls), 0)
            self.assertEqual(len(pygame_mock.draw_calls), 3)  # rect, circle, line
            
            # Check surfaces were created
            self.assertGreater(len(pygame_mock.surfaces), 0)
            
            # Check sounds were loaded
            self.assertEqual(len(pygame_mock.sounds), 1)
            self.assertEqual(pygame_mock.sounds[0]['filename'], "coin.wav")
            self.assertEqual(pygame_mock.sounds[0]['plays'], 1)
            
            # Check clock ticks
            self.assertEqual(len(pygame_mock.clock_ticks), 1)
            self.assertEqual(pygame_mock.clock_ticks[0], 60)
            
        self.assertFeedback(e, SUCCESS_MESSAGE)


if __name__ == '__main__':
    unittest.main()