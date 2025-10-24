from django.apps import AppConfig
from django.db import OperationalError, ProgrammingError


class CertificatesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sims.certificates"

    def ready(self):
        try:
            # Keep imports here to avoid DB access at module import time.
            from . import signals  # noqa: E402
        except (OperationalError, ProgrammingError):
            # DB not ready yet (migrations not applied).
            return