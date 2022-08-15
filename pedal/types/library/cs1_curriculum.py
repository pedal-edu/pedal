from pedal.types.new_types import BUILTIN_MODULES, ModuleType, FunctionType, NoneType

BUILTIN_MODULES['cisc108'] = ModuleType('cisc108', fields={
    'assert_equal': FunctionType(name='assert_equal', returns=NoneType),
    'assert_type': FunctionType(name='assert_type', returns=NoneType),
})

BUILTIN_MODULES['cisc106'] = ModuleType('cisc106', fields={
    'assert_equal': FunctionType(name='assert_equal', returns=NoneType),
    'assert_type': FunctionType(name='assert_type', returns=NoneType),
})

BUILTIN_MODULES['bakery'] = ModuleType('bakery', fields={
    'assert_equal': FunctionType(name='assert_equal', returns=NoneType),
    'assert_type': FunctionType(name='assert_type', returns=NoneType),
})