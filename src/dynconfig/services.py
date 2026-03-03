"""
Core service layer — the public API for reading and writing configuration values.

Usage:
    from dynconfig import get_config, set_config, get_configs_by_group

    secret = get_config("asaas.webhook_secret")
    max_retries = get_config("asaas.max_retries", default=3)
    set_config("asaas.max_retries", 5, value_type="integer", group="billing")
    all_billing = get_configs_by_group("billing")
"""

import json
import logging

from . import cache as config_cache
from . import conf
from .encryption import decrypt, encrypt
from .exceptions import ConfigNotFoundError
from .types import cast_value

logger = logging.getLogger(__name__)

_SENTINEL = object()


def get_config(key, *, default=_SENTINEL):
    """
    Get a configuration value by key.

    Checks cache first, then database. Returns the value cast to its configured type.
    Encrypted values are decrypted transparently.

    Args:
        key: The configuration key (e.g. "asaas.api_key").
        default: Value to return if the key doesn't exist.
                 If not provided and DYNCONFIG_RAISE_NOT_FOUND is True, raises ConfigNotFoundError.

    Returns:
        The typed configuration value.
    """
    # Check cache
    cached = config_cache.get(key)
    if cached is not None:
        raw_value, value_type, is_encrypted = cached
        if is_encrypted:
            raw_value = decrypt(raw_value)
        return cast_value(key, raw_value, value_type)

    # Cache miss — hit database
    from .models import ConfigEntry

    try:
        entry = ConfigEntry.objects.get(key=key)
    except ConfigEntry.DoesNotExist:
        if default is not _SENTINEL:
            return default
        if conf.RAISE_NOT_FOUND:
            raise ConfigNotFoundError(key) from None
        return None

    # Populate cache
    config_cache.set(key, entry.value, entry.value_type, entry.is_encrypted)

    raw_value = entry.value
    if entry.is_encrypted:
        raw_value = decrypt(raw_value)

    return cast_value(key, raw_value, entry.value_type)


def set_config(key, value, *, value_type=None, group="general", help_text="", is_encrypted=False):
    """
    Set a configuration value. Creates or updates the config entry.

    Args:
        key: The configuration key.
        value: The value to store. Will be serialized to string.
        value_type: The type hint (string, integer, boolean, json, list, etc.).
                    Auto-detected from the Python type if not provided.
        group: Logical grouping (default: "general").
        help_text: Description shown in admin.
        is_encrypted: Whether to encrypt the value at rest.

    Returns:
        The ConfigEntry instance.
    """
    from .models import ConfigEntry

    if value_type is None:
        value_type = _detect_type(value)

    # Serialize to string for storage
    raw_value = _serialize_value(value, value_type)

    # Encrypt if needed
    if is_encrypted:
        raw_value = encrypt(raw_value)

    entry, created = ConfigEntry.objects.update_or_create(
        key=key,
        defaults={
            "value": raw_value,
            "value_type": value_type,
            "is_encrypted": is_encrypted,
            "group": group,
            "help_text_field": help_text,
        },
    )

    # Cache is invalidated by the post_save signal, but we also set it here
    # to ensure the caller gets the latest value on next get_config().
    config_cache.set(key, entry.value, entry.value_type, entry.is_encrypted)

    action = "created" if created else "updated"
    logger.info("dynconfig: %s config '%s' [%s]", action, key, value_type)

    return entry


def get_configs_by_group(group):
    """
    Get all configuration values in a group as a dictionary.

    Args:
        group: The group name.

    Returns:
        Dict mapping keys to their typed values.
    """
    from .models import ConfigEntry

    entries = ConfigEntry.objects.filter(group=group)
    result = {}
    for entry in entries:
        raw_value = entry.value
        if entry.is_encrypted:
            raw_value = decrypt(raw_value)
        result[entry.key] = cast_value(entry.key, raw_value, entry.value_type)
    return result


def _detect_type(value):
    """Auto-detect value_type from a Python value."""
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "float"
    if isinstance(value, (dict, list)):
        return "json"
    return "string"


def _serialize_value(value, value_type):
    """Convert a Python value to a string for database storage."""
    if value_type == "json":
        return json.dumps(value, ensure_ascii=False)
    if value_type == "boolean":
        return "true" if value else "false"
    if value_type == "list" and isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value)
