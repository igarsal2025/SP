import uuid

from django.conf import settings
from django.db import models

from apps.companies.models import Company, Sitec


class ReporteSemanal(models.Model):
    """Reporte semanal de avance de proyecto"""
    STATUS_CHOICES = [
        ("draft", "Borrador"),
        ("submitted", "Enviado"),
        ("approved", "Aprobado"),
        ("rejected", "Rechazado"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    sitec = models.ForeignKey(Sitec, on_delete=models.CASCADE)
    project = models.ForeignKey(
        "projects.Proyecto",
        on_delete=models.SET_NULL,
        related_name="reportes",
        null=True,
        blank=True,
    )
    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="reportes_tecnico",
    )
    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reportes_supervisor",
    )

    # Datos del reporte (del wizard)
    week_start = models.DateField(help_text="Inicio de semana del reporte")
    week_end = models.DateField(null=True, blank=True)
    project_name = models.CharField(max_length=200)
    site_address = models.TextField()
    progress_pct = models.IntegerField(default=0, help_text="Porcentaje de avance 0-100")
    schedule_status = models.CharField(max_length=50, blank=True)

    # Datos técnicos
    cabling_nodes_total = models.IntegerField(null=True, blank=True)
    cabling_nodes_ok = models.IntegerField(null=True, blank=True)
    racks_installed = models.IntegerField(null=True, blank=True)
    security_devices = models.IntegerField(null=True, blank=True)
    materials_count = models.IntegerField(null=True, blank=True)

    # Evidencias y pruebas
    tests_passed = models.BooleanField(null=True, blank=True)
    qa_signed = models.BooleanField(default=False)

    # Incidentes
    incidents = models.BooleanField(default=False)
    incidents_count = models.IntegerField(default=0)
    incidents_severity = models.CharField(max_length=20, blank=True)
    incidents_detail = models.TextField(blank=True)
    mitigation_plan = models.TextField(blank=True)

    # Datos adicionales (JSON para flexibilidad)
    wizard_schema_version = models.IntegerField(default=1)
    wizard_updated_at = models.DateTimeField(null=True, blank=True)
    wizard_client_id = models.CharField(max_length=100, blank=True)
    wizard_data = models.JSONField(default=dict, blank=True)  # Datos completos del wizard
    metadata = models.JSONField(default=dict, blank=True)  # Metadatos adicionales
    rules_version = models.IntegerField(null=True, blank=True)

    # Campos IA (para Módulo 5)
    riesgo_score = models.FloatField(null=True, blank=True, help_text="Score de riesgo calculado por IA")
    sugerencias_ia = models.JSONField(default=list, blank=True)
    predicciones = models.JSONField(default=dict, blank=True)

    # Estado y firmas
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    signature_tech = models.TextField(blank=True)  # Firma del técnico
    signature_supervisor = models.TextField(blank=True)  # Firma del supervisor
    signature_date = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-week_start", "-created_at"]
        indexes = [
            models.Index(fields=["company", "-week_start"]),
            models.Index(fields=["technician", "-week_start"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["project", "-week_start"]),
            # Índices adicionales para optimización
            models.Index(fields=["company", "sitec", "-week_start"]),
            models.Index(fields=["company", "sitec", "status", "-created_at"]),
            models.Index(fields=["week_start"]),  # Para queries por fecha
            models.Index(fields=["created_at"]),  # Para queries por fecha de creación
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(progress_pct__gte=0) & models.Q(progress_pct__lte=100),
                name="reports_progress_pct_0_100",
            ),
            models.CheckConstraint(
                check=models.Q(cabling_nodes_total__gte=0) | models.Q(cabling_nodes_total__isnull=True),
                name="reports_cabling_nodes_total_non_negative",
            ),
            models.CheckConstraint(
                check=models.Q(materials_count__gte=0) | models.Q(materials_count__isnull=True),
                name="reports_materials_count_non_negative",
            ),
            models.CheckConstraint(
                check=models.Q(security_devices__gte=0) | models.Q(security_devices__isnull=True),
                name="reports_security_devices_non_negative",
            ),
        ]

    def __str__(self):
        return f"Reporte {self.project_name} - Semana {self.week_start}"

    @property
    def is_complete(self):
        """Verifica si el reporte está completo"""
        return (
            self.project_name
            and self.week_start
            and self.site_address
            and self.technician
            and self.progress_pct is not None
        )


class Evidencia(models.Model):
    """Evidencias fotográficas y documentos del reporte"""
    TIPO_CHOICES = [
        ("photo", "Fotografía"),
        ("document", "Documento"),
        ("video", "Video"),
        ("audio", "Audio"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporte = models.ForeignKey(
        ReporteSemanal,
        on_delete=models.CASCADE,
        related_name="evidencias",
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default="photo")
    file_path = models.CharField(max_length=500)  # Ruta al archivo en storage
    file_name = models.CharField(max_length=255)
    file_size = models.IntegerField(null=True, blank=True)  # Tamaño en bytes
    mime_type = models.CharField(max_length=100, blank=True)

    # Geolocalización
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Metadatos
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["reporte", "-created_at"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(latitude__gte=-90) & models.Q(latitude__lte=90) | models.Q(latitude__isnull=True),
                name="evidencia_latitude_range",
            ),
            models.CheckConstraint(
                check=models.Q(longitude__gte=-180) & models.Q(longitude__lte=180) | models.Q(longitude__isnull=True),
                name="evidencia_longitude_range",
            ),
        ]

    def __str__(self):
        return f"Evidencia {self.tipo} - {self.file_name}"


class Incidente(models.Model):
    """Incidentes reportados en el reporte semanal"""
    SEVERITY_CHOICES = [
        ("low", "Bajo"),
        ("medium", "Medio"),
        ("high", "Alto"),
        ("critical", "Crítico"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporte = models.ForeignKey(
        ReporteSemanal,
        on_delete=models.CASCADE,
        related_name="incidentes",
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default="medium")
    mitigation_plan = models.TextField(blank=True)
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["reporte", "severity"]),
            models.Index(fields=["resolved", "-created_at"]),
        ]

    def __str__(self):
        return f"Incidente {self.title} - {self.severity}"
