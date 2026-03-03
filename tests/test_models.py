import pytest
from django.db import IntegrityError

from dynconfig.models import ConfigEntry


@pytest.mark.django_db
class TestConfigEntry:
    def test_create_basic_entry(self):
        entry = ConfigEntry.objects.create(key="site.name", value="My Site")
        assert entry.key == "site.name"
        assert entry.value == "My Site"
        assert entry.value_type == "string"
        assert entry.group == "general"
        assert entry.is_encrypted is False

    def test_unique_key_constraint(self, config_entry):
        with pytest.raises(IntegrityError):
            ConfigEntry.objects.create(key="test.setting", value="duplicate")

    def test_str_representation(self, config_entry):
        assert str(config_entry) == "[test] test.setting"

    def test_ordering(self, config_entries):
        keys = list(ConfigEntry.objects.values_list("key", flat=True))
        assert keys == sorted(keys)  # Sorted by group, then key

    def test_default_values(self):
        entry = ConfigEntry(key="minimal")
        assert entry.value == ""
        assert entry.value_type == "string"
        assert entry.group == "general"
        assert entry.is_encrypted is False
        assert entry.help_text_field == ""

    def test_timestamps_set_on_create(self, config_entry):
        assert config_entry.created_at is not None
        assert config_entry.updated_at is not None
