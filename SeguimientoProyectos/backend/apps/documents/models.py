import uuid

from django.conf import settings
from django.db import models

from apps.companies.models import Company, Sitec


class Document(models.Model):
    """Documento generado (PDF) asociado a un reporte."""

    STATUS_CHOICES = [
        ("pending", "Pendiente"),
        ("ready", "Listo"),
        ("failed", "Fallido"),
    ]

    TYPE_CHOICES = [
        ("weekly_report", "Reporte semanal"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    sitec = models.ForeignKey(Sitec, on_delete=models.CASCADE)
    report = models.ForeignKey(
        "reports.ReporteSemanal",
        on_delete=models.CASCADE,
        related_name="documents",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="documents_created",
    )

    doc_type = models.CharField(max_length=40, choices=TYPE_CHOICES, default="weekly_report")
    version = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    file_path = models.CharField(max_length=600, blank=True)
    file_name = models.CharField(max_length=255, blank=True)
    file_size = models.IntegerField(null=True, blank=True)
    mime_type = models.CharField(max_length=100, blank=True, default="application/pdf")
    checksum_sha256 = models.CharField(max_length=128, blank=True)

    qr_token = models.UUIDField(default=uuid.uuid4, editable=False)
    nom151_stamp = models.CharField(max_length=200, blank=True)
    issued_at = models.DateTimeField(null=True, blank=True)

    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["company", "-created_at"]),
            models.Index(fields=["report", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["report", "version"], name="document_unique_report_version"),
        ]

    def __str__(self):
        return f"{self.report_id} v{self.version} ({self.status})"
