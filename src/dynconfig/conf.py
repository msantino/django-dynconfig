"""
Package settings with sensible defaults.

All settings are optional. Override in your Django settings.py:

    DYNCONFIG_CACHE_TIMEOUT = 600
    DYNCONFIG_ENCRYPTION_KEY = "your-fernet-key"

Settings are read lazily (on every access) so they work correctly with
Django's test overrides and pytest-django's `settings` fixture.
"""

from django.conf import settings


def __getattr__(name):
    """Lazy access to dynconfig settings — reads from Django settings on every call."""
    _defaults = {
        "CACHE_BACKEND": ("DYNCONFIG_CACHE_BACKEND", "default"),
        "CACHE_TIMEOUT": ("DYNCONFIG_CACHE_TIMEOUT", 300),
        "CACHE_PREFIX": ("DYNCONFIG_CACHE_PREFIX", "dynconfig"),
        "ENCRYPTION_KEY": ("DYNCONFIG_ENCRYPTION_KEY", None),
        "RAISE_NOT_FOUND": ("DYNCONFIG_RAISE_NOT_FOUND", False),
    }

    if name in _defaults:
        django_name, default = _defaults[name]
        return getattr(settings, django_name, default)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
