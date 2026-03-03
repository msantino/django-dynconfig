from django.db import models


class ValueType(models.TextChoices):
    STRING = "string", "String"
    TEXT = "text", "Text"
    INTEGER = "integer", "Integer"
    FLOAT = "float", "Float"
    BOOLEAN = "boolean", "Boolean"
    JSON = "json", "JSON"
    LIST = "list", "List (comma-separated)"


class ConfigEntry(models.Model):
    """A single configuration key-value pair stored in the database."""

    key = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="Unique identifier. Use dotted notation for namespacing (e.g. 'asaas.api_key').",
    )
    value = models.TextField(
        blank=True,
        default="",
        help_text="The configuration value. Encrypted values are stored as ciphertext.",
    )
    value_type = models.CharField(
        max_length=20,
        choices=ValueType.choices,
        default=ValueType.STRING,
        help_text="Determines how the value is cast when retrieved.",
    )

    is_encrypted = models.BooleanField(
        default=False,
        help_text="If True, the value is encrypted at rest. Requires DYNCONFIG_ENCRYPTION_KEY.",
    )

    group = models.CharField(
        max_length=100,
        blank=True,
        default="general",
        db_index=True,
        help_text="Logical grouping for organization in the admin (e.g. 'billing', 'notifications').",
    )
    help_text_field = models.CharField(
        "description",
        max_length=500,
        blank=True,
        default="",
        help_text="Human-readable description shown in the admin.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["group", "key"]
        verbose_name = "Configuration"
        verbose_name_plural = "Configurations"

    def __str__(self):
        return f"[{self.group}] {self.key}"
