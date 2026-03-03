import pytest

from dynconfig import encryption, get_config, set_config
from dynconfig.exceptions import EncryptionKeyMissingError
from dynconfig.models import ConfigEntry

# Only run encryption tests if cryptography is installed
cryptography = pytest.importorskip("cryptography")

from cryptography.fernet import Fernet  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_encryption():
    """Reset encryption state before and after each test."""
    encryption.reset()
    yield
    encryption.reset()


@pytest.fixture
def encryption_key():
    """Generate a valid Fernet key for testing."""
    return Fernet.generate_key().decode()


@pytest.fixture
def with_encryption(settings, encryption_key):
    """Configure encryption for the test."""
    settings.DYNCONFIG_ENCRYPTION_KEY = encryption_key
    encryption.reset()
    yield encryption_key


class TestEncryption:
    def test_encrypt_decrypt_roundtrip(self, with_encryption):
        original = "super-secret-api-key"
        encrypted = encryption.encrypt(original)
        assert encrypted != original
        assert encryption.decrypt(encrypted) == original

    def test_raises_without_key(self, settings):
        settings.DYNCONFIG_ENCRYPTION_KEY = None
        encryption.reset()
        with pytest.raises(EncryptionKeyMissingError):
            encryption.encrypt("test")

    def test_is_available(self):
        assert encryption.is_available() is True


@pytest.mark.django_db
class TestEncryptedConfig:
    def test_set_and_get_encrypted(self, with_encryption):
        set_config("secret.key", "my-secret", is_encrypted=True, group="secrets")

        # Raw DB value should be encrypted
        entry = ConfigEntry.objects.get(key="secret.key")
        assert entry.value != "my-secret"
        assert entry.is_encrypted is True

        # get_config should decrypt transparently
        assert get_config("secret.key") == "my-secret"

    def test_update_encrypted_value(self, with_encryption):
        set_config("secret.key", "original", is_encrypted=True)
        set_config("secret.key", "updated", is_encrypted=True)
        assert get_config("secret.key") == "updated"
