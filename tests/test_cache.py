import pytest

from dynconfig import cache as config_cache
from dynconfig.models import ConfigEntry


@pytest.mark.django_db
class TestCache:
    def test_set_and_get(self):
        config_cache.set("test.key", "value", "string", False)
        result = config_cache.get("test.key")
        assert result == ("value", "string", False)

    def test_get_missing_returns_none(self):
        assert config_cache.get("missing.key") is None

    def test_delete(self):
        config_cache.set("test.key", "value", "string", False)
        config_cache.delete("test.key")
        assert config_cache.get("test.key") is None

    def test_signal_invalidates_on_save(self):
        config_cache.set("test.key", "old", "string", False)
        # Creating a ConfigEntry triggers post_save signal
        ConfigEntry.objects.create(key="test.key", value="new", value_type="string")
        assert config_cache.get("test.key") is None

    def test_signal_invalidates_on_delete(self):
        entry = ConfigEntry.objects.create(key="test.key", value="val", value_type="string")
        config_cache.set("test.key", "val", "string", False)
        entry.delete()
        assert config_cache.get("test.key") is None
