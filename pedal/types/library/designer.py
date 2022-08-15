from pedal.types.new_types import BUILTIN_MODULES, ModuleType, FunctionType, NoneType, void_function, ClassType, \
    InstanceType

_VOID_FUNCTIONS = ['draw', 'start', 'set_window_size']

_DesignerObject = ClassType('DesignerObject', {}, [])
_DesignerObject_constructor = lambda: InstanceType(_DesignerObject)

_DESIGNER_FIELDS = {
    'circle': FunctionType('circle', returns=_DesignerObject_constructor),
    'rectangle': FunctionType('rectangle', returns=_DesignerObject_constructor),
    'arc': FunctionType('rectangle', returns=_DesignerObject_constructor),
    'group': FunctionType('group', returns=_DesignerObject_constructor),
    'move_to_xy': FunctionType('move_to_xy', returns='identity'),
    'change_xy': FunctionType('move_to_xy', returns='identity'),
    'change_x': FunctionType('move_to_xy', returns='identity'),
    'change_y': FunctionType('move_to_xy', returns='identity'),
}

_DESIGNER_FIELDS.update({
   name: void_function for name in _VOID_FUNCTIONS
})

BUILTIN_MODULES['designer'] = ModuleType('designer', _DESIGNER_FIELDS)
