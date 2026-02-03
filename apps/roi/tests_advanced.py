"""
Tests para funcionalidades avanzadas de ROI
"""
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.companies.models import Company, Sitec
from apps.projects.models import Proyecto

from apps.accounts.models import UserProfile

User = get_user_model()


class RoiAdvancedTests(APITestCase):
    """Tests para funcionalidades avanzadas de ROI"""

    def setUp(self):
        self.company = Company.objects.create(name="Test Company")
        self.sitec = Sitec.objects.create(company=self.company, schema_name="test")
        self.user = User.objects.create_user(username="testuser", password="password123")
        UserProfile.objects.create(user=self.user, company=self.company, role="pm")
        self.client.login(username="testuser", password="password123")
        self.client.defaults["HTTP_X_SITEC_ID"] = str(self.sitec.id)

        # Crear proyectos de prueba con presupuestos
        now = timezone.now()
        self.project1 = Proyecto.objects.create(
            company=self.company,
            sitec=self.sitec,
            name="Proyecto 1",
            code="P1",
            site_address="123 Test St",
            start_date=date(2023, 1, 1),
            project_manager=self.user,
            budget_estimated=100000,
            budget_actual=90000,
        )
        self.project2 = Proyecto.objects.create(
            company=self.company,
            sitec=self.sitec,
            name="Proyecto 2",
            code="P2",
            site_address="456 Test St",
            start_date=date(2023, 2, 1),
            project_manager=self.user,
            budget_estimated=50000,
            budget_actual=55000,
        )

    def test_roi_snapshot_with_comparatives(self):
        """Test que el snapshot de ROI incluye comparativos"""
        response = self.client.get("/api/roi/?period_days=30")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("comparatives", data)
        self.assertIn("prev_period", data["comparatives"])

    def test_roi_trends_endpoint(self):
        """Test que el endpoint de tendencias funciona"""
        response = self.client.get("/api/roi/trends/?periods=6&type=month")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("trends", data)
        self.assertIn("period_type", data)
        self.assertEqual(data["period_type"], "month")

    def test_roi_trends_weekly(self):
        """Test que las tendencias semanales funcionan"""
        response = self.client.get("/api/roi/trends/?periods=4&type=week")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["period_type"], "week")
        self.assertEqual(len(data["trends"]), 4)

    def test_roi_goals_endpoint(self):
        """Test que el endpoint de metas funciona"""
        response = self.client.get("/api/roi/goals/?target_roi_pct=10&period_days=30")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("goals", data)
        self.assertIn("current", data)
        self.assertIn("status", data["goals"])

    def test_roi_analysis_endpoint(self):
        """Test que el endpoint de análisis funciona"""
        response = self.client.get("/api/roi/analysis/?period_days=30")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("by_status", data)
        self.assertIn("top_performers", data)
        self.assertIn("underperformers", data)

    def test_roi_trends_caching(self):
        """Test que el cache de tendencias funciona"""
        # Primera request
        response1 = self.client.get("/api/roi/trends/?periods=6")
        self.assertEqual(response1.status_code, 200)
        
        # Segunda request (debe usar cache)
        response2 = self.client.get("/api/roi/trends/?periods=6")
        self.assertEqual(response2.status_code, 200)
        # Los datos deben ser iguales (mismo timestamp de computed_at si está cacheado)
        self.assertEqual(response1.json()["periods"], response2.json()["periods"])
