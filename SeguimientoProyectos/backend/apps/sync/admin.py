from django.contrib import admin

from .models import SyncItem, SyncSession


@admin.register(SyncSession)
class SyncSessionAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "status", "items_synced", "conflicts_detected", "started_at"]
    list_filter = ["status", "started_at"]
    search_fields = ["user__username", "id"]
    readonly_fields = ["id", "created_at", "updated_at"]
    date_hierarchy = "started_at"


@admin.register(SyncItem)
class SyncItemAdmin(admin.ModelAdmin):
    list_display = ["id", "session", "entity_type", "entity_id", "status", "created_at"]
    list_filter = ["status", "entity_type", "created_at"]
    search_fields = ["entity_id", "entity_type"]
    readonly_fields = ["id", "created_at", "updated_at"]
