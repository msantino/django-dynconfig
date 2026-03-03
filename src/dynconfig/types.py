"""
Type casting for configuration values.

Converts string values stored in the database to their intended Python types.
"""

import json

from .exceptions import ConfigTypeError


def cast_value(key, raw_value, value_type):
    """Cast a raw string value to the specified type."""
    if raw_value == "" and value_type not in ("string", "text"):
        return _get_empty_default(value_type)

    try:
        return _CASTERS[value_type](raw_value)
    except (ValueError, TypeError, json.JSONDecodeError) as e:
        raise ConfigTypeError(key, raw_value, value_type, original_error=e) from e


def _cast_string(value):
    return str(value)


def _cast_text(value):
    return str(value)


def _cast_integer(value):
    return int(value)


def _cast_float(value):
    return float(value)


def _cast_boolean(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        if value.lower() in ("true", "1", "yes", "on"):
            return True
        if value.lower() in ("false", "0", "no", "off", ""):
            return False
    raise ValueError(f"Cannot convert '{value}' to boolean.")


def _cast_json(value):
    if isinstance(value, (dict, list)):
        return value
    return json.loads(value)


def _cast_list(value):
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        if not value.strip():
            return []
        return [item.strip() for item in value.split(",") if item.strip()]
    raise ValueError(f"Cannot convert '{value}' to list.")


def _get_empty_default(value_type):
    """Return sensible empty defaults for each type."""
    defaults = {
        "integer": 0,
        "float": 0.0,
        "boolean": False,
        "json": {},
        "list": [],
    }
    return defaults.get(value_type, "")


_CASTERS = {
    "string": _cast_string,
    "text": _cast_text,
    "integer": _cast_integer,
    "float": _cast_float,
    "boolean": _cast_boolean,
    "json": _cast_json,
    "list": _cast_list,
}
