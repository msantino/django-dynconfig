"""
Exceptions for django-dynconfig.
"""


class DynConfigError(Exception):
    """Base exception for dynconfig."""


class ConfigNotFoundError(DynConfigError):
    """Raised when a config key is not found and no default is provided."""

    def __init__(self, key):
        self.key = key
        super().__init__(f"Configuration key '{key}' not found.")


class ConfigTypeError(DynConfigError):
    """Raised when a value cannot be cast to the expected type."""

    def __init__(self, key, value, value_type, original_error=None):
        self.key = key
        self.value = value
        self.value_type = value_type
        self.original_error = original_error
        super().__init__(f"Cannot cast '{key}' value to {value_type}: {original_error}")


class EncryptionError(DynConfigError):
    """Raised when encryption/decryption fails."""

    def __init__(self, message="Encryption operation failed.", original_error=None):
        self.original_error = original_error
        super().__init__(message)


class EncryptionKeyMissingError(EncryptionError):
    """Raised when an encryption key is required but not configured."""

    def __init__(self):
        super().__init__(
            "DYNCONFIG_ENCRYPTION_KEY is not set in Django settings. "
            "Set it to use encrypted configuration values."
        )
