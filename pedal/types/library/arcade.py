from pedal.types.new_types import ModuleType, FunctionType, NoneType, ListType, BoolType, NumType, register_builtin_module


# Arcade Support
def load_arcade_module():
    """Load type definitions for the Arcade game library."""
    
    # Color module types
    _COLOR_MODULE = ModuleType('color', fields={
        'WHITE': NumType,
        'BLACK': NumType,
        'RED': NumType,
        'GREEN': NumType,
        'BLUE': NumType,
        'YELLOW': NumType,
        'PURPLE': NumType,
        'CYAN': NumType,
        'ORANGE': NumType,
        'GRAY': NumType,
    })
    
    # Main arcade module types
    _ARCADE_MODULE = ModuleType('arcade', fields={
        # Window management
        'open_window': FunctionType(name='open_window', returns=NoneType),
        'set_background_color': FunctionType(name='set_background_color', returns=NoneType),
        'close_window': FunctionType(name='close_window', returns=NoneType),
        
        # Rendering
        'start_render': FunctionType(name='start_render', returns=NoneType),
        'finish_render': FunctionType(name='finish_render', returns=NoneType),
        
        # Drawing functions
        'draw_circle_filled': FunctionType(name='draw_circle_filled', returns=NoneType),
        'draw_circle_outline': FunctionType(name='draw_circle_outline', returns=NoneType),
        'draw_rectangle_filled': FunctionType(name='draw_rectangle_filled', returns=NoneType),
        'draw_rectangle_outline': FunctionType(name='draw_rectangle_outline', returns=NoneType),
        'draw_line': FunctionType(name='draw_line', returns=NoneType),
        'draw_text': FunctionType(name='draw_text', returns=NoneType),
        
        # Sprite management
        'Sprite': FunctionType(name='Sprite', returns=ModuleType('Sprite')),
        'SpriteList': FunctionType(name='SpriteList', returns=ListType),
        
        # Physics
        'PhysicsEngineSimple': FunctionType(name='PhysicsEngineSimple', returns=ModuleType('PhysicsEngine')),
        
        # Sound
        'load_sound': FunctionType(name='load_sound', returns=ModuleType('Sound')),
        'play_sound': FunctionType(name='play_sound', returns=NoneType),
        
        # Game loop
        'run': FunctionType(name='run', returns=NoneType),
        'schedule': FunctionType(name='schedule', returns=NoneType),
        
        # Collision detection
        'check_for_collision': FunctionType(name='check_for_collision', returns=BoolType),
        'check_for_collision_with_list': FunctionType(name='check_for_collision_with_list', returns=ListType),
        'get_sprites_at_point': FunctionType(name='get_sprites_at_point', returns=ListType),
        
        # Color constants
        'color': _COLOR_MODULE,
    })
    
    return _ARCADE_MODULE


register_builtin_module('arcade', load_arcade_module)