"""
django-dynconfig — Dynamic configuration management for Django.
"""

__version__ = "0.1.0"

default_app_config = "dynconfig.apps.DynConfigConfig"

_SENTINEL = object()


def get_config(key, *, default=_SENTINEL):
    """Get a configuration value by key. Returns typed value."""
    from .services import get_config as _get_config

    if default is _SENTINEL:
        return _get_config(key)
    return _get_config(key, default=default)


def set_config(key, value, *, value_type=None, group="general", help_text="", is_encrypted=False):
    """Set a configuration value. Creates the entry if it doesn't exist."""
    from .services import set_config as _set_config

    return _set_config(key, value, value_type=value_type, group=group, help_text=help_text, is_encrypted=is_encrypted)


def get_configs_by_group(group):
    """Get all configuration values in a group as a dictionary."""
    from .services import get_configs_by_group as _get_configs_by_group

    return _get_configs_by_group(group)
