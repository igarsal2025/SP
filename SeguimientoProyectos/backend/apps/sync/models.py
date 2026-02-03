import uuid

from django.conf import settings
from django.db import models

from apps.companies.models import Company, Sitec


class SyncSession(models.Model):
    """Sesión de sincronización para tracking y auditoría"""
    STATUS_CHOICES = [
        ("pending", "Pendiente"),
        ("syncing", "Sincronizando"),
        ("completed", "Completada"),
        ("failed", "Fallida"),
        ("conflict", "Conflicto"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    sitec = models.ForeignKey(Sitec, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    items_synced = models.IntegerField(default=0)
    items_failed = models.IntegerField(default=0)
    conflicts_detected = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)  # Para datos adicionales
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["company", "user", "-started_at"]),
            models.Index(fields=["status", "-started_at"]),
        ]

    def __str__(self):
        return f"Sync {self.id} - {self.user.username} - {self.status}"


class SyncItem(models.Model):
    """Item individual sincronizado en una sesión"""
    STATUS_CHOICES = [
        ("pending", "Pendiente"),
        ("synced", "Sincronizado"),
        ("failed", "Fallido"),
        ("conflict", "Conflicto"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(SyncSession, on_delete=models.CASCADE, related_name="items")
    entity_type = models.CharField(max_length=50)  # 'wizard_step', 'report', 'project', etc.
    entity_id = models.CharField(max_length=255)  # ID del recurso sincronizado
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    client_timestamp = models.DateTimeField(null=True, blank=True)
    server_timestamp = models.DateTimeField(null=True, blank=True)
    data = models.JSONField(default=dict)  # Datos sincronizados
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["session", "status"]),
            models.Index(fields=["entity_type", "entity_id"]),
        ]
        unique_together = [("session", "entity_type", "entity_id")]

    def __str__(self):
        return f"{self.entity_type}:{self.entity_id} - {self.status}"
