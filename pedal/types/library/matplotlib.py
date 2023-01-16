from pedal.types.new_types import ModuleType, FunctionType, NoneType, register_builtin_module


# MatPlotLib Support
def load_matplot_module():
    _PYPLOT_MODULE = ModuleType('pyplot', fields={
        'plot': FunctionType(name='plot', returns=NoneType),
        'hist': FunctionType(name='hist', returns=NoneType),
        'scatter': FunctionType(name='scatter', returns=NoneType),
        'show': FunctionType(name='show', returns=NoneType),
        'xlabel': FunctionType(name='xlabel', returns=NoneType),
        'ylabel': FunctionType(name='ylabel', returns=NoneType),
        'title': FunctionType(name='title', returns=NoneType),
    })
    return ModuleType('matplotlib', {}, {'pyplot': _PYPLOT_MODULE})


register_builtin_module('matplotlib', load_matplot_module)
