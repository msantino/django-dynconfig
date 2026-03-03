import pytest
from django.contrib.admin.sites import AdminSite

from dynconfig.admin import ConfigEntryAdmin
from dynconfig.models import ConfigEntry


@pytest.mark.django_db
class TestConfigEntryAdmin:
    def setup_method(self):
        self.site = AdminSite()
        self.admin = ConfigEntryAdmin(ConfigEntry, self.site)

    def test_display_value_normal(self):
        entry = ConfigEntry(key="test", value="visible", is_encrypted=False)
        assert self.admin.display_value(entry) == "visible"

    def test_display_value_encrypted(self):
        entry = ConfigEntry(key="test", value="encrypted_blob", is_encrypted=True)
        result = self.admin.display_value(entry)
        assert "••••••••" in result

    def test_display_value_long_truncated(self):
        entry = ConfigEntry(key="test", value="x" * 200, is_encrypted=False)
        result = self.admin.display_value(entry)
        assert len(result) < 200
        assert result.endswith("…")

    def test_key_readonly_on_edit(self):
        entry = ConfigEntry(key="test", value="val")
        readonly = self.admin.get_readonly_fields(None, obj=entry)
        assert "key" in readonly

    def test_key_editable_on_create(self):
        readonly = self.admin.get_readonly_fields(None, obj=None)
        assert "key" not in readonly
