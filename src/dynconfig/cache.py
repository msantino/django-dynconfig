"""
Cache layer using Django's cache framework.

Caches individual config values with configurable TTL.
Cache is invalidated automatically via model signals on save/delete.
"""

import logging

from django.core.cache import caches

from . import conf

logger = logging.getLogger(__name__)


def _get_cache():
    return caches[conf.CACHE_BACKEND]


def _make_key(config_key):
    return f"{conf.CACHE_PREFIX}:{config_key}"


def get(key):
    """
    Get a cached value. Returns the cached value or None if not found.

    The cache stores a tuple of (raw_value, value_type, is_encrypted) to avoid
    needing a DB hit for type information.
    """
    cache_key = _make_key(key)
    return _get_cache().get(cache_key)


def set(key, raw_value, value_type, is_encrypted):  # noqa: A001
    """Cache a config entry's data."""
    cache_key = _make_key(key)
    data = (raw_value, value_type, is_encrypted)
    _get_cache().set(cache_key, data, timeout=conf.CACHE_TIMEOUT)


def delete(key):
    """Remove a config entry from cache."""
    cache_key = _make_key(key)
    _get_cache().delete(cache_key)


def clear():
    """Clear all dynconfig cache entries."""
    # Django's cache doesn't support prefix-based deletion natively,
    # so we track keys or clear the whole cache backend.
    # For simplicity, we clear on a per-key basis via signals.
    # This method is a convenience for manual full-clear.
    _get_cache().clear()
    logger.info("dynconfig: cache cleared.")
