from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ConfigEntry",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "key",
                    models.CharField(
                        db_index=True,
                        help_text="Unique identifier. Use dotted notation for namespacing (e.g. 'asaas.api_key').",
                        max_length=255,
                        unique=True,
                    ),
                ),
                (
                    "value",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="The configuration value. Encrypted values are stored as ciphertext.",
                    ),
                ),
                (
                    "value_type",
                    models.CharField(
                        choices=[
                            ("string", "String"),
                            ("text", "Text"),
                            ("integer", "Integer"),
                            ("float", "Float"),
                            ("boolean", "Boolean"),
                            ("json", "JSON"),
                            ("list", "List (comma-separated)"),
                        ],
                        default="string",
                        help_text="Determines how the value is cast when retrieved.",
                        max_length=20,
                    ),
                ),
                (
                    "is_encrypted",
                    models.BooleanField(
                        default=False,
                        help_text="If True, the value is encrypted at rest. Requires DYNCONFIG_ENCRYPTION_KEY.",
                    ),
                ),
                (
                    "group",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        default="general",
                        help_text="Logical grouping for organization in the admin (e.g. 'billing', 'notifications').",
                        max_length=100,
                    ),
                ),
                (
                    "help_text_field",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Human-readable description shown in the admin.",
                        max_length=500,
                        verbose_name="description",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Configuration",
                "verbose_name_plural": "Configurations",
                "ordering": ["group", "key"],
            },
        ),
    ]
