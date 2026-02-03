from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Presupuesto, Proyecto, Riesgo, Tarea


class TareaSerializer(serializers.ModelSerializer):
    assigned_to = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Tarea
        fields = [
            "id",
            "project",
            "title",
            "description",
            "status",
            "priority",
            "assigned_to",
            "due_date",
            "completed_at",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "company",
            "sitec",
            "created_at",
            "updated_at",
            "completed_at",
        ]


class RiesgoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Riesgo
        fields = [
            "id",
            "project",
            "title",
            "description",
            "severity",
            "probability",
            "mitigation_plan",
            "mitigation_status",
            "riesgo_score",
            "sugerencias_ia",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PresupuestoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Presupuesto
        fields = [
            "id",
            "project",
            "category",
            "description",
            "amount_estimated",
            "amount_actual",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


User = get_user_model()


class ProyectoSerializer(serializers.ModelSerializer):
    project_manager = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
    )
    supervisor = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
    )
    technicians = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, required=False
    )
    tareas = TareaSerializer(many=True, read_only=True)
    riesgos = RiesgoSerializer(many=True, read_only=True)
    presupuestos = PresupuestoSerializer(many=True, read_only=True)

    class Meta:
        model = Proyecto
        fields = [
            "id",
            "company",
            "sitec",
            "name",
            "code",
            "description",
            "site_address",
            "client_name",
            "client_contact",
            "start_date",
            "end_date",
            "estimated_end_date",
            "project_manager",
            "supervisor",
            "technicians",
            "status",
            "priority",
            "progress_pct",
            "budget_estimated",
            "budget_actual",
            "riesgo_score",
            "sugerencias_ia",
            "predicciones",
            "metadata",
            "tags",
            "tareas",
            "riesgos",
            "presupuestos",
            "created_at",
            "updated_at",
            "completed_at",
        ]
        read_only_fields = [
            "id",
            "company",
            "sitec",
            "created_at",
            "updated_at",
            "completed_at",
        ]


class ProyectoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados"""
    project_manager = serializers.StringRelatedField()

    class Meta:
        model = Proyecto
        fields = [
            "id",
            "code",
            "name",
            "status",
            "progress_pct",
            "project_manager",
            "start_date",
            "end_date",
            "created_at",
        ]
