import hashlib

from django.db import transaction
from django.utils import timezone

from inventory.models import DeviceCapability, ExternalIdentifier

from .integrations import OxidizedError
from .models import BackupAttempt, BackupRun, ConfigVersion


class BackupWorkflowError(Exception):
    """Regla de negocio incumplida durante un flujo de respaldo."""


def calculate_run_status(attempt_statuses):
    statuses = list(attempt_statuses)
    if not statuses:
        return BackupRun.Status.FAILED
    if all(status == BackupAttempt.Status.SUCCESS for status in statuses):
        return BackupRun.Status.SUCCESS
    if any(
        status in {BackupAttempt.Status.PENDING, BackupAttempt.Status.RUNNING}
        for status in statuses
    ):
        return BackupRun.Status.RUNNING
    if all(
        status in {BackupAttempt.Status.FAILED, BackupAttempt.Status.SKIPPED}
        for status in statuses
    ):
        return BackupRun.Status.FAILED
    return BackupRun.Status.PARTIAL


@transaction.atomic
def create_backup_run(
    policy,
    triggered_by,
    trigger_type=BackupRun.TriggerType.MANUAL,
    simulation=False,
):
    if not simulation and not policy.is_active:
        raise BackupWorkflowError("La política de respaldo está inactiva.")

    assignments_query = policy.device_assignments.select_related("device")
    assignments = list(
        assignments_query if simulation else assignments_query.filter(enabled=True)
    )
    if not assignments:
        raise BackupWorkflowError("La política no tiene dispositivos habilitados.")

    prepared_devices = []
    for assignment in assignments:
        device = assignment.device
        if simulation:
            if not device.is_demo:
                raise BackupWorkflowError(
                    "La simulación solo puede utilizar dispositivos de demostración."
                )
            node_ref = f"demo:{device.asset_code or device.pk}"
        else:
            _validate_device_for_oxidized(device)
            node_ref = ExternalIdentifier.objects.get(
                device=device,
                system=ExternalIdentifier.ExternalSystem.OXIDIZED,
                is_active=True,
            ).external_id
        prepared_devices.append((device, node_ref))

    run = BackupRun.objects.create(
        policy=policy,
        triggered_by=triggered_by,
        trigger_type=trigger_type,
        status=BackupRun.Status.PENDING,
        summary="Simulación pendiente." if simulation else "En espera de Oxidized.",
    )
    BackupAttempt.objects.bulk_create(
        [
            BackupAttempt(
                run=run,
                device=device,
                status=BackupAttempt.Status.PENDING,
                attempt_number=1,
                oxidized_node_ref=node_ref,
            )
            for device, node_ref in prepared_devices
        ]
    )
    return run


def queue_backup_run(run, client):
    if run.status != BackupRun.Status.PENDING:
        raise BackupWorkflowError("Solo se puede enviar una ejecución pendiente.")

    run.status = BackupRun.Status.RUNNING
    run.started_at = timezone.now()
    run.summary = "Solicitudes enviadas a la cola de Oxidized."
    run.save(update_fields=["status", "started_at", "summary"])

    for attempt in run.attempts.filter(status=BackupAttempt.Status.PENDING):
        attempt.status = BackupAttempt.Status.RUNNING
        attempt.started_at = timezone.now()
        attempt.save(update_fields=["status", "started_at"])
        try:
            client.queue_node(attempt.oxidized_node_ref)
        except OxidizedError as error:
            attempt.status = BackupAttempt.Status.FAILED
            attempt.finished_at = timezone.now()
            attempt.error_code = "oxidized_request_failed"
            attempt.error_message = str(error)
            attempt.save(
                update_fields=[
                    "status",
                    "finished_at",
                    "error_code",
                    "error_message",
                ]
            )

    _refresh_run_status(run)
    return run


@transaction.atomic
def simulate_backup_run(run):
    if run.status != BackupRun.Status.PENDING:
        raise BackupWorkflowError("Solo se puede simular una ejecución pendiente.")

    attempts = list(run.attempts.select_related("device"))
    if not attempts or any(not attempt.device.is_demo for attempt in attempts):
        raise BackupWorkflowError(
            "La simulación requiere intentos asociados únicamente a dispositivos demo."
        )

    started_at = timezone.now()
    run.status = BackupRun.Status.RUNNING
    run.started_at = started_at
    run.save(update_fields=["status", "started_at"])

    for attempt in attempts:
        content_description = (
            "Configuración simulada para "
            f"{attempt.device.hostname or attempt.device.name}"
        )
        external_ref = f"demo:run-{run.pk}:device-{attempt.device_id}"
        checksum = hashlib.sha256(content_description.encode("utf-8")).hexdigest()
        collected_at = timezone.now()
        ConfigVersion.objects.update_or_create(
            device=attempt.device,
            source=ConfigVersion.Source.DEMO,
            external_ref=external_ref,
            defaults={
                "collected_at": collected_at,
                "checksum": checksum,
                "size_bytes": len(content_description.encode("utf-8")),
                "created_by": run.triggered_by,
                "notes": (
                    "Versión ficticia generada para probar el flujo; no contiene "
                    "una configuración real."
                ),
            },
        )
        attempt.status = BackupAttempt.Status.SUCCESS
        attempt.started_at = started_at
        attempt.finished_at = collected_at
        attempt.oxidized_version_ref = external_ref
        attempt.error_code = ""
        attempt.error_message = ""
        attempt.save(
            update_fields=[
                "status",
                "started_at",
                "finished_at",
                "oxidized_version_ref",
                "error_code",
                "error_message",
            ]
        )

    run.status = BackupRun.Status.SUCCESS
    run.finished_at = timezone.now()
    run.summary = (
        "Simulación exitosa. No se contactó a Oxidized ni a dispositivos reales."
    )
    run.save(update_fields=["status", "finished_at", "summary"])
    return run


def _validate_device_for_oxidized(device):
    supports_backup = DeviceCapability.objects.filter(
        device=device,
        capability=DeviceCapability.Capability.OXIDIZED_BACKUP,
        status=DeviceCapability.SupportStatus.SUPPORTED,
    ).exists()
    if not supports_backup:
        raise BackupWorkflowError(
            f"{device} no tiene respaldo Oxidized confirmado como soportado."
        )

    identifiers = ExternalIdentifier.objects.filter(
        device=device,
        system=ExternalIdentifier.ExternalSystem.OXIDIZED,
        is_active=True,
    )
    if identifiers.count() != 1:
        raise BackupWorkflowError(
            f"{device} debe tener exactamente un identificador Oxidized activo."
        )


def _refresh_run_status(run):
    status = calculate_run_status(run.attempts.values_list("status", flat=True))
    run.status = status
    update_fields = ["status"]
    if status in {
        BackupRun.Status.SUCCESS,
        BackupRun.Status.PARTIAL,
        BackupRun.Status.FAILED,
    }:
        run.finished_at = timezone.now()
        update_fields.append("finished_at")
    run.save(update_fields=update_fields)
