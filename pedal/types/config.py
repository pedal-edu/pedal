"""
Configuration system for Pedal's unified type system.

This module provides a centralized configuration system that allows teachers
to customize type system behavior across all Pedal tools (TIFA, Assertions, etc.).
"""


class TypeSystemConfig:
    """
    Centralized configuration for Pedal's type system.

    This configuration class controls how types are interpreted, normalized,
    and compared across all Pedal tools. Teachers can modify these settings
    to achieve specific educational experiences.

    Attributes:
        accept_generic_types (bool): Whether to accept generic type annotations
            like List[int] or just List. Default: True
        numeric_type_equality (bool): Whether int and float should be considered
            equivalent for type checking. Default: True
        enforce_nominal_types (bool): Whether to strictly enforce nominal typing
            vs structural typing. Default: True
        evaluate_string_literal_types (bool): Whether string literal types should
            be evaluated as actual types. Default: False
        allow_type_changes (bool): Whether variables can change types during
            execution. Default: True
        truthiness_returns_booleans (bool): Whether truthiness operations
            should always return boolean types. Default: True
        allow_optional_by_default (bool): Whether None should be automatically
            allowed for all types (making them Optional). Default: False
        support_list_annotations (bool): Whether to support custom list annotations
            like [int] for List[int]. Default: True
        allow_any_fallback (bool): Whether unknown types should fall back to
            Any type instead of generating errors. Default: False
        struct_type_support (dict): Controls which structural type patterns
            are supported (dataclasses, typed_dict, record_dict, class).
    """

    def __init__(self, **kwargs):
        # Type System Core Settings
        self.accept_generic_types = kwargs.get('accept_generic_types', True)
        self.numeric_type_equality = kwargs.get('numeric_type_equality', True)
        self.enforce_nominal_types = kwargs.get('enforce_nominal_types', True)
        self.evaluate_string_literal_types = kwargs.get('evaluate_string_literal_types', False)
        self.allow_type_changes = kwargs.get('allow_type_changes', True)
        self.truthiness_returns_booleans = kwargs.get('truthiness_returns_booleans', True)

        # Teacher Customization Settings
        self.allow_optional_by_default = kwargs.get('allow_optional_by_default', False)
        self.support_list_annotations = kwargs.get('support_list_annotations', True)
        self.allow_any_fallback = kwargs.get('allow_any_fallback', False)

        # Structural Type Support
        self.struct_type_support = kwargs.get('struct_type_support', {
            'dataclasses': True,
            'typed_dict': True,
            'record_dict': True,
            'class': True
        })

        # Versioning for backward compatibility
        self.type_system_version = kwargs.get('type_system_version', 2)

    def copy(self, **overrides):
        """
        Create a copy of this configuration with optional overrides.

        Args:
            **overrides: Configuration values to override in the copy

        Returns:
            TypeSystemConfig: New configuration instance
        """
        current_config = self.to_dict()
        current_config.update(overrides)
        return TypeSystemConfig(**current_config)

    def to_dict(self):
        """
        Convert configuration to dictionary format.

        Returns:
            dict: Configuration as dictionary
        """
        return {
            'accept_generic_types': self.accept_generic_types,
            'numeric_type_equality': self.numeric_type_equality,
            'enforce_nominal_types': self.enforce_nominal_types,
            'evaluate_string_literal_types': self.evaluate_string_literal_types,
            'allow_type_changes': self.allow_type_changes,
            'truthiness_returns_booleans': self.truthiness_returns_booleans,
            'allow_optional_by_default': self.allow_optional_by_default,
            'support_list_annotations': self.support_list_annotations,
            'allow_any_fallback': self.allow_any_fallback,
            'struct_type_support': self.struct_type_support.copy(),
            'type_system_version': self.type_system_version
        }

    @classmethod
    def from_tifa_settings(cls, tifa_settings):
        """
        Create TypeSystemConfig from TIFA settings dictionary for backward compatibility.

        Args:
            tifa_settings (dict): TIFA settings dictionary

        Returns:
            TypeSystemConfig: New configuration instance
        """
        return cls(
            accept_generic_types=tifa_settings.get('accept_generic_types', True),
            numeric_type_equality=tifa_settings.get('numeric_type_equality', True),
            enforce_nominal_types=tifa_settings.get('enforce_nominal_types', True),
            evaluate_string_literal_types=tifa_settings.get('evaluate_string_literal_types', False),
            allow_type_changes=tifa_settings.get('allow_type_changes', True),
            truthiness_returns_booleans=tifa_settings.get('truthiness_returns_booleans', True),
            struct_type_support=tifa_settings.get('struct_type', {
                'dataclasses': True,
                'typed_dict': True,
                'record_dict': True,
                'class': True
            }),
            type_system_version=tifa_settings.get('type_system_version', 2)
        )

    def to_tifa_settings(self):
        """
        Convert to TIFA settings format for backward compatibility.

        Returns:
            dict: TIFA-compatible settings dictionary
        """
        return {
            'accept_generic_types': self.accept_generic_types,
            'numeric_type_equality': self.numeric_type_equality,
            'struct_type': self.struct_type_support,
            'enforce_nominal_types': self.enforce_nominal_types,
            'evaluate_string_literal_types': self.evaluate_string_literal_types,
            'allow_type_changes': self.allow_type_changes,
            'truthiness_returns_booleans': self.truthiness_returns_booleans,
            'type_system_version': self.type_system_version
        }


# Global default configuration instance
_default_config = TypeSystemConfig()


def get_default_type_system_config():
    """
    Get the default type system configuration.

    Returns:
        TypeSystemConfig: Default configuration instance
    """
    return _default_config


def set_default_type_system_config(config):
    """
    Set the global default type system configuration.

    Args:
        config (TypeSystemConfig): New default configuration
    """
    global _default_config
    _default_config = config


def configure_type_system(**kwargs):
    """
    Configure the global type system with the given settings.

    Args:
        **kwargs: Configuration parameters

    Returns:
        TypeSystemConfig: The updated configuration
    """
    global _default_config
    _default_config = _default_config.copy(**kwargs)
    return _default_config