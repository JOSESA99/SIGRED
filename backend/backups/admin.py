from django.contrib import admin

from .models import (
    BackupAttempt,
    BackupPolicy,
    BackupPolicyDevice,
    BackupRun,
    BackupSchedule,
    ConfigComparison,
    ConfigVersion,
    RestorePlan,
)


class BackupPolicyDeviceInline(admin.TabularInline):
    model = BackupPolicyDevice
    extra = 0
    autocomplete_fields = ("device",)


class BackupScheduleInline(admin.TabularInline):
    model = BackupSchedule
    extra = 0


@admin.register(BackupPolicy)
class BackupPolicyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_active",
        "default_retry_count",
        "default_timeout_seconds",
        "created_by",
        "updated_at",
    )
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    autocomplete_fields = ("created_by",)
    inlines = (BackupPolicyDeviceInline, BackupScheduleInline)


@admin.register(BackupPolicyDevice)
class BackupPolicyDeviceAdmin(admin.ModelAdmin):
    list_display = ("policy", "device", "enabled", "updated_at")
    list_filter = ("enabled", "policy")
    search_fields = ("policy__name", "device__name", "device__management_ip")
    autocomplete_fields = ("policy", "device")


@admin.register(BackupSchedule)
class BackupScheduleAdmin(admin.ModelAdmin):
    list_display = ("policy", "frequency", "timezone", "next_run_at", "is_active")
    list_filter = ("frequency", "is_active", "timezone")
    search_fields = ("policy__name", "cron_expression")
    autocomplete_fields = ("policy",)


class BackupAttemptInline(admin.TabularInline):
    model = BackupAttempt
    extra = 0
    autocomplete_fields = ("device",)
    fields = (
        "device",
        "attempt_number",
        "status",
        "started_at",
        "finished_at",
        "oxidized_node_ref",
        "oxidized_version_ref",
        "error_code",
        "error_message",
    )


@admin.register(BackupRun)
class BackupRunAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "policy",
        "trigger_type",
        "status",
        "triggered_by",
        "started_at",
        "finished_at",
    )
    list_filter = ("trigger_type", "status", "policy")
    search_fields = ("policy__name", "summary")
    autocomplete_fields = ("policy", "triggered_by")
    readonly_fields = ("created_at",)
    inlines = (BackupAttemptInline,)


@admin.register(BackupAttempt)
class BackupAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "run",
        "device",
        "attempt_number",
        "status",
        "started_at",
        "finished_at",
    )
    list_filter = ("status", "attempt_number")
    search_fields = (
        "device__name",
        "device__management_ip",
        "oxidized_node_ref",
        "oxidized_version_ref",
        "error_message",
    )
    autocomplete_fields = ("run", "device")


@admin.register(ConfigVersion)
class ConfigVersionAdmin(admin.ModelAdmin):
    list_display = (
        "device",
        "source",
        "external_ref",
        "collected_at",
        "size_bytes",
    )
    list_filter = ("source", "collected_at")
    search_fields = ("device__name", "external_ref", "checksum")
    autocomplete_fields = ("device", "created_by")
    readonly_fields = ("created_at",)


@admin.register(ConfigComparison)
class ConfigComparisonAdmin(admin.ModelAdmin):
    list_display = ("device", "from_version", "to_version", "created_by", "created_at")
    list_filter = ("created_at",)
    search_fields = ("device__name", "change_summary", "diff_external_ref")
    autocomplete_fields = ("device", "from_version", "to_version", "created_by")
    readonly_fields = ("created_at",)


@admin.register(RestorePlan)
class RestorePlanAdmin(admin.ModelAdmin):
    list_display = (
        "device",
        "config_version",
        "status",
        "requested_by",
        "approved_by",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("device__name", "reason")
    autocomplete_fields = (
        "device",
        "config_version",
        "requested_by",
        "approved_by",
    )
    readonly_fields = ("created_at",)
