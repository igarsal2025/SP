import uuid

from django.conf import settings
from django.db import models

from apps.companies.models import Company


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("admin_empresa", "Admin Empresa"),
        ("pm", "Project Manager"),
        ("tecnico", "Tecnico"),
        ("supervisor", "Supervisor"),
        ("cliente", "Cliente"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="users", null=True, blank=True
    )
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    department = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    preferences = models.JSONField(default=dict, blank=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class AccessPolicy(models.Model):
    EFFECT_CHOICES = [
        ("allow", "Allow"),
        ("deny", "Deny"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="policies")
    action = models.CharField(max_length=100)
    conditions = models.JSONField(default=dict, blank=True)
    effect = models.CharField(max_length=10, choices=EFFECT_CHOICES, default="allow")
    priority = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name} - {self.action}"
