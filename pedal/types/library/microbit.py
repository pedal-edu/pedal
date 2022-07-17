from pedal.types.builtin import BUILTIN_MODULES
from pedal.types.new_types import ModuleType, FunctionType
from pedal.types.new_types import void_function, int_function, ClassType, bool_function, InstanceType

_VOID_FUNCTIONS = ['run_every', 'panic', 'sleep', 'set_volume']

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
   'button_b': InstanceType(_BUTTON_CLASS)
}
_MICROBIT_FIELDS.update({
   name: void_function for name in _VOID_FUNCTIONS
})

BUILTIN_MODULES['microbit'] = ModuleType('microbit', fields=_MICROBIT_FIELDS)
