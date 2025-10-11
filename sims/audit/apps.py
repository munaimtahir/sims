from django.apps import AppConfig


class AuditConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sims.audit"
    verbose_name = "Audit Trail"

    def ready(self):
        from . import signals  # noqa: F401
