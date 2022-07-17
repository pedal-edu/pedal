def get_default_tifa_settings():
    return {
        # Type System
        'accept_generic_types': True,
        'numeric_type_equality': True,
        'struct_type': {
            'dataclasses': True,
            'typed_dict': True,
            'record_dict': True,
            'class': True
        },
        'enforce_nominal_types': True,
        'evaluate_string_literal_types': False,
        'allow_type_changes': True,
        'truthiness_returns_booleans': True,
        # Flow System
        'allow_global_writes': False,
        'allow_unused_variables': False,
        'allow_unused_return_value': False,
        'allow_unused_expression_value': False,
        # Bad Code
        'allow_redundant_equal_true': False,
        'allow_redundant_empty_else': False,
        'allow_unnecessary_if_return': False,
        # Versioning
        'type_system_version': 2
    }
