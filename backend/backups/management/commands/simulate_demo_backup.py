from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from backups.models import BackupPolicy
from backups.services import (
    BackupWorkflowError,
    create_backup_run,
    simulate_backup_run,
)


class Command(BaseCommand):
    help = "Genera un respaldo ficticio usando solo los datos demo de SIGRED."

    def handle(self, *args, **options):
        policy = BackupPolicy.objects.filter(
            name="[DEMO] Respaldo semanal OTI"
        ).first()
        if not policy:
            raise CommandError(
                "No existe la política demo. Ejecute setup_sigred_demo primero."
            )

        user = get_user_model().objects.filter(is_superuser=True).order_by("pk").first()
        if not user:
            raise CommandError("No existe un superusuario para registrar la simulación.")

        try:
            run = create_backup_run(policy, user, simulation=True)
            simulate_backup_run(run)
        except BackupWorkflowError as error:
            raise CommandError(str(error)) from error

        self.stdout.write(
            self.style.SUCCESS(
                f"Simulación {run.pk} completada sin contactar equipos reales."
            )
        )
