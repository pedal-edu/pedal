from pedal.sandbox.mocked import MockModule


class MockPygame(MockModule):
    """
    Mock Pygame library that can be used to capture game development data.
    
    Pygame is the classic Python library for creating 2D games. This mock captures
    common game development patterns for educational purposes, focusing on the
    most commonly used pygame functions in educational settings.

    Attributes:
        display_info (dict): Information about the pygame display
        events (list): List of events created
        surfaces (list): List of surfaces created
        sounds (list): List of sounds loaded/played
        draw_calls (list): List of drawing operations
        clock_ticks (list): List of clock tick operations
    """

    def __init__(self):
        super().__init__()
        self._reset_pygame_state()

    def _reset_pygame_state(self):
        """Reset all pygame state tracking"""
        self.display_info = {
            'initialized': False,
            'width': 0,
            'height': 0,
            'caption': '',
            'flip_count': 0
        }
        self.events = []
        self.surfaces = []
        self.sounds = []
        self.draw_calls = []
        self.clock_ticks = []
        self.keys_pressed = {}

    # Core pygame functions
    def init(self):
        """Initialize pygame"""
        self.display_info['initialized'] = True
        return (6, 0)  # Mock return: (successful, failed)

    def quit(self):
        """Quit pygame"""
        self.display_info['initialized'] = False

    # Display module
    @property
    def display(self):
        """Mock display module"""
        return MockPygameDisplay(self)

    # Event module  
    @property
    def event(self):
        """Mock event module"""
        return MockPygameEvent(self)

    # Draw module
    @property
    def draw(self):
        """Mock draw module"""
        return MockPygameDraw(self)

    # Mixer module (sound)
    @property
    def mixer(self):
        """Mock mixer module"""
        return MockPygameMixer(self)

    # Time module
    @property
    def time(self):
        """Mock time module"""
        return MockPygameTime(self)

    # Key module
    @property
    def key(self):
        """Mock key module"""
        return MockPygameKey(self)

    # Mouse module
    @property
    def mouse(self):
        """Mock mouse module"""
        return MockPygameMouse(self)

    # Image module
    @property
    def image(self):
        """Mock image module"""
        return MockPygameImage(self)

    # Transform module
    @property
    def transform(self):
        """Mock transform module"""
        return MockPygameTransform(self)

    # Surface creation
    def Surface(self, size, flags=0, depth=0):
        """Create a surface mock"""
        surface_data = {
            'type': 'surface',
            'size': size,
            'flags': flags,
            'depth': depth,
            'fills': [],
            'blits': []
        }
        self.surfaces.append(surface_data)
        return MockSurface(surface_data)

    # Color constants
    @property
    def Color(self):
        """Mock Color class"""
        return MockColor

    # Rectangle
    @property
    def Rect(self):
        """Mock Rect class"""
        return MockRect

    def _generate_patches(self):
        """Generate patches for the pygame module"""
        return {
            'init': self.init,
            'quit': self.quit,
            'display': self.display,
            'event': self.event,
            'draw': self.draw,
            'mixer': self.mixer,
            'time': self.time,
            'key': self.key,
            'mouse': self.mouse,
            'image': self.image,
            'transform': self.transform,
            'Surface': self.Surface,
            'Color': self.Color,
            'Rect': self.Rect,
        }


class MockPygameDisplay:
    """Mock pygame.display module"""
    def __init__(self, pygame_mock):
        self.pygame_mock = pygame_mock

    def set_mode(self, resolution, flags=0, depth=0):
        """Set display mode"""
        self.pygame_mock.display_info.update({
            'width': resolution[0],
            'height': resolution[1],
            'flags': flags,
            'depth': depth
        })
        surface_data = {'size': resolution, 'type': 'display_surface', 'fills': [], 'blits': []}
        self.pygame_mock.surfaces.append(surface_data)
        return MockSurface(surface_data)

    def flip(self):
        """Flip the display"""
        self.pygame_mock.display_info['flip_count'] += 1

    def update(self, rectangle=None):
        """Update display"""
        pass

    def set_caption(self, title, icontitle=None):
        """Set window caption"""
        self.pygame_mock.display_info['caption'] = title

    def get_caption(self):
        """Get window caption"""
        return self.pygame_mock.display_info['caption']


class MockPygameEvent:
    """Mock pygame.event module"""
    def __init__(self, pygame_mock):
        self.pygame_mock = pygame_mock

    def get(self, eventtype=None):
        """Get events"""
        if eventtype is None:
            events = self.pygame_mock.events[:]
            self.pygame_mock.events.clear()
            return events
        else:
            matching_events = [e for e in self.pygame_mock.events if e.type == eventtype]
            self.pygame_mock.events = [e for e in self.pygame_mock.events if e.type != eventtype]
            return matching_events

    def pump(self):
        """Process events"""
        pass


