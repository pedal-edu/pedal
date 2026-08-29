from pedal.types.new_types import ModuleType, FunctionType, NoneType, ListType, BoolType, NumType, register_builtin_module


# Pygame Support
def load_pygame_module():
    """Load type definitions for the Pygame game library."""
    
    # Display module types
    _DISPLAY_MODULE = ModuleType('display', fields={
        'set_mode': FunctionType(name='set_mode', returns=ModuleType('Surface')),
        'flip': FunctionType(name='flip', returns=NoneType),
        'update': FunctionType(name='update', returns=NoneType),
        'set_caption': FunctionType(name='set_caption', returns=NoneType),
        'get_caption': FunctionType(name='get_caption', returns=str),
    })
    
    # Event module types
    _EVENT_MODULE = ModuleType('event', fields={
        'get': FunctionType(name='get', returns=ListType),
        'pump': FunctionType(name='pump', returns=NoneType),
    })
    
    # Draw module types
    _DRAW_MODULE = ModuleType('draw', fields={
        'rect': FunctionType(name='rect', returns=NoneType),
        'circle': FunctionType(name='circle', returns=NoneType),
        'line': FunctionType(name='line', returns=NoneType),
    })
    
    # Mixer module types
    _MIXER_MODULE = ModuleType('mixer', fields={
        'init': FunctionType(name='init', returns=NoneType),
        'Sound': FunctionType(name='Sound', returns=ModuleType('Sound')),
    })
    
    # Time module types
    _TIME_MODULE = ModuleType('time', fields={
        'Clock': FunctionType(name='Clock', returns=ModuleType('Clock')),
    })
    
    # Key module types
    _KEY_MODULE = ModuleType('key', fields={
        'get_pressed': FunctionType(name='get_pressed', returns=ListType),
    })
    
    # Mouse module types
    _MOUSE_MODULE = ModuleType('mouse', fields={
        'get_pos': FunctionType(name='get_pos', returns=ListType),
        'get_pressed': FunctionType(name='get_pressed', returns=ListType),
    })
    
    # Image module types
    _IMAGE_MODULE = ModuleType('image', fields={
        'load': FunctionType(name='load', returns=ModuleType('Surface')),
    })
    
    # Transform module types
    _TRANSFORM_MODULE = ModuleType('transform', fields={
        'scale': FunctionType(name='scale', returns=ModuleType('Surface')),
    })
    
    # Main pygame module types
    _PYGAME_MODULE = ModuleType('pygame', fields={
        # Core functions
        'init': FunctionType(name='init', returns=NumType),
        'quit': FunctionType(name='quit', returns=NoneType),
        
        # Submodules
        'display': _DISPLAY_MODULE,
        'event': _EVENT_MODULE,
        'draw': _DRAW_MODULE,
        'mixer': _MIXER_MODULE,
        'time': _TIME_MODULE,
        'key': _KEY_MODULE,
        'mouse': _MOUSE_MODULE,
        'image': _IMAGE_MODULE,
        'transform': _TRANSFORM_MODULE,
        
        # Classes
        'Surface': FunctionType(name='Surface', returns=ModuleType('Surface')),
        'Color': FunctionType(name='Color', returns=ModuleType('Color')),
        'Rect': FunctionType(name='Rect', returns=ModuleType('Rect')),
    })
    
    return _PYGAME_MODULE


register_builtin_module('pygame', load_pygame_module)