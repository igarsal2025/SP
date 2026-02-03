import uuid

from django.conf import settings
from django.db import models

from apps.companies.models import Company, Sitec


class Proyecto(models.Model):
    """Proyecto de instalación IT"""
    STATUS_CHOICES = [
        ("planning", "Planificación"),
        ("in_progress", "En Progreso"),
        ("on_hold", "En Pausa"),
        ("completed", "Completado"),
        ("cancelled", "Cancelado"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Baja"),
        ("medium", "Media"),
        ("high", "Alta"),
        ("urgent", "Urgente"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    sitec = models.ForeignKey(Sitec, on_delete=models.CASCADE)

    # Información básica
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True, help_text="Código único del proyecto")
    description = models.TextField(blank=True)
    site_address = models.TextField()
    client_name = models.CharField(max_length=200, blank=True)
    client_contact = models.CharField(max_length=200, blank=True)

    # Fechas
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    estimated_end_date = models.DateField(null=True, blank=True)

    # Asignaciones
    project_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="proyectos_pm",
    )
    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="proyectos_supervisor",
    )
    technicians = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="proyectos_tecnico",
        blank=True,
    )

    # Estado y progreso
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="planning")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="medium")
    progress_pct = models.IntegerField(default=0, help_text="Porcentaje de avance 0-100")

    # Presupuesto
    budget_estimated = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, help_text="Presupuesto estimado (MXN)"
    )
    budget_actual = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, help_text="Presupuesto actual (MXN)"
    )

    # Campos IA (para Módulo 5)
    riesgo_score = models.FloatField(null=True, blank=True, help_text="Score de riesgo calculado por IA")
    sugerencias_ia = models.JSONField(default=list, blank=True)
    predicciones = models.JSONField(default=dict, blank=True)

    # Metadatos
    metadata = models.JSONField(default=dict, blank=True)
    tags = models.JSONField(default=list, blank=True)  # Tags para categorización

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["company", "status"]),
            models.Index(fields=["project_manager", "-created_at"]),
            models.Index(fields=["code"]),
            models.Index(fields=["start_date", "end_date"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(progress_pct__gte=0) & models.Q(progress_pct__lte=100),
                name="projects_progress_pct_0_100",
            ),
            models.CheckConstraint(
                check=models.Q(budget_estimated__gte=0) | models.Q(budget_estimated__isnull=True),
                name="projects_budget_estimated_non_negative",
            ),
            models.CheckConstraint(
                check=models.Q(budget_actual__gte=0) | models.Q(budget_actual__isnull=True),
                name="projects_budget_actual_non_negative",
            ),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def is_overdue(self):
        """Verifica si el proyecto está retrasado"""
        if self.end_date and self.status not in ["completed", "cancelled"]:
            from django.utils import timezone
            return timezone.now().date() > self.end_date
        return False

    @property
    def days_remaining(self):
        """Días restantes hasta fecha de fin"""
        if self.end_date:
            from datetime import date
            delta = self.end_date - date.today()
            return delta.days
        return None


class Tarea(models.Model):
    """Tareas del proyecto"""
    STATUS_CHOICES = [
        ("pending", "Pendiente"),
        ("in_progress", "En Progreso"),
        ("completed", "Completada"),
        ("blocked", "Bloqueada"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name="tareas",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    priority = models.CharField(
        max_length=20,
        choices=Proyecto.PRIORITY_CHOICES,
        default="medium",
    )

    # Asignación
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tareas_asignadas",
    )

    # Fechas
    due_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Metadatos
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["project", "status"]),
            models.Index(fields=["assigned_to", "status"]),
            models.Index(fields=["due_date"]),
        ]

    def __str__(self):
        return f"{self.project.code} - {self.title}"


class Riesgo(models.Model):
    """Riesgos identificados en el proyecto"""
    SEVERITY_CHOICES = [
        ("low", "Bajo"),
        ("medium", "Medio"),
        ("high", "Alto"),
        ("critical", "Crítico"),
    ]

    PROBABILITY_CHOICES = [
        ("very_low", "Muy Baja"),
        ("low", "Baja"),
        ("medium", "Media"),
        ("high", "Alta"),
        ("very_high", "Muy Alta"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name="riesgos",
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default="medium")
    probability = models.CharField(max_length=20, choices=PROBABILITY_CHOICES, default="medium")

    # Mitigación
    mitigation_plan = models.TextField(blank=True)
    mitigation_status = models.CharField(
        max_length=20,
        choices=[
            ("not_started", "No Iniciada"),
            ("in_progress", "En Progreso"),
            ("completed", "Completada"),
        ],
        default="not_started",
    )

    # Campos IA
    riesgo_score = models.FloatField(null=True, blank=True, help_text="Score calculado por IA")
    sugerencias_ia = models.JSONField(default=list, blank=True)

    # Metadatos
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["project", "severity"]),
            models.Index(fields=["mitigation_status"]),
        ]

    def __str__(self):
        return f"Riesgo {self.title} - {self.severity}"


class Presupuesto(models.Model):
    """Presupuesto del proyecto"""
    CATEGORY_CHOICES = [
        ("materiales", "Materiales"),
        ("mano_obra", "Mano de Obra"),
        ("equipamiento", "Equipamiento"),
        ("servicios", "Servicios"),
        ("otros", "Otros"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name="presupuestos",
    )
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.CharField(max_length=200)
    amount_estimated = models.DecimalField(
        max_digits=12, decimal_places=2, help_text="Monto estimado (MXN)"
    )
    amount_actual = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, help_text="Monto actual (MXN)"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "-created_at"]
        indexes = [
            models.Index(fields=["project", "category"]),
        ]

    def __str__(self):
        return f"{self.project.code} - {self.category} - {self.amount_estimated}"

    @property
    def variance(self):
        """Diferencia entre estimado y actual"""
        if self.amount_actual:
            return self.amount_actual - self.amount_estimated
        return None
