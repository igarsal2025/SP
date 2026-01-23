import uuid

from django.conf import settings
from django.db import models

from apps.companies.models import Company, Sitec


class AiSuggestion(models.Model):
    STATUS_CHOICES = [
        ("success", "Success"),
        ("fallback", "Fallback"),
        ("queued", "Queued"),
        ("error", "Error"),
    ]
    MODE_CHOICES = [
        ("quick", "Quick"),
        ("heavy", "Heavy"),
        ("fallback", "Fallback"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    sitec = models.ForeignKey(Sitec, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    step = models.IntegerField(null=True, blank=True)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default="quick")
    model_name = models.CharField(max_length=100, default="rule_engine")
    model_version = models.CharField(max_length=50, default="v1")

    input_snapshot = models.JSONField(default=dict, blank=True)
    output = models.JSONField(default=dict, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    latency_ms = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="success")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["company", "sitec", "-created_at"]),
            models.Index(fields=["model_name", "model_version"]),
            models.Index(fields=["status", "-created_at"]),
        ]


class AiAsset(models.Model):
    ASSET_CHOICES = [
        ("image", "Image"),
        ("audio", "Audio"),
        ("text", "Text"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    sitec = models.ForeignKey(Sitec, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    suggestion = models.ForeignKey(AiSuggestion, on_delete=models.SET_NULL, null=True, blank=True)

    asset_type = models.CharField(max_length=20, choices=ASSET_CHOICES)
    hash = models.CharField(max_length=128)
    embedding = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["company", "hash"], name="ai_asset_unique_hash_per_company"),
        ]
        indexes = [
            models.Index(fields=["company", "sitec", "-created_at"]),
            models.Index(fields=["asset_type"]),
        ]


class AiTrainingJob(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("dataset_ready", "Dataset Ready"),
        ("submitted", "Submitted"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    sitec = models.ForeignKey(Sitec, on_delete=models.CASCADE)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    provider_name = models.CharField(max_length=100, blank=True)
    provider_job_id = models.CharField(max_length=200, blank=True)

    dataset_path = models.CharField(max_length=500, blank=True)
    dataset_size = models.IntegerField(null=True, blank=True)
    dataset_checksum = models.CharField(max_length=128, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["company", "sitec", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
        ]
