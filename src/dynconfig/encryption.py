"""
Optional encryption support using Fernet (from the `cryptography` library).

Install with: pip install django-dynconfig[encryption]
"""

import logging

from .exceptions import EncryptionError, EncryptionKeyMissingError

logger = logging.getLogger(__name__)

_fernet_instance = None


def _get_fernet():
    """Lazily initialize and return a Fernet instance."""
    global _fernet_instance

    if _fernet_instance is not None:
        return _fernet_instance

    from . import conf

    key = conf.ENCRYPTION_KEY
    if not key:
        raise EncryptionKeyMissingError()

    try:
        from cryptography.fernet import Fernet

        _fernet_instance = Fernet(key.encode() if isinstance(key, str) else key)
        return _fernet_instance
    except ImportError:
        raise EncryptionError(
            "The 'cryptography' package is required for encryption. "
            "Install it with: pip install django-dynconfig[encryption]"
        ) from None
    except Exception as e:
        raise EncryptionError(f"Invalid encryption key: {e}", original_error=e) from e


def encrypt(value):
    """Encrypt a string value. Returns the encrypted string."""
    fernet = _get_fernet()
    try:
        return fernet.encrypt(value.encode()).decode()
    except Exception as e:
        raise EncryptionError(f"Encryption failed: {e}", original_error=e) from e


def decrypt(value):
    """Decrypt an encrypted string value. Returns the plaintext string."""
    fernet = _get_fernet()
    try:
        return fernet.decrypt(value.encode()).decode()
    except Exception as e:
        raise EncryptionError(f"Decryption failed: {e}", original_error=e) from e


def reset():
    """Reset the cached Fernet instance. Useful for testing."""
    global _fernet_instance
    _fernet_instance = None


def is_available():
    """Check if the cryptography library is installed."""
    try:
        import cryptography  # noqa: F401

        return True
    except ImportError:
        return False
