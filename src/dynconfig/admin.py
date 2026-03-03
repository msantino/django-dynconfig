from django.contrib import admin
from django.utils.html import mark_safe

from .models import ConfigEntry


@admin.register(ConfigEntry)
class ConfigEntryAdmin(admin.ModelAdmin):
    list_display = ["key", "display_value", "value_type", "group", "is_encrypted", "updated_at"]
    list_display_links = ["key"]
    list_filter = ["group", "value_type", "is_encrypted"]
    search_fields = ["key", "help_text_field", "group"]
    readonly_fields = ["created_at", "updated_at"]
    list_per_page = 50
    save_on_top = True

    fieldsets = (
        (None, {
            "fields": ("key", "value", "value_type"),
        }),
        ("Organization", {
            "fields": ("group", "help_text_field"),
        }),
        ("Security", {
            "fields": ("is_encrypted",),
            "description": "Encrypted values require DYNCONFIG_ENCRYPTION_KEY in Django settings.",
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at"),
        }),
    )

    def display_value(self, obj):
        """Show masked value for encrypted entries, truncated value for long text."""
        if obj.is_encrypted:
            return mark_safe('<span style="color: #999;">••••••••</span>')  # noqa: S308
        value = obj.value
        if len(value) > 80:
            return f"{value[:80]}…"
        return value

    display_value.short_description = "Value"

    def get_readonly_fields(self, request, obj=None):
        """Make key read-only on edit (prevent accidental renames)."""
        if obj:
            return [*self.readonly_fields, "key"]
        return self.readonly_fields
