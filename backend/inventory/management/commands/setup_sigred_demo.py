from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from backups.models import BackupPolicy, BackupPolicyDevice, BackupSchedule
from inventory.models import (
    Device,
    DeviceCapability,
    DeviceModel,
    InstitutionalUnit,
    Location,
    Vendor,
)


ROLE_PERMISSION_RULES = {
    "Administradores SIGRED": {
        "inventory": {"add", "change", "delete", "view"},
        "backups": {"add", "change", "delete", "view"},
    },
    "Gestores de inventario": {
        "inventory": {"add", "change", "view"},
    },
    "Gestores de respaldos": {
        "inventory": {"view"},
        "backups": {"add", "change", "view"},
    },
    "Gestores de monitoreo": {
        "inventory": {"view"},
    },
    "Consulta SIGRED": {
        "inventory": {"view"},
        "backups": {"view"},
    },
}

ROLE_EXTRA_PERMISSIONS = {
    "Administradores SIGRED": {
        "execute_backuprun",
        "approve_restoreplan",
        "execute_restoreplan",
    },
    "Gestores de respaldos": {"execute_backuprun"},
}


class Command(BaseCommand):
    help = "Crea roles iniciales y un inventario de demostracion sin borrar datos."

    @transaction.atomic
    def handle(self, *args, **options):
        self._create_roles()
        self._create_demo_inventory()
        self.stdout.write(self.style.SUCCESS("Configuracion inicial de SIGRED lista."))

    def _create_roles(self):
        managed_apps = {"inventory", "backups"}
        managed_permissions = Permission.objects.filter(
            content_type__app_label__in=managed_apps
        )

        for role_name, app_rules in ROLE_PERMISSION_RULES.items():
            group, _ = Group.objects.get_or_create(name=role_name)
            permissions = [
                permission
                for permission in managed_permissions
                if (
                    permission.codename.split("_", 1)[0]
                    in app_rules.get(permission.content_type.app_label, set())
                    or permission.codename
                    in ROLE_EXTRA_PERMISSIONS.get(role_name, set())
                )
            ]
            group.permissions.set(permissions)
            self.stdout.write(f"Rol preparado: {role_name}")

    def _create_demo_inventory(self):
        unit, _ = InstitutionalUnit.objects.update_or_create(
            code="DEMO-OTI",
            defaults={
                "name": "[DEMO] Oficina de Tecnologia de la Informacion",
                "unit_type": InstitutionalUnit.UnitType.OTI,
                "is_active": True,
            },
        )
        location, _ = Location.objects.update_or_create(
            unit=unit,
            name="[DEMO] Sala de comunicaciones",
            defaults={
                "location_type": Location.LocationType.ROOM,
                "description": "Ubicacion ficticia para desarrollo y pruebas.",
                "is_active": True,
            },
        )
        vendor, _ = Vendor.objects.update_or_create(
            name="[DEMO] Cisco",
            defaults={"is_active": True},
        )
        device_model, _ = DeviceModel.objects.update_or_create(
            vendor=vendor,
            name="Catalyst 2960 (DEMO)",
            defaults={
                "device_family": "Catalyst",
                "device_type": DeviceModel.DeviceType.SWITCH,
                "notes": "Modelo ficticio para validar las pantallas de SIGRED.",
                "is_active": True,
            },
        )
        device, _ = Device.objects.update_or_create(
            asset_code="DEMO-SW-001",
            defaults={
                "name": "[DEMO] Switch principal OTI",
                "hostname": "demo-sw-oti-01",
                "management_ip": "192.0.2.10",
                "serial_number": "DEMO-SERIAL-001",
                "unit": unit,
                "location": location,
                "vendor": vendor,
                "model": device_model,
                "device_type": DeviceModel.DeviceType.SWITCH,
                "status": Device.Status.ACTIVE,
                "criticality": Device.Criticality.HIGH,
                "description": "Dispositivo ficticio; no representa un equipo real.",
                "is_demo": True,
            },
        )

        capabilities = {
            DeviceCapability.Capability.SSH: DeviceCapability.SupportStatus.SUPPORTED,
            DeviceCapability.Capability.SNMP: DeviceCapability.SupportStatus.PENDING_TEST,
            DeviceCapability.Capability.OXIDIZED_BACKUP: (
                DeviceCapability.SupportStatus.PENDING_TEST
            ),
            DeviceCapability.Capability.ZABBIX_MONITORING: (
                DeviceCapability.SupportStatus.PENDING_TEST
            ),
        }
        for capability, status in capabilities.items():
            DeviceCapability.objects.update_or_create(
                device=device,
                capability=capability,
                defaults={
                    "status": status,
                    "source": DeviceCapability.Source.MANUAL,
                    "notes": "Dato de demostracion pendiente de validacion real.",
                },
            )

        self.stdout.write("Inventario de demostracion preparado: DEMO-SW-001")
        self._create_demo_backup_policy(device)

    def _create_demo_backup_policy(self, device):
        user = get_user_model().objects.filter(is_superuser=True).order_by("pk").first()
        if not user:
            self.stdout.write(
                self.style.WARNING(
                    "No se creó la política demo porque no existe un superusuario."
                )
            )
            return

        policy, _ = BackupPolicy.objects.update_or_create(
            name="[DEMO] Respaldo semanal OTI",
            defaults={
                "description": (
                    "Política ficticia e inactiva hasta conectar y validar Oxidized."
                ),
                "is_active": False,
                "default_retry_count": 2,
                "default_timeout_seconds": 120,
                "created_by": user,
            },
        )
        BackupPolicyDevice.objects.update_or_create(
            policy=policy,
            device=device,
            defaults={
                "enabled": False,
                "notes": (
                    "Asignación demo deshabilitada: falta validar Oxidized y el acceso."
                ),
            },
        )
        BackupSchedule.objects.update_or_create(
            policy=policy,
            frequency=BackupSchedule.Frequency.WEEKLY,
            defaults={
                "timezone": "America/Lima",
                "is_active": False,
            },
        )
        self.stdout.write("Política de respaldo demo preparada e inactiva.")
