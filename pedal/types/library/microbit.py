from pedal.types.builtin import BUILTIN_MODULES
from pedal.types.new_types import ModuleType, FunctionType, register_builtin_module
from pedal.types.new_types import void_function, int_function, ClassType, bool_function, InstanceType

_VOID_FUNCTIONS = ['run_every', 'panic', 'sleep', 'set_volume']


def load_microbit_module():
    _BUTTON_CLASS = ClassType('Button', {
        'is_pressed': bool_function('is_pressed'),
        'was_pressed': bool_function('was_pressed'),
        'get_presses': int_function('get_presses')
    }, [])

    _MICROBIT_FIELDS = {
        'running_time': int_function('running_time'),
        'temperature': int_function('temperature'),
        'Button': _BUTTON_CLASS,
        'button_a': InstanceType(_BUTTON_CLASS),
        'button_b': InstanceType(_BUTTON_CLASS),
    }
    _MICROBIT_FIELDS.update({
        name: void_function for name in _VOID_FUNCTIONS
    })

    _MICROBIT_SUBMODULES = {
        'display': ModuleType('display', {
            'show': void_function('show'),
            'scroll': void_function('scroll'),
            'on': void_function('on'),
            'off': void_function('off'),
            'clear': void_function('clear'),
            'set_pixel': void_function('set_pixel'),
            'get_pixel': int_function('get_pixel'),
            'is_on': bool_function('is_on'),
            'read_light_level': int_function('read_light_level')
        })
    }

    return ModuleType('microbit', fields=_MICROBIT_FIELDS, submodules=_MICROBIT_SUBMODULES)


register_builtin_module('microbit', load_microbit_module)
