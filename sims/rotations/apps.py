from django.apps import AppConfig
from django.db import OperationalError, ProgrammingError


class RotationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sims.rotations"
    verbose_name = "SIMS Rotations & Training"

    def ready(self):
        """
        Guard DB-dependent initialization so migrations can run without the app
        querying models before tables exist.
        """
        try:
            # Import signals or other DB-dependent initialization here.
            # Keep imports inside the try block to avoid module-level DB access.
            from . import signals  # noqa: E402
            # If there is permission/initial row creation logic, keep it here and
            # guard further DB operations similarly.
        except (OperationalError, ProgrammingError):
            # Database not ready (migrations not applied). Skip DB-dependent init.
            return