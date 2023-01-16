from pedal.types.new_types import BUILTIN_MODULES, ModuleType, FunctionType, NoneType, register_builtin_module

register_builtin_module('cisc108', lambda: ModuleType('cisc108', fields={
    'assert_equal': FunctionType(name='assert_equal', returns=NoneType),
    'assert_type': FunctionType(name='assert_type', returns=NoneType),
}))

register_builtin_module('cisc106', lambda: ModuleType('cisc106', fields={
    'assert_equal': FunctionType(name='assert_equal', returns=NoneType),
    'assert_type': FunctionType(name='assert_type', returns=NoneType),
}))

register_builtin_module('bakery', lambda: ModuleType('bakery', fields={
    'assert_equal': FunctionType(name='assert_equal', returns=NoneType),
    'assert_type': FunctionType(name='assert_type', returns=NoneType),
}))