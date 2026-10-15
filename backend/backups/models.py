from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from inventory.models import Device, DeviceCapability, TimeStampedModel


class BackupPolicy(TimeStampedModel):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    default_retry_count = models.PositiveSmallIntegerField(default=2)
    default_timeout_seconds = models.PositiveIntegerField(default=120)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_backup_policies",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "política de respaldo"
        verbose_name_plural = "políticas de respaldo"
        indexes = [models.Index(fields=["is_active"])]

    def __str__(self):
        return self.name


class BackupPolicyDevice(TimeStampedModel):
    policy = models.ForeignKey(
        BackupPolicy,
        on_delete=models.CASCADE,
        related_name="device_assignments",
    )
    device = models.ForeignKey(
        Device,
        on_delete=models.PROTECT,
        related_name="backup_policy_assignments",
    )
    enabled = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["policy__name", "device__name"]
        verbose_name = "dispositivo de política de respaldo"
        verbose_name_plural = "dispositivos de políticas de respaldo"
        constraints = [
            models.UniqueConstraint(
                fields=["policy", "device"],
                name="backups_policy_device_unique",
            )
        ]
        indexes = [models.Index(fields=["enabled"])]

    def __str__(self):
        return f"{self.policy} - {self.device}"

    def clean(self):
        super().clean()
        if not self.enabled or not self.device_id:
            return

        supports_backup = DeviceCapability.objects.filter(
            device_id=self.device_id,
            capability=DeviceCapability.Capability.OXIDIZED_BACKUP,
            status=DeviceCapability.SupportStatus.SUPPORTED,
        ).exists()
        if not supports_backup:
            raise ValidationError(
                {
                    "device": (
                        "El dispositivo debe tener la capacidad de respaldo Oxidized "
                        "marcada como soportada antes de habilitarlo."
                    )
                }
            )


class BackupSchedule(TimeStampedModel):
    class Frequency(models.TextChoices):
        MANUAL = "manual", "Manual"
        DAILY = "daily", "Diaria"
        WEEKLY = "weekly", "Semanal"
        MONTHLY = "monthly", "Mensual"
        CRON = "cron", "Expresión cron"

    policy = models.ForeignKey(
        BackupPolicy,
        on_delete=models.CASCADE,
        related_name="schedules",
    )
    frequency = models.CharField(max_length=20, choices=Frequency.choices)
    cron_expression = models.CharField(max_length=100, blank=True)
    timezone = models.CharField(max_length=50, default="America/Lima")
    next_run_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["policy__name", "frequency"]
        verbose_name = "programación de respaldo"
        verbose_name_plural = "programaciones de respaldo"
        indexes = [
            models.Index(fields=["is_active", "next_run_at"]),
            models.Index(fields=["policy", "frequency"]),
        ]

    def __str__(self):
        return f"{self.policy} - {self.get_frequency_display()}"

    def clean(self):
        super().clean()
        if self.frequency == self.Frequency.CRON and not self.cron_expression.strip():
            raise ValidationError(
                {"cron_expression": "La frecuencia cron requiere una expresión."}
            )
        if self.frequency == self.Frequency.MANUAL and self.next_run_at:
            raise ValidationError(
                {"next_run_at": "Una programación manual no debe tener próxima ejecución."}
            )


class BackupRun(models.Model):
    class TriggerType(models.TextChoices):
        MANUAL = "manual", "Manual"
        SCHEDULED = "scheduled", "Programada"
        RETRY = "retry", "Reintento"
        EXTERNAL = "external", "Externa"

    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        RUNNING = "running", "En ejecución"
        SUCCESS = "success", "Exitosa"
        PARTIAL = "partial", "Parcial"
        FAILED = "failed", "Fallida"
        CANCELED = "canceled", "Cancelada"

    policy = models.ForeignKey(
        BackupPolicy,
        on_delete=models.PROTECT,
        related_name="runs",
    )
    triggered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="triggered_backup_runs",
    )
    trigger_type = models.CharField(max_length=20, choices=TriggerType.choices)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    started_at = models.DateTimeField(blank=True, null=True)
    finished_at = models.DateTimeField(blank=True, null=True)
    summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "ejecución de respaldo"
        verbose_name_plural = "ejecuciones de respaldo"
        permissions = [
            ("execute_backuprun", "Puede ejecutar respaldos"),
        ]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["policy", "created_at"]),
        ]

    def __str__(self):
        return f"Ejecución {self.pk or 'nueva'} - {self.policy}"

    def clean(self):
        super().clean()
        errors = {}
        if self.trigger_type == self.TriggerType.MANUAL and not self.triggered_by_id:
            errors["triggered_by"] = (
                "Una ejecución manual debe registrar al usuario que la inició."
            )
        if self.finished_at and not self.started_at:
            errors["started_at"] = (
                "Una ejecución finalizada debe tener fecha de inicio."
            )
        elif self.started_at and self.finished_at and self.finished_at < self.started_at:
            errors["finished_at"] = (
                "La fecha de finalización no puede ser anterior al inicio."
            )
        if errors:
            raise ValidationError(errors)


