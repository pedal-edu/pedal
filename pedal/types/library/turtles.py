from pedal.types.new_types import BUILTIN_MODULES, ModuleType, void_function


BUILTIN_MODULES['turtle'] = ModuleType('turtle', {
   'forward': void_function('forward'),
   'backward': void_function('backward'),
   'color': void_function('color'),
   'right': void_function('right'),
   'left': void_function('left'),
}, {})
