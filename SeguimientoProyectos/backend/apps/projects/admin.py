from django.contrib import admin

from .models import Presupuesto, Proyecto, Riesgo, Tarea


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "name",
        "status",
        "progress_pct",
        "project_manager",
        "start_date",
        "end_date",
    ]
    list_filter = ["status", "priority", "start_date"]
    search_fields = ["code", "name", "client_name"]
    readonly_fields = ["id", "created_at", "updated_at", "completed_at"]
    date_hierarchy = "start_date"
    filter_horizontal = ["technicians"]


@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    list_display = ["title", "project", "status", "assigned_to", "due_date"]
    list_filter = ["status", "priority", "due_date"]
    search_fields = ["title", "description"]


@admin.register(Riesgo)
class RiesgoAdmin(admin.ModelAdmin):
    list_display = ["title", "project", "severity", "probability", "mitigation_status"]
    list_filter = ["severity", "probability", "mitigation_status"]
    search_fields = ["title", "description"]


@admin.register(Presupuesto)
class PresupuestoAdmin(admin.ModelAdmin):
    list_display = ["project", "category", "description", "amount_estimated", "amount_actual"]
    list_filter = ["category"]
    search_fields = ["description"]
