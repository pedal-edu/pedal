from pedal.types.new_types import ModuleType, FunctionType, void_function, ClassType, \
    InstanceType, bool_function, int_function, str_function, register_builtin_module

# TODO: route, Button, ...

_VOID_FUNCTIONS = []
_DESIGNER_FUNCTIONS = []
_IDENTITY_FUNCTIONS = []
_DECORATOR_FUNCTIONS = ["route"]

def build_drafter_module():
    _PageObject = ClassType('Page', {
        'state': AnyType(),
        'content': ListType(AnyType())
    }, [])

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
    return ModuleType('drafter', _DRAFTER_FIELDS)


register_builtin_module('drafter', build_drafter_module)
