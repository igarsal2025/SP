import uuid

from django.db import models

from apps.companies.models import Company, Sitec


class RuleSet(models.Model):
    SCOPE_CHOICES = [
        ("wizard", "Wizard"),
        ("report", "Report"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    sitec = models.ForeignKey(Sitec, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    version = models.IntegerField(default=1)
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, default="wizard")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["company", "sitec", "scope", "-created_at"]),
        ]
        unique_together = ("company", "sitec", "scope", "version")


class RuleItem(models.Model):
    SEVERITY_CHOICES = [
        ("critical", "Critical"),
        ("warning", "Warning"),
        ("info", "Info"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ruleset = models.ForeignKey(RuleSet, on_delete=models.CASCADE, related_name="rules")
    code = models.CharField(max_length=80)
    field = models.CharField(max_length=80, blank=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default="warning")
    message = models.CharField(max_length=200)
    step = models.IntegerField(null=True, blank=True)

    # condition example: {"field":"progress_pct","op":"lt","value":0}
    condition = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["code"]
        indexes = [
            models.Index(fields=["ruleset", "step", "severity"]),
            models.Index(fields=["code"]),
        ]
