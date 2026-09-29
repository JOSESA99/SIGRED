from django.db import models
from django.db.models import Q


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class InstitutionalUnit(TimeStampedModel):
    class UnitType(models.TextChoices):
        OTI = "oti", "OTI"
        FACULTY = "faculty", "Facultad"
        OFFICE = "office", "Oficina"
        LABORATORY = "laboratory", "Laboratorio"
        OTHER = "other", "Otro"

    name = models.CharField(max_length=150)
    code = models.CharField(max_length=50, blank=True, null=True)
    unit_type = models.CharField(
        max_length=20,
        choices=UnitType.choices,
        default=UnitType.OTHER,
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="children",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "unidad institucional"
        verbose_name_plural = "unidades institucionales"
        constraints = [
            models.UniqueConstraint(
                fields=["code"],
                condition=Q(code__isnull=False),
                name="inventory_unit_code_unique_when_present",
            ),
        ]

    def __str__(self):
        return self.name


class Location(TimeStampedModel):
    class LocationType(models.TextChoices):
        CAMPUS = "campus", "Sede"
        BUILDING = "building", "Edificio"
        FLOOR = "floor", "Piso"
        ROOM = "room", "Ambiente"
        RACK = "rack", "Rack"
        OTHER = "other", "Otro"

    unit = models.ForeignKey(
        InstitutionalUnit,
        on_delete=models.PROTECT,
        related_name="locations",
    )
    name = models.CharField(max_length=150)
    location_type = models.CharField(
        max_length=20,
        choices=LocationType.choices,
        default=LocationType.OTHER,
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="children",
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["unit__name", "name"]
        verbose_name = "ubicacion"
        verbose_name_plural = "ubicaciones"
        indexes = [
            models.Index(fields=["unit", "location_type"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.unit})"


class Vendor(models.Model):
    name = models.CharField(max_length=100, unique=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "fabricante"
        verbose_name_plural = "fabricantes"

    def __str__(self):
        return self.name


class DeviceModel(models.Model):
    class DeviceType(models.TextChoices):
        SWITCH = "switch", "Switch"
        ROUTER = "router", "Router"
        FIREWALL = "firewall", "Firewall"
        ACCESS_POINT = "access_point", "Access point"
        NETWORK_SERVER = "network_server", "Servidor de red"
        OTHER = "other", "Otro"

    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.PROTECT,
        related_name="device_models",
    )
    name = models.CharField(max_length=120)
    device_family = models.CharField(max_length=120, blank=True)
    device_type = models.CharField(
        max_length=30,
        choices=DeviceType.choices,
        default=DeviceType.OTHER,
    )
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["vendor__name", "name"]
        verbose_name = "modelo de dispositivo"
        verbose_name_plural = "modelos de dispositivo"
        constraints = [
            models.UniqueConstraint(
                fields=["vendor", "name"],
                name="inventory_device_model_vendor_name_unique",
            ),
        ]
        indexes = [
            models.Index(fields=["device_type"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.vendor} {self.name}"


class Device(TimeStampedModel):
    class Status(models.TextChoices):
        PLANNED = "planned", "Planificado"
        ACTIVE = "active", "Activo"
        MAINTENANCE = "maintenance", "En mantenimiento"
        RETIRED = "retired", "Retirado"
        UNKNOWN = "unknown", "Desconocido"

    class Criticality(models.TextChoices):
        LOW = "low", "Baja"
        MEDIUM = "medium", "Media"
        HIGH = "high", "Alta"
        CRITICAL = "critical", "Critica"

    name = models.CharField(max_length=150)
    hostname = models.CharField(max_length=150, blank=True)
    management_ip = models.GenericIPAddressField(blank=True, null=True)
    serial_number = models.CharField(max_length=120, blank=True, null=True)
    asset_code = models.CharField(max_length=80, blank=True, null=True)
    unit = models.ForeignKey(
        InstitutionalUnit,
        on_delete=models.PROTECT,
        related_name="devices",
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="devices",
    )
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="devices",
    )
    model = models.ForeignKey(
        DeviceModel,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="devices",
    )
    device_type = models.CharField(
        max_length=30,
        choices=DeviceModel.DeviceType.choices,
        default=DeviceModel.DeviceType.OTHER,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UNKNOWN,
    )
    criticality = models.CharField(
        max_length=20,
        choices=Criticality.choices,
        default=Criticality.MEDIUM,
    )
    description = models.TextField(blank=True)
    is_demo = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]
        verbose_name = "dispositivo"
        verbose_name_plural = "dispositivos"
        constraints = [
            models.UniqueConstraint(
                fields=["management_ip"],
                condition=Q(management_ip__isnull=False),
                name="inventory_device_management_ip_unique_when_present",
            ),
            models.UniqueConstraint(
                fields=["serial_number"],
                condition=Q(serial_number__isnull=False),
                name="inventory_device_serial_unique_when_present",
            ),
            models.UniqueConstraint(
                fields=["asset_code"],
                condition=Q(asset_code__isnull=False),
                name="inventory_device_asset_code_unique_when_present",
            ),
        ]
        indexes = [
            models.Index(fields=["unit", "status"]),
            models.Index(fields=["location"]),
            models.Index(fields=["device_type"]),
            models.Index(fields=["management_ip"]),
            models.Index(fields=["is_demo"]),
        ]

    def __str__(self):
        return self.name


class DeviceCapability(TimeStampedModel):
    class Capability(models.TextChoices):
        SSH = "ssh", "SSH"
        TELNET = "telnet", "Telnet"
        SNMP = "snmp", "SNMP"
        API = "api", "API"
        OXIDIZED_BACKUP = "oxidized_backup", "Respaldo Oxidized"
        ZABBIX_MONITORING = "zabbix_monitoring", "Monitoreo Zabbix"
        CONFIG_RESTORE = "config_restore", "Restauracion de configuracion"
        INTERFACE_METRICS = "interface_metrics", "Metricas de interfaces"
        OTHER = "other", "Otro"

    class SupportStatus(models.TextChoices):
        UNKNOWN = "unknown", "Desconocido"
        SUPPORTED = "supported", "Soportado"
        UNSUPPORTED = "unsupported", "No soportado"
        PENDING_TEST = "pending_test", "Pendiente de prueba"

    class Source(models.TextChoices):
        MANUAL = "manual", "Manual"
        DETECTED = "detected", "Detectado"
        IMPORTED = "imported", "Importado"

    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="capabilities",
    )
    capability = models.CharField(max_length=40, choices=Capability.choices)
    status = models.CharField(
        max_length=20,
        choices=SupportStatus.choices,
        default=SupportStatus.UNKNOWN,
    )
    source = models.CharField(
        max_length=20,
        choices=Source.choices,
        default=Source.MANUAL,
    )
    notes = models.TextField(blank=True)
    verified_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["device__name", "capability"]
        verbose_name = "capacidad de dispositivo"
        verbose_name_plural = "capacidades de dispositivo"
        constraints = [
            models.UniqueConstraint(
                fields=["device", "capability"],
                name="inventory_device_capability_unique",
            ),
        ]
        indexes = [
            models.Index(fields=["capability", "status"]),
            models.Index(fields=["verified_at"]),
        ]

    def __str__(self):
        return f"{self.device} - {self.get_capability_display()}"


class ExternalIdentifier(TimeStampedModel):
    class ExternalSystem(models.TextChoices):
        OXIDIZED = "oxidized", "Oxidized"
        ZABBIX = "zabbix", "Zabbix"
        INSTITUTIONAL_INVENTORY = (
            "institutional_inventory",
            "Inventario institucional",
        )
        OTHER = "other", "Otro"

    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="external_identifiers",
    )
    system = models.CharField(max_length=40, choices=ExternalSystem.choices)
    external_id = models.CharField(max_length=150)
    external_name = models.CharField(max_length=150, blank=True)
    url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    last_verified_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["system", "external_id"]
        verbose_name = "identificador externo"
        verbose_name_plural = "identificadores externos"
        constraints = [
            models.UniqueConstraint(
                fields=["system", "external_id"],
                name="inventory_external_system_id_unique",
            ),
            models.UniqueConstraint(
                fields=["device", "system", "external_id"],
                name="inventory_device_external_id_unique",
            ),
        ]
        indexes = [
            models.Index(fields=["device", "system"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.get_system_display()}: {self.external_id}"


class CredentialProfile(TimeStampedModel):
    class Purpose(models.TextChoices):
        BACKUP = "backup", "Respaldos"
        MONITORING = "monitoring", "Monitoreo"
        ADMIN = "admin", "Administracion"
        API = "api", "API"

    class AuthType(models.TextChoices):
        SSH_PASSWORD = "ssh_password", "SSH con password"
        SSH_KEY = "ssh_key", "SSH con llave"
        SNMP_V2 = "snmp_v2", "SNMP v2"
        SNMP_V3 = "snmp_v3", "SNMP v3"
        API_TOKEN = "api_token", "Token API"
        OTHER = "other", "Otro"

    name = models.CharField(max_length=120, unique=True)
    purpose = models.CharField(max_length=20, choices=Purpose.choices)
    auth_type = models.CharField(max_length=30, choices=AuthType.choices)
    storage_reference = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    devices = models.ManyToManyField(
        Device,
        through="DeviceCredentialProfile",
        related_name="credential_profiles",
        blank=True,
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "perfil de credenciales"
        verbose_name_plural = "perfiles de credenciales"
        indexes = [
            models.Index(fields=["purpose", "auth_type"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.name


class DeviceCredentialProfile(TimeStampedModel):
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="device_credential_profiles",
    )
    credential_profile = models.ForeignKey(
        CredentialProfile,
        on_delete=models.PROTECT,
        related_name="device_assignments",
    )
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["device__name", "credential_profile__name"]
        verbose_name = "perfil de credenciales por dispositivo"
        verbose_name_plural = "perfiles de credenciales por dispositivo"
        constraints = [
            models.UniqueConstraint(
                fields=["device", "credential_profile"],
                name="inventory_device_credential_profile_unique",
            ),
        ]
        indexes = [
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.device} - {self.credential_profile}"
