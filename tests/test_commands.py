import json
import tempfile

import pytest
from django.core.management import call_command

from dynconfig.models import ConfigEntry


@pytest.mark.django_db
class TestExportConfigs:
    def test_export_to_file(self, config_entries):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            call_command("exportconfigs", output=f.name)
            f.seek(0)
            with open(f.name) as rf:
                data = json.load(rf)
        assert len(data) == 6
        keys = [entry["key"] for entry in data]
        assert "app.name" in keys

    def test_export_by_group(self, config_entries):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            call_command("exportconfigs", output=f.name, group="app")
            with open(f.name) as rf:
                data = json.load(rf)
        assert all(entry["group"] == "app" for entry in data)

    def test_export_no_secrets(self, db):
        ConfigEntry.objects.create(key="public", value="visible", is_encrypted=False)
        ConfigEntry.objects.create(key="secret", value="hidden", is_encrypted=True)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            call_command("exportconfigs", output=f.name, no_secrets=True)
            with open(f.name) as rf:
                data = json.load(rf)
        assert len(data) == 1
        assert data[0]["key"] == "public"


@pytest.mark.django_db
class TestImportConfigs:
    def test_import_creates_entries(self):
        data = [
            {"key": "imported.one", "value": "val1", "value_type": "string", "group": "import"},
            {"key": "imported.two", "value": "42", "value_type": "integer", "group": "import"},
        ]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            f.flush()
            call_command("importconfigs", f.name)
        assert ConfigEntry.objects.filter(key="imported.one").exists()
        assert ConfigEntry.objects.filter(key="imported.two").exists()

    def test_import_skips_existing(self, config_entry):
        data = [{"key": "test.setting", "value": "overwrite_attempt"}]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            f.flush()
            call_command("importconfigs", f.name)
        # Value should NOT be overwritten
        entry = ConfigEntry.objects.get(key="test.setting")
        assert entry.value == "hello"

    def test_import_overwrite(self, config_entry):
        data = [{"key": "test.setting", "value": "new_value"}]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            f.flush()
            call_command("importconfigs", f.name, overwrite=True)
        entry = ConfigEntry.objects.get(key="test.setting")
        assert entry.value == "new_value"

    def test_dry_run(self):
        data = [{"key": "dryrun.key", "value": "val"}]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            f.flush()
            call_command("importconfigs", f.name, dry_run=True)
        assert not ConfigEntry.objects.filter(key="dryrun.key").exists()
