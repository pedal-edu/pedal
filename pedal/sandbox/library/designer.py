from pedal.sandbox.mocked import MockModule
from pedal.utilities.system import IS_PYTHON_36


class MockDesigner(MockModule):
    """
    This will eventually be much more sophisticated. We really need a "MockPygame" that provides a
    window-less version of itself suitable for testing. I think that will be very key for the long-term
    testing behavior of Designer!
    """
    UNKNOWN_FUNCTIONS = []

    SUBMODULES = []

    module_name = 'designer'
    FIELDS = ['Animation', 'Arc', 'COMMON_EVENT_NAMES', 'COMMON_EVENT_NAME_LOOKUP',
              'emoji', '_tifa_definitions',
              'CubicIn', 'CubicInOut', 'CubicOut', 'DEFAULT_WINDOW_TITLE', 'DelayAnimation', 'DesignerObject',
              'Director', 'Event', 'EventHandler', 'GLOBAL_DIRECTOR', 'GameEndException', 'InternalImage',
              'Iterate', 'KNOWN_EVENTS', 'KeyboardKey', 'KeyboardModule', 'Keys', 'Linear', 'LinearTuple',
              'List', 'LiveEventHandler', 'MOUSE_MAP', 'Mods', 'MouseModule', 'MultiAnimation', 'MusicModule',
              'Optional', 'Polar', 'QuadraticIn', 'QuadraticInOut', 'QuadraticOut', 'Random',
              'ReplayEventHandler', 'Request', 'SequentialAnimation', 'SfxModule', 'Sine', 'Union', 'Vec2D',
              'WeakMethod', 'WeakSet', 'Window', 'above',
              'animation', 'arc', 'background_image', 'background_music', 'base64', 'below', 'check_initialized',
              'circle', 'clear_namespace', 'colliding', 'colors', 'continue_music', 'core', 'cursors', 'designer',
              'designer_object', 'destroy', 'difflib', 'disable_keyboard_repeating', 'draw', 'ellipse',
              'enable_keyboard_repeating', 'environ', 'f', 'get_director', 'get_height', 'get_keyboard_delay',
              'get_keyboard_interval', 'get_keyboard_repeat', 'get_mouse_cursor', 'get_mouse_position',
              'get_mouse_visible', 'get_mouse_x', 'get_mouse_y', 'get_music_position', 'get_music_volume',
              'get_positional_event_parameters', 'get_width', 'get_window_color', 'get_window_title',
              'glide_around', 'glide_down', 'glide_in_degrees', 'glide_left', 'glide_right', 'glide_up',
              'group', 'handle', 'helpers', 'hex_to_rgb', 'image', 'imghdr', 'importlib', 'inspect', 'io',
              'is_music_playing', 'json', 'keyboard', 'keys', 'line', 'linear_animation', 'make_suggestions',
              'math', 'mods', 'mouse', 'music', 'objects', 'os', 'path', 'pause', 'pause_music', 'play_music',
              'play_sound', 'positioning', 'pprint', 'pygame', 'queue', 'random', 're', 'rectangle', 'register',
              'rewind_music', 'sequence_animation', 'set_game_state', 'set_keyboard_delay',
              'set_keyboard_interval', 'set_keyboard_repeat', 'set_mouse_cursor', 'set_mouse_position',
              'set_mouse_visible', 'set_music_position', 'set_music_volume', 'set_window_color',
              'set_window_size', 'set_window_state', 'set_window_title', 'set_world_state', 'sfx', 'shape',
              'spin', 'start', 'stop', 'stop_music', 'sys', 'text', 'this_directory', 'unregister', 'urlopen',
              'utilities', 'when']

    def __init__(self):
        super().__init__()
        self.calls = []

    def get_submodules(self):
        return {}

    def _reset_designer(self):
        self.calls = []

    def _generate_patches(self):
        if IS_PYTHON_36:
            # Generate patches manually
            return {name: self.getter(name) for name in self.FIELDS}
        else:
            return {'__getattr__': self.getter, '__all__': ['test']}

    def getter(self, key):
        " If anything asks, we prevent the module. Except for __file__. "
        # Needed to support coverage - it's okay to ask who I am.
        if key == '__file__':
            return self.module_name
        if key == '__all__':
            return self.FIELDS

        def _fake_call_wrapper(*args, **kwargs):
            self.calls.append((key, args, kwargs))
            return self._fake_call(args, kwargs)

        return _fake_call_wrapper

    def _fake_call(self, *args, **kwargs):
        return 0


