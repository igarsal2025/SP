"""
Tests básicos del wizard (mantener compatibilidad)
Los tests completos están en tests_security.py, tests_performance.py, tests_functional.py
"""
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.accounts.models import AccessPolicy, UserProfile
from apps.companies.models import Company, Sitec

User = get_user_model()


class WizardApiTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="SITEC",
            timezone="America/Mexico_City",
            locale="es-MX",
            plan="enterprise",
            status="active",
        )
        self.sitec = Sitec.objects.create(
            company=self.company,
            schema_name="sitec",
            status="active",
        )
        self.user = User.objects.create_user(
            username="wizard",
            email="wizard@sitec.mx",
            password="password123",
        )
        UserProfile.objects.create(
            user=self.user,
            company=self.company,
            role="tecnico",
        )
        AccessPolicy.objects.create(
            company=self.company,
            action="*",
            effect="allow",
            priority=0,
            is_active=True,
        )
        self.client.login(username="wizard", password="password123")

    def test_save_step_creates_draft(self):
        response = self.client.post(
            "/api/wizard/steps/save/",
            {"step": 1, "data": {"project_name": "Demo", "week_start": "2026-01-01"}},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["step"], 1)

    def test_validate_step_blocks_missing_required(self):
        response = self.client.post(
            "/api/wizard/validate/",
            {"step": 1, "data": {}},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["allowed"])
        self.assertIn("project_name_required", response.data["critical"])

    def test_sync_multiple_steps(self):
        response = self.client.post(
            "/api/wizard/sync/",
            {
                "steps": [
                    {"step": 1, "data": {"project_name": "A", "week_start": "2026-01-01"}},
                    {"step": 2, "data": {"progress_pct": 20}},
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["updated_steps"]), 2)

    def test_schema_endpoint_returns_schema(self):
        response = self.client.get("/api/wizard/schema/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("schema_version", response.data)
        self.assertIn("steps", response.data)
