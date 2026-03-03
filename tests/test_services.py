import pytest

from dynconfig import get_config, get_configs_by_group, set_config
from dynconfig.exceptions import ConfigNotFoundError
from dynconfig.models import ConfigEntry


@pytest.mark.django_db
class TestGetConfig:
    def test_basic_get(self, config_entry):
        assert get_config("test.setting") == "hello"

    def test_returns_default_when_missing(self):
        assert get_config("nonexistent", default="fallback") == "fallback"

    def test_returns_none_when_missing_no_default(self):
        assert get_config("nonexistent") is None

    def test_raises_when_configured(self, settings):
        settings.DYNCONFIG_RAISE_NOT_FOUND = True
        with pytest.raises(ConfigNotFoundError):
            get_config("nonexistent")

    def test_typed_integer(self, config_entries):
        assert get_config("app.max_retries") == 5
        assert isinstance(get_config("app.max_retries"), int)

    def test_typed_boolean(self, config_entries):
        assert get_config("app.debug") is True

    def test_typed_float(self, config_entries):
        assert get_config("app.rate_limit") == 1.5

    def test_typed_list(self, config_entries):
        assert get_config("app.tags") == ["web", "api", "backend"]

    def test_typed_json(self, config_entries):
        assert get_config("app.metadata") == {"env": "staging"}

    def test_uses_cache_on_second_call(self, config_entry):
        # First call hits DB
        assert get_config("test.setting") == "hello"
        # Modify DB directly (bypass signals by using update)
        ConfigEntry.objects.filter(key="test.setting").update(value="changed")
        # Second call should still return cached value
        assert get_config("test.setting") == "hello"


@pytest.mark.django_db
class TestSetConfig:
    def test_create_new(self):
        set_config("new.key", "new_value")
        assert ConfigEntry.objects.filter(key="new.key").exists()
        assert get_config("new.key") == "new_value"

    def test_update_existing(self, config_entry):
        set_config("test.setting", "updated")
        assert get_config("test.setting") == "updated"

    def test_auto_detect_integer(self):
        entry = set_config("auto.int", 42)
        assert entry.value_type == "integer"
        assert get_config("auto.int") == 42

    def test_auto_detect_boolean(self):
        entry = set_config("auto.bool", True)
        assert entry.value_type == "boolean"
        assert get_config("auto.bool") is True

    def test_auto_detect_float(self):
        entry = set_config("auto.float", 3.14)
        assert entry.value_type == "float"

    def test_auto_detect_json(self):
        entry = set_config("auto.json", {"key": "value"})
        assert entry.value_type == "json"
        assert get_config("auto.json") == {"key": "value"}

    def test_set_with_group(self):
        set_config("billing.key", "val", group="billing")
        entry = ConfigEntry.objects.get(key="billing.key")
        assert entry.group == "billing"

    def test_set_with_help_text(self):
        set_config("documented.key", "val", help_text="This is documented")
        entry = ConfigEntry.objects.get(key="documented.key")
        assert entry.help_text_field == "This is documented"

    def test_returns_entry(self):
        entry = set_config("ret.key", "val")
        assert isinstance(entry, ConfigEntry)


@pytest.mark.django_db
class TestGetConfigsByGroup:
    def test_returns_group_dict(self, config_entries):
        result = get_configs_by_group("app")
        assert "app.name" in result
        assert result["app.name"] == "MyApp"
        assert result["app.debug"] is True
        assert result["app.max_retries"] == 5

    def test_empty_group_returns_empty_dict(self):
        assert get_configs_by_group("nonexistent") == {}
