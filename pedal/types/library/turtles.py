from pedal.types.new_types import ModuleType, void_function, register_builtin_module


def load_turtle_module():
    return ModuleType('turtle', {
        'forward': void_function('forward'),
        'backward': void_function('backward'),
        'color': void_function('color'),
        'right': void_function('right'),
        'left': void_function('left'),
    }, {})


register_builtin_module('turtle', load_turtle_module)
