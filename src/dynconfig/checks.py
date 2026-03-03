"""
Django system checks for dynconfig.

Run with: python manage.py check
"""

from django.core.checks import Warning, register


@register()
def check_encryption_key(app_configs, **kwargs):
    """Warn if encrypted config entries exist but no encryption key is set."""
    errors = []

    from . import conf

    if conf.ENCRYPTION_KEY:
        return errors

    # Only check if tables exist (skip during initial migration)
    try:
        from .models import ConfigEntry

        encrypted_count = ConfigEntry.objects.filter(is_encrypted=True).count()
    except Exception:
        return errors

    if encrypted_count > 0:
        errors.append(
            Warning(
                f"Found {encrypted_count} encrypted config entries but DYNCONFIG_ENCRYPTION_KEY is not set.",
                hint="Set DYNCONFIG_ENCRYPTION_KEY in your Django settings to decrypt these values.",
                id="dynconfig.W001",
            )
        )

    return errors
