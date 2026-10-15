from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase
from django.utils import timezone

from inventory.models import Device, InstitutionalUnit

from .models import (
    BackupAttempt,
    BackupRun,
    BackupSchedule,
    ConfigComparison,
    ConfigVersion,
    RestorePlan,
)
from .services import calculate_run_status


class BackupValidationTests(SimpleTestCase):
    def setUp(self):
        unit = InstitutionalUnit(id=1, name="OTI")
        self.device = Device(id=1, name="Switch", unit=unit)
        self.other_device = Device(id=2, name="Router", unit=unit)

    def test_cron_schedule_requires_expression(self):
        schedule = BackupSchedule(frequency=BackupSchedule.Frequency.CRON)

        with self.assertRaisesMessage(
            ValidationError,
            "La frecuencia cron requiere una expresión.",
        ):
            schedule.clean()

    def test_failed_attempt_requires_error_message(self):
        attempt = BackupAttempt(
            status=BackupAttempt.Status.FAILED,
            attempt_number=1,
        )

        with self.assertRaisesMessage(
            ValidationError,
            "Un intento fallido debe registrar el motivo del error.",
        ):
            attempt.clean()

    def test_finished_run_requires_valid_start_date(self):
        now = timezone.now()
        run = BackupRun(
            trigger_type=BackupRun.TriggerType.SCHEDULED,
            started_at=now,
            finished_at=now - timedelta(minutes=1),
        )

        with self.assertRaisesMessage(
            ValidationError,
            "La fecha de finalización no puede ser anterior al inicio.",
        ):
            run.clean()

    def test_comparison_versions_must_belong_to_device(self):
        first = ConfigVersion(id=1, device=self.device)
        second = ConfigVersion(id=2, device=self.other_device)
        comparison = ConfigComparison(
            device=self.device,
            from_version=first,
            to_version=second,
        )

        with self.assertRaisesMessage(
            ValidationError,
            "Las dos versiones deben pertenecer al dispositivo seleccionado.",
        ):
            comparison.clean()

    def test_restore_version_must_belong_to_device(self):
        version = ConfigVersion(id=1, device=self.other_device)
        plan = RestorePlan(device=self.device, config_version=version)

        with self.assertRaisesMessage(
            ValidationError,
            "La versión debe pertenecer al dispositivo que se recuperará.",
        ):
            plan.clean()


class BackupRunStatusTests(SimpleTestCase):
    def test_all_success_is_success(self):
        status = calculate_run_status(
            [BackupAttempt.Status.SUCCESS, BackupAttempt.Status.SUCCESS]
        )

        self.assertEqual(status, BackupRun.Status.SUCCESS)

    def test_running_attempt_keeps_run_running(self):
        status = calculate_run_status(
            [BackupAttempt.Status.SUCCESS, BackupAttempt.Status.RUNNING]
        )

        self.assertEqual(status, BackupRun.Status.RUNNING)

    def test_terminal_mixed_results_are_partial(self):
        status = calculate_run_status(
            [BackupAttempt.Status.SUCCESS, BackupAttempt.Status.FAILED]
        )

        self.assertEqual(status, BackupRun.Status.PARTIAL)

    def test_all_failures_are_failed(self):
        status = calculate_run_status(
            [BackupAttempt.Status.FAILED, BackupAttempt.Status.SKIPPED]
        )

        self.assertEqual(status, BackupRun.Status.FAILED)
