"""
Test cases for the Pygame mock library.
"""
import unittest
from pedal.sandbox.library.pygame import MockPygame


class TestMockPygame(unittest.TestCase):
    """Test the MockPygame implementation"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_pygame = MockPygame()

    def test_initialization(self):
        """Test pygame initialization"""
        result = self.mock_pygame.init()
        self.assertTrue(self.mock_pygame.display_info['initialized'])
        self.assertEqual(result, (6, 0))

        self.mock_pygame.quit()
        self.assertFalse(self.mock_pygame.display_info['initialized'])

    def test_display_functions(self):
        """Test display functionality"""
        display = self.mock_pygame.display
        
        # Test set_mode
        surface = display.set_mode((800, 600))
        self.assertEqual(self.mock_pygame.display_info['width'], 800)
        self.assertEqual(self.mock_pygame.display_info['height'], 600)

        # Test caption
        display.set_caption("Test Game")
        self.assertEqual(self.mock_pygame.display_info['caption'], "Test Game")
        self.assertEqual(display.get_caption(), "Test Game")

        # Test flip
        initial_flips = self.mock_pygame.display_info['flip_count']
        display.flip()
        self.assertEqual(self.mock_pygame.display_info['flip_count'], initial_flips + 1)

    def test_drawing_functions(self):
        """Test drawing function tracking"""
        draw = self.mock_pygame.draw
        surface = self.mock_pygame.Surface((400, 300))

        # Test rectangle drawing
        draw.rect(surface, (255, 0, 0), (10, 10, 100, 50))
        
        # Test circle drawing
        draw.circle(surface, (0, 255, 0), (200, 150), 25)
        
        # Test line drawing
        draw.line(surface, (0, 0, 255), (0, 0), (100, 100))

        # Verify draw calls were tracked
        self.assertEqual(len(self.mock_pygame.draw_calls), 3)
        
        rect_call = self.mock_pygame.draw_calls[0]
        self.assertEqual(rect_call['type'], 'rect')
        self.assertEqual(rect_call['color'], (255, 0, 0))

    def test_surface_creation(self):
        """Test surface creation and manipulation"""
        surface = self.mock_pygame.Surface((200, 100))
        self.assertEqual(len(self.mock_pygame.surfaces), 1)
        
        # Test surface methods
        surface.fill((255, 255, 255))
        self.assertEqual(len(surface.data['fills']), 1)
        self.assertEqual(surface.data['fills'][0], (255, 255, 255))

        # Test blit
        other_surface = self.mock_pygame.Surface((50, 50))
        surface.blit(other_surface, (10, 10))
        self.assertEqual(len(surface.data['blits']), 1)

    def test_sound_functionality(self):
        """Test sound loading and playing"""
        mixer = self.mock_pygame.mixer
        mixer.init()
        
        # Load sound
        sound = mixer.Sound("test.wav")
        self.assertEqual(len(self.mock_pygame.sounds), 1)
        self.assertEqual(self.mock_pygame.sounds[0]['filename'], "test.wav")

        # Play sound
        sound.play()
        self.assertEqual(self.mock_pygame.sounds[0]['plays'], 1)

    def test_time_clock(self):
        """Test clock functionality"""
        time_module = self.mock_pygame.time
        clock = time_module.Clock()
        
        # Test tick
        milliseconds = clock.tick(60)
        self.assertEqual(len(self.mock_pygame.clock_ticks), 1)
        self.assertEqual(self.mock_pygame.clock_ticks[0], 60)
        self.assertEqual(milliseconds, 16)

    def test_event_handling(self):
        """Test event handling"""
        event_module = self.mock_pygame.event
        
        # Test get events
        events = event_module.get()
        self.assertEqual(events, [])
        
        # Test pump
        event_module.pump()  # Should not raise error

    def test_color_creation(self):
        """Test Color functionality"""
        Color = self.mock_pygame.Color
        
        # Test RGB color
        red = Color(255, 0, 0)
        self.assertEqual(red.r, 255)
        self.assertEqual(red.g, 0)
        self.assertEqual(red.b, 0)
        
        # Test iteration
        color_tuple = tuple(red)
        self.assertEqual(color_tuple, (255, 0, 0, 255))

    def test_rect_creation(self):
        """Test Rect functionality"""
        Rect = self.mock_pygame.Rect
        
        rect = Rect(10, 20, 100, 50)
        self.assertEqual(rect.x, 10)
        self.assertEqual(rect.y, 20)
        self.assertEqual(rect.width, 100)
        self.assertEqual(rect.height, 50)
        
        # Test center property
        self.assertEqual(rect.center, (60, 45))

    def test_image_loading(self):
        """Test image loading"""
        image_module = self.mock_pygame.image
        
        surface = image_module.load("player.png")
        self.assertEqual(len(self.mock_pygame.surfaces), 1)
        self.assertEqual(self.mock_pygame.surfaces[0]['filename'], "player.png")

    def test_patches_generation(self):
        """Test that _generate_patches returns expected functions"""
        patches = self.mock_pygame._generate_patches()
        
        # Check that key functions are included
        expected_functions = [
            'init', 'quit', 'display', 'event', 'draw', 'mixer',
            'time', 'Surface', 'Color', 'Rect'
        ]
        
        for func_name in expected_functions:
            self.assertIn(func_name, patches)


if __name__ == '__main__':
    unittest.main()