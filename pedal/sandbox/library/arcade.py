from pedal.sandbox.mocked import MockModule


class MockArcade(MockModule):
    """
    Mock Arcade library that can be used to capture game development data.
    
    Arcade is a modern Python library for creating 2D games, designed to be
    more beginner-friendly and Pythonic than Pygame. This mock captures
    common game development patterns for educational purposes.

    Attributes:
        window (dict): Information about the game window
        sprites (list): List of sprites created
        sounds (list): List of sounds played
        scenes (list): List of scenes created
        draw_commands (list): List of drawing commands executed
        physics_engines (list): List of physics engines created
    """

    def __init__(self):
        super().__init__()
        self._reset_game_state()

    def _reset_game_state(self):
        """Reset all game state tracking"""
        self.window = {
            'width': 800,
            'height': 600,
            'title': 'Arcade Window',
            'background_color': (255, 255, 255),
            'open': False
        }
        self.sprites = []
        self.sounds = []
        self.scenes = []
        self.draw_commands = []
        self.physics_engines = []
        self.textures = []
        self.current_view = None
        self.delta_time = 1/60  # Default 60 FPS

    # Window Management
    def open_window(self, width, height, title, resizable=False, **kwargs):
        """Open a game window"""
        self.window.update({
            'width': width,
            'height': height,
            'title': title,
            'resizable': resizable,
            'open': True,
            'kwargs': kwargs
        })

    def set_background_color(self, color):
        """Set the background color"""
        self.window['background_color'] = color

    def close_window(self):
        """Close the game window"""
        self.window['open'] = False

    # Drawing Functions
    def start_render(self):
        """Start the rendering process"""
        self.draw_commands.append({'type': 'start_render'})

    def finish_render(self):
        """Finish the rendering process"""
        self.draw_commands.append({'type': 'finish_render'})

    def draw_circle_filled(self, center_x, center_y, radius, color):
        """Draw a filled circle"""
        self.draw_commands.append({
            'type': 'circle_filled',
            'center_x': center_x,
            'center_y': center_y,
            'radius': radius,
            'color': color
        })

    def draw_circle_outline(self, center_x, center_y, radius, color, border_width=1):
        """Draw a circle outline"""
        self.draw_commands.append({
            'type': 'circle_outline',
            'center_x': center_x,
            'center_y': center_y,
            'radius': radius,
            'color': color,
            'border_width': border_width
        })

    def draw_rectangle_filled(self, center_x, center_y, width, height, color, tilt_angle=0):
        """Draw a filled rectangle"""
        self.draw_commands.append({
            'type': 'rectangle_filled',
            'center_x': center_x,
            'center_y': center_y,
            'width': width,
            'height': height,
            'color': color,
            'tilt_angle': tilt_angle
        })

    def draw_rectangle_outline(self, center_x, center_y, width, height, color, border_width=1, tilt_angle=0):
        """Draw a rectangle outline"""
        self.draw_commands.append({
            'type': 'rectangle_outline',
            'center_x': center_x,
            'center_y': center_y,
            'width': width,
            'height': height,
            'color': color,
            'border_width': border_width,
            'tilt_angle': tilt_angle
        })

    def draw_line(self, start_x, start_y, end_x, end_y, color, line_width=1):
        """Draw a line"""
        self.draw_commands.append({
            'type': 'line',
            'start_x': start_x,
            'start_y': start_y,
            'end_x': end_x,
            'end_y': end_y,
            'color': color,
            'line_width': line_width
        })

    def draw_text(self, text, start_x, start_y, color, font_size=12, **kwargs):
        """Draw text"""
        self.draw_commands.append({
            'type': 'text',
            'text': text,
            'start_x': start_x,
            'start_y': start_y,
            'color': color,
            'font_size': font_size,
            'kwargs': kwargs
        })

    # Sprite Management
    def Sprite(self, filename=None, scale=1.0, **kwargs):
        """Create a sprite mock"""
        sprite_data = {
            'type': 'sprite',
            'filename': filename,
            'scale': scale,
            'center_x': 0,
            'center_y': 0,
            'change_x': 0,
            'change_y': 0,
            'angle': 0,
            'kwargs': kwargs
        }
        self.sprites.append(sprite_data)
        return MockSprite(sprite_data)

    def SpriteList(self, **kwargs):
        """Create a sprite list mock"""
        sprite_list_data = {
            'type': 'sprite_list',
            'sprites': [],
            'kwargs': kwargs
        }
        return MockSpriteList(sprite_list_data)

    # Physics
    def PhysicsEngineSimple(self, player_sprite, walls, **kwargs):
        """Create a simple physics engine mock"""
        physics_data = {
            'type': 'physics_simple',
            'player_sprite': player_sprite,
            'walls': walls,
            'kwargs': kwargs
        }
        self.physics_engines.append(physics_data)
        return MockPhysicsEngine(physics_data)

    # Sound
    def load_sound(self, filename):
        """Load a sound file"""
        sound_data = {
            'type': 'load_sound',
            'filename': filename
        }
        self.sounds.append(sound_data)
        return MockSound(sound_data)

    def play_sound(self, sound, **kwargs):
        """Play a sound"""
        self.sounds.append({
            'type': 'play_sound',
            'sound': sound,
            'kwargs': kwargs
        })

    # Game Loop and Events
    def run(self):
        """Run the game loop"""
        self.draw_commands.append({'type': 'run_game'})

    def schedule(self, function, interval):
        """Schedule a function to run at intervals"""
        self.draw_commands.append({
            'type': 'schedule',
            'function': function.__name__ if hasattr(function, '__name__') else str(function),
            'interval': interval
        })

    # Utility Functions
    def check_for_collision(self, sprite1, sprite2):
        """Check if two sprites collide"""
        return False  # Mock collision detection

    def check_for_collision_with_list(self, sprite, sprite_list):
        """Check collision between sprite and sprite list"""
        return []  # Mock collision detection

    def get_sprites_at_point(self, point, sprite_list):
        """Get sprites at a specific point"""
        return []  # Mock point detection

    # Color constants (common colors used in educational projects)
    @property 
    def color(self):
        """Mock color module"""
        return MockColor()

    def _generate_patches(self):
        """Generate patches for the arcade module"""
        return {
            'open_window': self.open_window,
            'set_background_color': self.set_background_color,
            'close_window': self.close_window,
            'start_render': self.start_render,
            'finish_render': self.finish_render,
            'draw_circle_filled': self.draw_circle_filled,
            'draw_circle_outline': self.draw_circle_outline,
            'draw_rectangle_filled': self.draw_rectangle_filled,
            'draw_rectangle_outline': self.draw_rectangle_outline,
            'draw_line': self.draw_line,
            'draw_text': self.draw_text,
            'Sprite': self.Sprite,
            'SpriteList': self.SpriteList,
            'PhysicsEngineSimple': self.PhysicsEngineSimple,
            'load_sound': self.load_sound,
            'play_sound': self.play_sound,
            'run': self.run,
            'schedule': self.schedule,
            'check_for_collision': self.check_for_collision,
            'check_for_collision_with_list': self.check_for_collision_with_list,
            'get_sprites_at_point': self.get_sprites_at_point,
            'color': self.color,
        }


