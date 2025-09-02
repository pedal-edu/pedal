"""
Test cases for the Arcade mock library.
"""
import unittest
from pedal.sandbox.library.arcade import MockArcade


class TestMockArcade(unittest.TestCase):
    """Test the MockArcade implementation"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_arcade = MockArcade()

    def test_window_management(self):
        """Test window creation and management"""
        # Test opening window
        self.mock_arcade.open_window(800, 600, "Test Window")
        self.assertTrue(self.mock_arcade.window['open'])
        self.assertEqual(self.mock_arcade.window['width'], 800)
        self.assertEqual(self.mock_arcade.window['height'], 600)
        self.assertEqual(self.mock_arcade.window['title'], "Test Window")

        # Test background color
        self.mock_arcade.set_background_color((255, 0, 0))
        self.assertEqual(self.mock_arcade.window['background_color'], (255, 0, 0))

        # Test closing window
        self.mock_arcade.close_window()
        self.assertFalse(self.mock_arcade.window['open'])

    def test_drawing_functions(self):
        """Test drawing function tracking"""
        # Test circle drawing
        self.mock_arcade.draw_circle_filled(100, 100, 50, (255, 0, 0))
        self.mock_arcade.draw_circle_outline(200, 200, 30, (0, 255, 0), 2)

        # Test rectangle drawing
        self.mock_arcade.draw_rectangle_filled(150, 150, 100, 80, (0, 0, 255))
        self.mock_arcade.draw_rectangle_outline(250, 250, 120, 90, (255, 255, 0), 3)

        # Test line drawing
        self.mock_arcade.draw_line(0, 0, 100, 100, (255, 255, 255), 2)

        # Test text drawing
        self.mock_arcade.draw_text("Hello World", 50, 50, (0, 0, 0), 16)

        # Verify commands were tracked
        self.assertEqual(len(self.mock_arcade.draw_commands), 6)
        
        # Check specific draw command
        circle_cmd = self.mock_arcade.draw_commands[0]
        self.assertEqual(circle_cmd['type'], 'circle_filled')
        self.assertEqual(circle_cmd['center_x'], 100)
        self.assertEqual(circle_cmd['center_y'], 100)
        self.assertEqual(circle_cmd['radius'], 50)
        self.assertEqual(circle_cmd['color'], (255, 0, 0))

    def test_sprite_creation(self):
        """Test sprite creation and management"""
        # Create sprite
        sprite = self.mock_arcade.Sprite("player.png", 0.5)
        self.assertEqual(len(self.mock_arcade.sprites), 1)
        
        # Test sprite properties
        sprite.center_x = 100
        sprite.center_y = 200
        sprite.change_x = 5
        sprite.change_y = -3
        
        self.assertEqual(sprite.center_x, 100)
        self.assertEqual(sprite.center_y, 200)
        self.assertEqual(sprite.change_x, 5)
        self.assertEqual(sprite.change_y, -3)

        # Test sprite update
        sprite.update()
        self.assertEqual(sprite.center_x, 105)  # 100 + 5
        self.assertEqual(sprite.center_y, 197)  # 200 + (-3)

    def test_sprite_list(self):
        """Test sprite list functionality"""
        sprite_list = self.mock_arcade.SpriteList()
        
        # Create and add sprites
        sprite1 = self.mock_arcade.Sprite("sprite1.png")
        sprite2 = self.mock_arcade.Sprite("sprite2.png")
        
        sprite_list.append(sprite1)
        sprite_list.append(sprite2)
        
        self.assertEqual(len(sprite_list.data['sprites']), 2)

    def test_physics_engine(self):
        """Test physics engine creation"""
        player = self.mock_arcade.Sprite("player.png")
        walls = self.mock_arcade.SpriteList()
        
        physics_engine = self.mock_arcade.PhysicsEngineSimple(player, walls)
        
        self.assertEqual(len(self.mock_arcade.physics_engines), 1)
        self.assertEqual(self.mock_arcade.physics_engines[0]['type'], 'physics_simple')

    def test_sound_functionality(self):
        """Test sound loading and playing"""
        # Load sound
        sound = self.mock_arcade.load_sound("coin.wav")
        self.assertEqual(len(self.mock_arcade.sounds), 1)
        self.assertEqual(self.mock_arcade.sounds[0]['type'], 'load_sound')
        self.assertEqual(self.mock_arcade.sounds[0]['filename'], "coin.wav")

        # Play sound
        self.mock_arcade.play_sound(sound, volume=0.5)
        self.assertEqual(len(self.mock_arcade.sounds), 2)
        self.assertEqual(self.mock_arcade.sounds[1]['type'], 'play_sound')

    def test_game_loop_functions(self):
        """Test game loop and scheduling"""
        def dummy_function():
            pass

        # Test run
        self.mock_arcade.run()
        self.assertEqual(self.mock_arcade.draw_commands[-1]['type'], 'run_game')

        # Test schedule
        self.mock_arcade.schedule(dummy_function, 1/60)
        schedule_cmd = self.mock_arcade.draw_commands[-1]
        self.assertEqual(schedule_cmd['type'], 'schedule')
        self.assertEqual(schedule_cmd['function'], 'dummy_function')
        self.assertEqual(schedule_cmd['interval'], 1/60)

    def test_collision_detection(self):
        """Test collision detection functions"""
        sprite1 = self.mock_arcade.Sprite("sprite1.png")
        sprite2 = self.mock_arcade.Sprite("sprite2.png")
        sprite_list = self.mock_arcade.SpriteList()

        # Test collision between sprites (mock returns False)
        collision = self.mock_arcade.check_for_collision(sprite1, sprite2)
        self.assertFalse(collision)

        # Test collision with list (mock returns empty list)
        collisions = self.mock_arcade.check_for_collision_with_list(sprite1, sprite_list)
        self.assertEqual(collisions, [])

        # Test sprites at point (mock returns empty list)
        sprites_at_point = self.mock_arcade.get_sprites_at_point((100, 100), sprite_list)
        self.assertEqual(sprites_at_point, [])

    def test_color_constants(self):
        """Test color constant access"""
        color_module = self.mock_arcade.color
        self.assertEqual(color_module.WHITE, (255, 255, 255))
        self.assertEqual(color_module.BLACK, (0, 0, 0))
        self.assertEqual(color_module.RED, (255, 0, 0))
        self.assertEqual(color_module.GREEN, (0, 255, 0))
        self.assertEqual(color_module.BLUE, (0, 0, 255))

    def test_render_cycle(self):
        """Test complete render cycle tracking"""
        self.mock_arcade.start_render()
        self.mock_arcade.draw_circle_filled(100, 100, 50, (255, 0, 0))
        self.mock_arcade.draw_text("Score: 100", 10, 10, (0, 0, 0))
        self.mock_arcade.finish_render()

        # Check that all commands were tracked
        commands = self.mock_arcade.draw_commands
        self.assertEqual(len(commands), 4)
        self.assertEqual(commands[0]['type'], 'start_render')
        self.assertEqual(commands[1]['type'], 'circle_filled')
        self.assertEqual(commands[2]['type'], 'text')
        self.assertEqual(commands[3]['type'], 'finish_render')

    def test_patches_generation(self):
        """Test that _generate_patches returns expected functions"""
        patches = self.mock_arcade._generate_patches()
        
        # Check that key functions are included
        expected_functions = [
            'open_window', 'draw_circle_filled', 'Sprite', 'SpriteList',
            'load_sound', 'run', 'check_for_collision', 'color'
        ]
        
        for func_name in expected_functions:
            self.assertIn(func_name, patches)


if __name__ == '__main__':
    unittest.main()