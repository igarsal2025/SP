import uuid

from django.db import models


class Company(models.Model):
    PLAN_CHOICES = [
        ("starter", "Starter"),
        ("pro", "Pro"),
        ("enterprise", "Enterprise"),
    ]
    STATUS_CHOICES = [
        ("active", "Active"),
        ("suspended", "Suspended"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    rfc = models.CharField(max_length=20, blank=True)
    tax_regime = models.CharField(max_length=100, blank=True)
    timezone = models.CharField(max_length=64, default="America/Mexico_City")
    locale = models.CharField(max_length=10, default="es-MX")
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default="starter")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Sitec(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("suspended", "Suspended"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    schema_name = models.CharField(max_length=100, unique=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="sitec_instances"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    activated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name} ({self.schema_name})"
