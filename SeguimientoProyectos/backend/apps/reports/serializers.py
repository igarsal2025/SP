from rest_framework import serializers

from apps.accounts.serializers import UserSerializer

from .models import Evidencia, Incidente, ReporteSemanal


class EvidenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evidencia
        fields = [
            "id",
            "reporte",
            "tipo",
            "file_path",
            "file_name",
            "file_size",
            "mime_type",
            "latitude",
            "longitude",
            "description",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class IncidenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incidente
        fields = [
            "id",
            "reporte",
            "title",
            "description",
            "severity",
            "mitigation_plan",
            "resolved",
            "resolved_at",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ReporteSemanalSerializer(serializers.ModelSerializer):
    technician = serializers.PrimaryKeyRelatedField(read_only=True)
    supervisor = serializers.PrimaryKeyRelatedField(read_only=True)
    evidencias = EvidenciaSerializer(many=True, read_only=True)
    incidentes = IncidenteSerializer(many=True, read_only=True)

    class Meta:
        model = ReporteSemanal
        fields = [
            "id",
            "company",
            "sitec",
            "project",
            "technician",
            "supervisor",
            "week_start",
            "week_end",
            "project_name",
            "site_address",
            "progress_pct",
            "schedule_status",
            "cabling_nodes_total",
            "cabling_nodes_ok",
            "racks_installed",
            "security_devices",
            "materials_count",
            "tests_passed",
            "qa_signed",
            "incidents",
            "incidents_count",
            "incidents_severity",
            "incidents_detail",
            "mitigation_plan",
            "wizard_schema_version",
            "wizard_updated_at",
            "wizard_client_id",
            "wizard_data",
            "metadata",
            "rules_version",
            "riesgo_score",
            "sugerencias_ia",
            "predicciones",
            "status",
            "signature_tech",
            "signature_supervisor",
            "signature_date",
            "evidencias",
            "incidentes",
            "created_at",
            "updated_at",
            "submitted_at",
            "approved_at",
        ]
        read_only_fields = [
            "id",
            "company",
            "sitec",
            "technician",
            "supervisor",
            "created_at",
            "updated_at",
            "submitted_at",
            "approved_at",
        ]


class ReporteSemanalListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados"""
    technician = serializers.StringRelatedField()
    project_name = serializers.CharField()

    class Meta:
        model = ReporteSemanal
        fields = [
            "id",
            "project_name",
            "week_start",
            "progress_pct",
            "status",
            "technician",
            "created_at",
        ]
