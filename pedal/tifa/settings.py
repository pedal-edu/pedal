def get_default_tifa_settings():
    # Import here to avoid circular imports
    from pedal.types.config import get_default_type_system_config
    
    # Get unified type system config and convert to TIFA format
    type_config = get_default_type_system_config()
    tifa_settings = type_config.to_tifa_settings()
    
    # Add TIFA-specific settings that aren't part of the unified type system
    tifa_settings.update({
        # Flow System
        'allow_global_writes': False,
        'allow_unused_variables': False,
        'allow_unused_return_value': False,
        'allow_unused_expression_value': False,
        # Bad Code
        'allow_redundant_equal_true': False,
        'allow_redundant_empty_else': False,
        'allow_unnecessary_if_return': False,
    })
    
    return tifa_settings
