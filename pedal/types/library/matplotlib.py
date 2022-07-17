from pedal.types.new_types import BUILTIN_MODULES, ModuleType, FunctionType, NoneType

# MatPlotLib Support
_PYPLOT_MODULE = ModuleType('pyplot', fields={
    'plot': FunctionType(name='plot', returns=NoneType),
    'hist': FunctionType(name='hist', returns=NoneType),
    'scatter': FunctionType(name='scatter', returns=NoneType),
    'show': FunctionType(name='show', returns=NoneType),
    'xlabel': FunctionType(name='xlabel', returns=NoneType),
    'ylabel': FunctionType(name='ylabel', returns=NoneType),
    'title': FunctionType(name='title', returns=NoneType),
})
BUILTIN_MODULES['matplotlib'] = ModuleType('matplotlib', {}, {'pyplot': _PYPLOT_MODULE})