class BackupAttempt(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        RUNNING = "running", "En ejecución"
        SUCCESS = "success", "Exitoso"
        FAILED = "failed", "Fallido"
        SKIPPED = "skipped", "Omitido"

    run = models.ForeignKey(
        BackupRun,
        on_delete=models.CASCADE,
        related_name="attempts",
    )
    device = models.ForeignKey(
        Device,
        on_delete=models.PROTECT,
        related_name="backup_attempts",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    attempt_number = models.PositiveSmallIntegerField(default=1)
    started_at = models.DateTimeField(blank=True, null=True)
    finished_at = models.DateTimeField(blank=True, null=True)
    error_code = models.CharField(max_length=80, blank=True)
    error_message = models.TextField(blank=True)
    oxidized_node_ref = models.CharField(max_length=255, blank=True)
    oxidized_version_ref = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["run", "device__name", "attempt_number"]
        verbose_name = "intento de respaldo"
        verbose_name_plural = "intentos de respaldo"
        constraints = [
            models.UniqueConstraint(
                fields=["run", "device", "attempt_number"],
                name="backups_run_device_attempt_unique",
            )
        ]
        indexes = [
            models.Index(fields=["device", "status"]),
            models.Index(fields=["run", "status"]),
        ]

    def __str__(self):
        return f"{self.run} - {self.device} - intento {self.attempt_number}"

    def clean(self):
        super().clean()
        errors = {}
        if self.attempt_number < 1:
            errors["attempt_number"] = "El número de intento debe ser mayor que cero."
        if self.finished_at and not self.started_at:
            errors["started_at"] = "Un intento finalizado debe tener fecha de inicio."
        elif self.started_at and self.finished_at and self.finished_at < self.started_at:
            errors["finished_at"] = (
                "La fecha de finalización no puede ser anterior al inicio."
            )
        if self.status == self.Status.FAILED and not self.error_message.strip():
            errors["error_message"] = (
                "Un intento fallido debe registrar el motivo del error."
            )
        if errors:
            raise ValidationError(errors)


class ConfigVersion(models.Model):
    class Source(models.TextChoices):
        OXIDIZED = "oxidized", "Oxidized"
        MANUAL_IMPORT = "manual_import", "Importación manual"
        DEMO = "demo", "Demostración"

    device = models.ForeignKey(
        Device,
        on_delete=models.PROTECT,
        related_name="config_versions",
    )
    source = models.CharField(max_length=20, choices=Source.choices)
    external_ref = models.CharField(max_length=255)
    collected_at = models.DateTimeField()
    checksum = models.CharField(max_length=128, blank=True)
    size_bytes = models.PositiveBigIntegerField(blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="registered_config_versions",
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-collected_at"]
        verbose_name = "versión de configuración"
        verbose_name_plural = "versiones de configuración"
        constraints = [
            models.UniqueConstraint(
                fields=["device", "source", "external_ref"],
                name="backups_device_source_external_ref_unique",
            )
        ]
        indexes = [
            models.Index(fields=["device", "collected_at"]),
            models.Index(fields=["source", "collected_at"]),
        ]

    def __str__(self):
        return f"{self.device} - {self.collected_at:%Y-%m-%d %H:%M}"


class ConfigComparison(models.Model):
    device = models.ForeignKey(
        Device,
        on_delete=models.PROTECT,
        related_name="config_comparisons",
    )
    from_version = models.ForeignKey(
        ConfigVersion,
        on_delete=models.PROTECT,
        related_name="comparisons_as_origin",
    )
    to_version = models.ForeignKey(
        ConfigVersion,
        on_delete=models.PROTECT,
        related_name="comparisons_as_destination",
    )
    change_summary = models.TextField(blank=True)
    diff_external_ref = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_config_comparisons",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "comparación de configuraciones"
        verbose_name_plural = "comparaciones de configuraciones"
        indexes = [models.Index(fields=["device", "created_at"])]

    def __str__(self):
        return f"Comparación de {self.device} ({self.pk or 'nueva'})"

    def clean(self):
        super().clean()
        errors = {}
        if self.from_version_id and self.to_version_id:
            if self.from_version_id == self.to_version_id:
                errors["to_version"] = "Debe seleccionar dos versiones diferentes."
            if self.device_id and (
                self.from_version.device_id != self.device_id
                or self.to_version.device_id != self.device_id
            ):
                errors["device"] = (
                    "Las dos versiones deben pertenecer al dispositivo seleccionado."
                )
        if errors:
            raise ValidationError(errors)


class RestorePlan(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Borrador"
        PENDING_APPROVAL = "pending_approval", "Pendiente de aprobación"
        APPROVED = "approved", "Aprobado"
        EXECUTED = "executed", "Ejecutado"
        CANCELED = "canceled", "Cancelado"
        REJECTED = "rejected", "Rechazado"

    device = models.ForeignKey(
        Device,
        on_delete=models.PROTECT,
        related_name="restore_plans",
    )
    config_version = models.ForeignKey(
        ConfigVersion,
        on_delete=models.PROTECT,
        related_name="restore_plans",
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="requested_restore_plans",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="approved_restore_plans",
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    executed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "plan de recuperación"
        verbose_name_plural = "planes de recuperación"
        permissions = [
            ("approve_restoreplan", "Puede aprobar planes de recuperación"),
            (
                "execute_restoreplan",
                "Puede registrar una recuperación como ejecutada",
            ),
        ]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["device", "created_at"]),
        ]

    def __str__(self):
        return f"Recuperación de {self.device} ({self.get_status_display()})"

    def clean(self):
        super().clean()
        errors = {}
        if (
            self.device_id
            and self.config_version_id
            and self.config_version.device_id != self.device_id
        ):
            errors["config_version"] = (
                "La versión debe pertenecer al dispositivo que se recuperará."
            )
        if self.status in {self.Status.APPROVED, self.Status.EXECUTED}:
            if not self.approved_by_id:
                errors["approved_by"] = (
                    "Un plan aprobado debe registrar quién lo autorizó."
                )
            if not self.approved_at:
                errors["approved_at"] = (
                    "Un plan aprobado debe registrar la fecha de aprobación."
                )
        if self.status == self.Status.EXECUTED and not self.executed_at:
            errors["executed_at"] = (
                "Un plan ejecutado debe registrar la fecha de ejecución."
            )
        if errors:
            raise ValidationError(errors)
