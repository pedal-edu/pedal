"""
Test the Arcade mock integration with the sandbox system.
"""
import unittest
from textwrap import dedent
from tests.execution_helper import Execution, ExecutionTestCase, SUCCESS_MESSAGE


# Sample arcade code that might be used in educational settings
sample_arcade_code = dedent('''
import arcade

# Open window
arcade.open_window(800, 600, "My Game")
arcade.set_background_color(arcade.color.WHITE)

# Start rendering
arcade.start_render()

# Draw some shapes
arcade.draw_circle_filled(100, 100, 50, arcade.color.RED)
arcade.draw_rectangle_filled(200, 200, 100, 80, arcade.color.BLUE)
arcade.draw_text("Score: 100", 10, 580, arcade.color.BLACK, 16)

# Finish rendering
arcade.finish_render()

# Create a sprite
player = arcade.Sprite("player.png", 0.5)
player.center_x = 400
player.center_y = 300

# Create sprite list
sprite_list = arcade.SpriteList()
sprite_list.append(player)

# Load and play sound
coin_sound = arcade.load_sound("coin.wav")
arcade.play_sound(coin_sound)
''').strip()


class TestArcadeIntegration(ExecutionTestCase):
    """Test Arcade mock integration with pedal sandbox"""

    def test_arcade_basic_execution(self):
        """Test that basic arcade code executes without errors"""
        with Execution(sample_arcade_code) as e:
            # Should execute without error
            pass
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_arcade_mock_captures_data(self):
        """Test that the arcade mock captures drawing and game data"""
        with Execution(sample_arcade_code) as e:
            student = e.student
            # Access the mocked arcade module
            arcade_mock = student.modules.arcade
            
            # Check window creation
            self.assertTrue(arcade_mock.window['open'])
            self.assertEqual(arcade_mock.window['width'], 800)
            self.assertEqual(arcade_mock.window['height'], 600)
            self.assertEqual(arcade_mock.window['title'], "My Game")
            
            # Check drawing commands were captured
            self.assertGreater(len(arcade_mock.draw_commands), 0)
            
            # Check specific draw commands
            draw_types = [cmd['type'] for cmd in arcade_mock.draw_commands]
            self.assertIn('start_render', draw_types)
            self.assertIn('circle_filled', draw_types)
            self.assertIn('rectangle_filled', draw_types)
            self.assertIn('text', draw_types)
            self.assertIn('finish_render', draw_types)
            
            # Check sprites were created
            self.assertEqual(len(arcade_mock.sprites), 1)
            
            # Check sounds were loaded and played
            self.assertEqual(len(arcade_mock.sounds), 2)  # load_sound + play_sound
            
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_arcade_sprite_interaction(self):
        """Test sprite creation and manipulation"""
        sprite_code = dedent('''
        import arcade
        
        # Create sprite
        player = arcade.Sprite("player.png")
        player.center_x = 100
        player.center_y = 200
        player.change_x = 5
        player.change_y = -3
        
        # Update sprite position
        player.update()
        
        # Check final position
        final_x = player.center_x
        final_y = player.center_y
        
        # Use the variables to avoid unused variable warnings
        print(final_x, final_y)
        ''').strip()
        
        with Execution(sprite_code) as e:
            student = e.student
            arcade_mock = student.modules.arcade
            
            # Verify sprite was created and updated correctly
            self.assertEqual(len(arcade_mock.sprites), 1)
            sprite_data = arcade_mock.sprites[0]
            self.assertEqual(sprite_data['center_x'], 105)  # 100 + 5
            self.assertEqual(sprite_data['center_y'], 197)  # 200 + (-3)
            
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_arcade_collision_detection(self):
        """Test collision detection functionality"""
        collision_code = dedent('''
        import arcade
        
        sprite1 = arcade.Sprite("sprite1.png")
        sprite2 = arcade.Sprite("sprite2.png")
        sprite_list = arcade.SpriteList()
        
        # Test collision functions
        collision = arcade.check_for_collision(sprite1, sprite2)
        collisions = arcade.check_for_collision_with_list(sprite1, sprite_list)
        sprites_at_point = arcade.get_sprites_at_point((100, 100), sprite_list)
        
        # Use the variables to avoid unused variable warnings
        print(collision, len(collisions), len(sprites_at_point))
        ''').strip()
        
        with Execution(collision_code) as e:
            # Should execute without error
            pass
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_arcade_physics_engine(self):
        """Test physics engine creation"""
        physics_code = dedent('''
        import arcade
        
        player = arcade.Sprite("player.png")
        walls = arcade.SpriteList()
        
        physics_engine = arcade.PhysicsEngineSimple(player, walls)
        physics_engine.update()
        ''').strip()
        
        with Execution(physics_code) as e:
            student = e.student
            arcade_mock = student.modules.arcade
            
            # Verify physics engine was created
            self.assertEqual(len(arcade_mock.physics_engines), 1)
            self.assertEqual(arcade_mock.physics_engines[0]['type'], 'physics_simple')
            
        self.assertFeedback(e, SUCCESS_MESSAGE)

    def test_arcade_color_constants(self):
        """Test color constant access"""
        color_code = dedent('''
        import arcade
        
        white = arcade.color.WHITE
        red = arcade.color.RED
        blue = arcade.color.BLUE
        
        # Use the colors to avoid unused variable warnings
        print(white, red, blue)
        ''').strip()
        
        with Execution(color_code) as e:
            # Should execute without error
            pass
        self.assertFeedback(e, SUCCESS_MESSAGE)


if __name__ == '__main__':
    unittest.main()