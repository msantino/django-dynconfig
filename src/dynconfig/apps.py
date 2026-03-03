from django.apps import AppConfig


class DynConfigConfig(AppConfig):
    name = "dynconfig"
    verbose_name = "Dynamic Configuration"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        from . import signals  # noqa: F401
