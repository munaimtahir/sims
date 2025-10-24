from django.apps import AppConfig
from django.db import OperationalError, ProgrammingError


class LogbookConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sims.logbook"

    def ready(self):
        try:
            from . import signals  # noqa: E402
        except (OperationalError, ProgrammingError):
            return