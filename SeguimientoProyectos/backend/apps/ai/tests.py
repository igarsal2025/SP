from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APITestCase

from apps.accounts.models import AccessPolicy, UserProfile
from apps.companies.models import Company, Sitec
from apps.reports.models import ReporteSemanal

from .pipeline import run_training_pipeline

User = get_user_model()


class AiModuleTests(APITestCase):
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
            username="ai-user",
            email="ai@sitec.mx",
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
        self.client.login(username="ai-user", password="password123")

    def test_contract_endpoint(self):
        response = self.client.get("/api/ai/contract/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("request", response.data)
        self.assertIn("response", response.data)

    def test_quick_suggest(self):
        response = self.client.post(
            "/api/ai/suggest/",
            {"step": 10, "data": {"incidents": "true"}},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        self.assertIsInstance(response.data["suggestions"], list)

    def test_heavy_suggest_fallback(self):
        response = self.client.post(
            "/api/ai/suggest/",
            {"step": 10, "data": {"incidents": "true"}, "mode": "heavy"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "queued")
        self.assertTrue(response.data["fallback"])

    def test_suggestion_status_endpoint(self):
        response = self.client.post(
            "/api/ai/suggest/",
            {"step": 2, "data": {"progress_pct": 10}, "mode": "heavy"},
            format="json",
        )
        suggestion_id = response.data.get("suggestion_id")
        self.assertIsNotNone(suggestion_id)

        status_response = self.client.get(f"/api/ai/suggestions/{suggestion_id}/")
        self.assertEqual(status_response.status_code, 200)
        self.assertIn("status", status_response.data)

    def test_asset_create(self):
        response = self.client.post(
            "/api/ai/assets/",
            {"asset_type": "image", "hash": "hash123", "metadata": {"size": "1mb"}},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["asset_type"], "image")


class AiPipelineTests(TestCase):
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
            username="ai-pipeline",
            email="pipeline@sitec.mx",
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
        ReporteSemanal.objects.create(
            company=self.company,
            sitec=self.sitec,
            technician=self.user,
            project_name="Demo",
            week_start="2026-01-01",
            site_address="Site",
            progress_pct=10,
            status="draft",
            wizard_data={"steps": {"1": {"project_name": "Demo"}}},
        )

    @override_settings(AI_TRAIN_PROVIDER_URL="")
    def test_run_training_pipeline_creates_job(self):
        job = run_training_pipeline(self.company, self.sitec, created_by=self.user, since_days=30, limit=10)
        self.assertEqual(job.status, "dataset_ready")
        self.assertTrue(job.dataset_path)
        self.assertTrue(job.dataset_size)
        self.assertTrue(job.dataset_checksum)
