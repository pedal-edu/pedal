from pedal.types.new_types import ModuleType, FunctionType, void_function, ClassType, \
    InstanceType, bool_function, int_function, str_function, register_builtin_module

_VOID_FUNCTIONS = ['draw', 'start', 'debug', 'stop', 'stop_music', 'set_window_size', 'background_image',
                   'background_music', 'continue_music', 'destroy', 'pause', 'pause_music', 'play_music',
                   'play_sound', 'rewind_music', 'set_keyboard_delay', 'set_game_state',
                   'set_keyboard_interval', 'set_keyboard_repeat', 'set_mouse_cursor', 'set_mouse_position',
                   'set_mouse_visible', 'set_music_position', 'set_music_volume', 'set_window_color',
                   'set_window_size', 'set_window_state', 'set_window_title', 'set_world_state',
                   'disable_keyboard_repeating', 'enable_keyboard_repeating', 'when', 'unregister']
_DESIGNER_FUNCTIONS = ['circle', 'rectangle', 'arc', 'emoji', 'group', 'image',
                       'lines', 'pen', 'line', 'shape', 'text',
                       'Arc', 'DesignerObject', 'designer_object', 'ellipse']
_IDENTITY_FUNCTIONS = ['above', 'below', 'beside', 'spin',
                       'move_forward', 'move_backward', 'turn_left', 'turn_right', 'go_to', 'go_to_xy', 'go_to_mouse',
                       'point_towards', 'point_towards_mouse', 'point_in_direction', 'change_xy', 'change_x',
                       'change_y', 'set_x', 'set_y',
                       'get_angle', 'get_x', 'get_y',
                       'flip_x', 'flip_y', 'set_flip_x', 'set_flip_y', 'set_scale', 'set_scale_x', 'set_scale_y',
                       'set_background_image',
                       'get_scale', 'get_scale_x', 'get_scale_y', 'get_visible', 'get_flip_x', 'get_flip_y', 'show',
                       'hide',
                       'grow', 'grow_x', 'grow_y', 'shrink',
                       'move_to_x', 'move_to_y', 'move_to', 'move_to_mouse', 'move_to_xy',
                       'set_visible', 'change_scale', 'set_emoji_name', 'set_text']


def build_designer_module():
    _DesignerObject = ClassType('DesignerObject', {}, [])

    def _DesignerObject_constructor():
        return InstanceType(_DesignerObject)

    _DESIGNER_FIELDS = {
        'colliding': bool_function('colliding'),
        'colliding_with_mouse': bool_function('colliding_with_mouse'),
        'get_window_title': str_function('get_window_title'),
        'get_mouse_x': int_function('get_mouse_x'),
        'get_mouse_y': int_function('get_mouse_y'),
        'get_height': int_function('get_height'),
        'get_width': int_function('get_width'),
        'get_keyboard_delay': int_function('get_keyboard_delay'),
        'get_keyboard_interval': int_function('get_keyboard_interval'),
        'get_keyboard_repeat': bool_function('get_keyboard_repeat'),
        'get_emoji_name': str_function('get_emoji_name'),
        'get_text': str_function('get_text'),
    }

    _DESIGNER_FIELDS.update({
        name: void_function(name) for name in _VOID_FUNCTIONS
    })
    _DESIGNER_FIELDS.update({
        name: FunctionType(name, returns=_DesignerObject_constructor)
        for name in _DESIGNER_FUNCTIONS
    })
    _DESIGNER_FIELDS.update({
        name: FunctionType(name, returns='identity')
        for name in _IDENTITY_FUNCTIONS
    })
    return ModuleType('designer', _DESIGNER_FIELDS)


register_builtin_module('designer', build_designer_module)
