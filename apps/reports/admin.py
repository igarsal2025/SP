from django.contrib import admin

from .models import Evidencia, Incidente, ReporteSemanal


@admin.register(ReporteSemanal)
class ReporteSemanalAdmin(admin.ModelAdmin):
    list_display = [
        "project_name",
        "week_start",
        "technician",
        "progress_pct",
        "status",
        "created_at",
    ]
    list_filter = ["status", "week_start", "created_at"]
    search_fields = ["project_name", "site_address", "technician__username"]
    readonly_fields = ["id", "created_at", "updated_at", "submitted_at", "approved_at"]
    date_hierarchy = "week_start"


@admin.register(Evidencia)
class EvidenciaAdmin(admin.ModelAdmin):
    list_display = ["file_name", "tipo", "reporte", "created_at"]
    list_filter = ["tipo", "created_at"]
    search_fields = ["file_name", "description"]


@admin.register(Incidente)
class IncidenteAdmin(admin.ModelAdmin):
    list_display = ["title", "reporte", "severity", "resolved", "created_at"]
    list_filter = ["severity", "resolved", "created_at"]
    search_fields = ["title", "description"]