class MockPygameDraw:
    """Mock pygame.draw module"""
    def __init__(self, pygame_mock):
        self.pygame_mock = pygame_mock

    def rect(self, surface, color, rect, width=0):
        """Draw rectangle"""
        self.pygame_mock.draw_calls.append({
            'type': 'rect',
            'surface': surface,
            'color': color,
            'rect': rect,
            'width': width
        })

    def circle(self, surface, color, pos, radius, width=0):
        """Draw circle"""
        self.pygame_mock.draw_calls.append({
            'type': 'circle',
            'surface': surface,
            'color': color,
            'pos': pos,
            'radius': radius,
            'width': width
        })

    def line(self, surface, color, start_pos, end_pos, width=1):
        """Draw line"""
        self.pygame_mock.draw_calls.append({
            'type': 'line',
            'surface': surface,
            'color': color,
            'start_pos': start_pos,
            'end_pos': end_pos,
            'width': width
        })


class MockPygameMixer:
    """Mock pygame.mixer module"""
    def __init__(self, pygame_mock):
        self.pygame_mock = pygame_mock

    def init(self):
        """Initialize mixer"""
        pass

    def Sound(self, filename):
        """Create sound object"""
        sound_data = {
            'type': 'sound',
            'filename': filename,
            'plays': 0
        }
        self.pygame_mock.sounds.append(sound_data)
        return MockSound(sound_data)


class MockPygameTime:
    """Mock pygame.time module"""
    def __init__(self, pygame_mock):
        self.pygame_mock = pygame_mock

    def Clock(self):
        """Create clock object"""
        return MockClock(self.pygame_mock)


class MockPygameKey:
    """Mock pygame.key module"""
    def __init__(self, pygame_mock):
        self.pygame_mock = pygame_mock

    def get_pressed(self):
        """Get pressed keys"""
        return self.pygame_mock.keys_pressed


class MockPygameMouse:
    """Mock pygame.mouse module"""
    def __init__(self, pygame_mock):
        self.pygame_mock = pygame_mock

    def get_pos(self):
        """Get mouse position"""
        return (0, 0)

    def get_pressed(self):
        """Get mouse button states"""
        return (False, False, False)


class MockPygameImage:
    """Mock pygame.image module"""
    def __init__(self, pygame_mock):
        self.pygame_mock = pygame_mock

    def load(self, filename):
        """Load image"""
        surface_data = {
            'type': 'image_surface',
            'filename': filename,
            'size': (32, 32)  # Default size
        }
        self.pygame_mock.surfaces.append(surface_data)
        return MockSurface(surface_data)


class MockPygameTransform:
    """Mock pygame.transform module"""
    def __init__(self, pygame_mock):
        self.pygame_mock = pygame_mock

    def scale(self, surface, size):
        """Scale surface"""
        return surface  # Return same surface for simplicity


class MockSurface:
    """Mock pygame Surface"""
    def __init__(self, data):
        self.data = data

    def fill(self, color):
        """Fill surface with color"""
        self.data.setdefault('fills', []).append(color)

    def blit(self, source, dest):
        """Blit surface onto this surface"""
        self.data.setdefault('blits', []).append({
            'source': source,
            'dest': dest
        })

    def get_rect(self):
        """Get surface rectangle"""
        size = self.data.get('size', (0, 0))
        return MockRect(0, 0, size[0], size[1])


class MockSound:
    """Mock pygame Sound"""
    def __init__(self, data):
        self.data = data

    def play(self):
        """Play sound"""
        self.data['plays'] += 1


class MockClock:
    """Mock pygame Clock"""
    def __init__(self, pygame_mock):
        self.pygame_mock = pygame_mock

    def tick(self, framerate=0):
        """Tick clock"""
        self.pygame_mock.clock_ticks.append(framerate)
        return 16  # Return mock milliseconds


class MockColor:
    """Mock pygame Color constants"""
    def __init__(self, r, g=None, b=None, a=255):
        if g is None:
            # Single argument - could be another color or string
            if isinstance(r, str):
                # Named color
                color_map = {
                    'red': (255, 0, 0),
                    'green': (0, 255, 0),
                    'blue': (0, 0, 255),
                    'white': (255, 255, 255),
                    'black': (0, 0, 0),
                    'yellow': (255, 255, 0),
                    'purple': (255, 0, 255),
                    'cyan': (0, 255, 255)
                }
                r, g, b = color_map.get(r.lower(), (0, 0, 0))
            else:
                # Grayscale
                g = b = r
        self.r, self.g, self.b, self.a = r, g, b, a

    def __iter__(self):
        return iter((self.r, self.g, self.b, self.a))

    def __getitem__(self, index):
        return (self.r, self.g, self.b, self.a)[index]


class MockRect:
    """Mock pygame Rect"""
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    @property
    def center(self):
        return (self.x + self.width // 2, self.y + self.height // 2)

    @center.setter
    def center(self, pos):
        self.x = pos[0] - self.width // 2
        self.y = pos[1] - self.height // 2

    def colliderect(self, other):
        """Check collision with another rect"""
        return False  # Mock collision detection