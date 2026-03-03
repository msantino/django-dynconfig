"""
Signal handlers for cache invalidation.

Automatically clears cache when config entries are saved or deleted.
"""

import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from . import cache as config_cache

logger = logging.getLogger(__name__)


@receiver(post_save, sender="dynconfig.ConfigEntry")
def invalidate_cache_on_save(sender, instance, **kwargs):
    """Clear the cache for this key when a config entry is saved."""
    config_cache.delete(instance.key)
    logger.debug("dynconfig: cache invalidated for '%s' (save)", instance.key)


@receiver(post_delete, sender="dynconfig.ConfigEntry")
def invalidate_cache_on_delete(sender, instance, **kwargs):
    """Clear the cache for this key when a config entry is deleted."""
    config_cache.delete(instance.key)
    logger.debug("dynconfig: cache invalidated for '%s' (delete)", instance.key)
