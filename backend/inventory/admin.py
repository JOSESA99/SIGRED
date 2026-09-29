from django.contrib import admin

from .models import (
    CredentialProfile,
    Device,
    DeviceCapability,
    DeviceCredentialProfile,
    DeviceModel,
    ExternalIdentifier,
    InstitutionalUnit,
    Location,
    Vendor,
)


@admin.register(InstitutionalUnit)
class InstitutionalUnitAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "unit_type", "parent", "is_active")
    list_filter = ("unit_type", "is_active")
    search_fields = ("name", "code")
    autocomplete_fields = ("parent",)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "unit", "location_type", "parent", "is_active")
    list_filter = ("location_type", "is_active", "unit")
    search_fields = ("name", "unit__name")
    autocomplete_fields = ("unit", "parent")


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ("name", "website", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(DeviceModel)
class DeviceModelAdmin(admin.ModelAdmin):
    list_display = ("name", "vendor", "device_family", "device_type", "is_active")
    list_filter = ("device_type", "is_active", "vendor")
    search_fields = ("name", "device_family", "vendor__name")
    autocomplete_fields = ("vendor",)


class DeviceCapabilityInline(admin.TabularInline):
    model = DeviceCapability
    extra = 0
    fields = ("capability", "status", "source", "verified_at", "notes")


class ExternalIdentifierInline(admin.TabularInline):
    model = ExternalIdentifier
    extra = 0
    fields = ("system", "external_id", "external_name", "url", "is_active")


class DeviceCredentialProfileForDeviceInline(admin.TabularInline):
    model = DeviceCredentialProfile
    extra = 0
    autocomplete_fields = ("credential_profile",)
    fields = ("credential_profile", "is_active", "notes")


class DeviceCredentialProfileForCredentialInline(admin.TabularInline):
    model = DeviceCredentialProfile
    extra = 0
    autocomplete_fields = ("device",)
    fields = ("device", "is_active", "notes")


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "management_ip",
        "unit",
        "location",
        "vendor",
        "model",
        "device_type",
        "status",
        "criticality",
        "is_demo",
    )
    list_filter = (
        "status",
        "criticality",
        "device_type",
        "vendor",
        "unit",
        "is_demo",
    )
    search_fields = (
        "name",
        "hostname",
        "management_ip",
        "serial_number",
        "asset_code",
    )
    autocomplete_fields = ("unit", "location", "vendor", "model")
    inlines = (
        DeviceCapabilityInline,
        ExternalIdentifierInline,
        DeviceCredentialProfileForDeviceInline,
    )


@admin.register(DeviceCapability)
class DeviceCapabilityAdmin(admin.ModelAdmin):
    list_display = ("device", "capability", "status", "source", "verified_at")
    list_filter = ("capability", "status", "source")
    search_fields = ("device__name", "device__management_ip", "notes")
    autocomplete_fields = ("device",)


@admin.register(ExternalIdentifier)
class ExternalIdentifierAdmin(admin.ModelAdmin):
    list_display = (
        "device",
        "system",
        "external_id",
        "external_name",
        "is_active",
        "last_verified_at",
    )
    list_filter = ("system", "is_active")
    search_fields = ("device__name", "external_id", "external_name")
    autocomplete_fields = ("device",)


@admin.register(CredentialProfile)
class CredentialProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "purpose", "auth_type", "storage_reference", "is_active")
    list_filter = ("purpose", "auth_type", "is_active")
    search_fields = ("name", "storage_reference")
    inlines = (DeviceCredentialProfileForCredentialInline,)


@admin.register(DeviceCredentialProfile)
class DeviceCredentialProfileAdmin(admin.ModelAdmin):
    list_display = ("device", "credential_profile", "is_active")
    list_filter = ("is_active", "credential_profile__purpose")
    search_fields = ("device__name", "credential_profile__name")
    autocomplete_fields = ("device", "credential_profile")
