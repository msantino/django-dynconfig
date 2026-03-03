import pytest

from dynconfig.checks import check_encryption_key
from dynconfig.models import ConfigEntry


@pytest.mark.django_db
class TestSystemChecks:
    def test_no_warning_when_no_encrypted_entries(self, settings):
        settings.DYNCONFIG_ENCRYPTION_KEY = None
        ConfigEntry.objects.create(key="normal", value="val")
        warnings = check_encryption_key(None)
        assert len(warnings) == 0

    def test_warning_when_encrypted_entries_without_key(self, settings):
        settings.DYNCONFIG_ENCRYPTION_KEY = None
        ConfigEntry.objects.create(key="secret", value="encrypted_blob", is_encrypted=True)
        warnings = check_encryption_key(None)
        assert len(warnings) == 1
        assert warnings[0].id == "dynconfig.W001"

    def test_no_warning_when_key_is_set(self, settings):
        settings.DYNCONFIG_ENCRYPTION_KEY = "some-key"
        ConfigEntry.objects.create(key="secret", value="encrypted_blob", is_encrypted=True)
        warnings = check_encryption_key(None)
        assert len(warnings) == 0
