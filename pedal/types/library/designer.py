from pedal.types.new_types import BUILTIN_MODULES, ModuleType, FunctionType, NoneType

BUILTIN_MODULES['designer'] = ModuleType('designer', fields={
    'set_window_size': FunctionType(name='set_window_size', returns=NoneType)
})