class MockSprite:
    """Mock arcade sprite"""
    def __init__(self, data):
        self.data = data
        
    @property
    def center_x(self):
        return self.data['center_x']
    
    @center_x.setter
    def center_x(self, value):
        self.data['center_x'] = value
        
    @property
    def center_y(self):
        return self.data['center_y']
    
    @center_y.setter
    def center_y(self, value):
        self.data['center_y'] = value
        
    @property
    def change_x(self):
        return self.data['change_x']
    
    @change_x.setter
    def change_x(self, value):
        self.data['change_x'] = value
        
    @property
    def change_y(self):
        return self.data['change_y']
    
    @change_y.setter
    def change_y(self, value):
        self.data['change_y'] = value

    def update(self):
        """Update sprite position"""
        self.data['center_x'] += self.data['change_x']
        self.data['center_y'] += self.data['change_y']


class MockSpriteList:
    """Mock arcade sprite list"""
    def __init__(self, data):
        self.data = data
        
    def append(self, sprite):
        """Add sprite to list"""
        self.data['sprites'].append(sprite)
        
    def update(self):
        """Update all sprites in list"""
        for sprite in self.data['sprites']:
            if hasattr(sprite, 'update'):
                sprite.update()
                
    def draw(self):
        """Draw all sprites in list"""
        pass  # Mock drawing


class MockPhysicsEngine:
    """Mock arcade physics engine"""
    def __init__(self, data):
        self.data = data
        
    def update(self):
        """Update physics"""
        pass  # Mock physics update


class MockSound:
    """Mock arcade sound"""
    def __init__(self, data):
        self.data = data
        
    def play(self, **kwargs):
        """Play the sound"""
        pass  # Mock sound playback


class MockColor:
    """Mock arcade color constants"""
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    PURPLE = (255, 0, 255)
    CYAN = (0, 255, 255)
    ORANGE = (255, 165, 0)
    GRAY = (128, 128, 128)