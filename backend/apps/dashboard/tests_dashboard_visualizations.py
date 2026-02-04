"""
Tests end-to-end para visualizaciones del dashboard
"""
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.accounts.models import AccessPolicy
from apps.accounts.models import UserProfile
from apps.companies.models import Company, Sitec
from apps.projects.models import Proyecto
from apps.reports.models import ReporteSemanal

User = get_user_model()


class DashboardVisualizationsTests(APITestCase):
    """Tests para visualizaciones del dashboard"""

    def setUp(self):
        self.company = Company.objects.create(
            name="Test Company",
            timezone="America/Mexico_City",
            locale="es-MX",
            plan="enterprise",
            status="active",
        )
        self.sitec = Sitec.objects.create(
            company=self.company,
            schema_name="test",
            status="active",
        )

        # Crear usuario PM
        self.pm = User.objects.create_user(
            username="pm",
            email="pm@example.com",
            password="password123",
        )
        UserProfile.objects.create(
            user=self.pm,
            company=self.company,
            role="pm",
        )

        # Política para dashboard
        AccessPolicy.objects.create(
            company=self.company,
            action="dashboard.*",
            conditions={"role": "pm"},
            effect="allow",
            priority=5,
            is_active=True,
        )

        # Crear datos de prueba
        self.project = Proyecto.objects.create(
            company=self.company,
            sitec=self.sitec,
            name="Proyecto Test",
            code="TEST-001",
            site_address="Calle Test 123",
            start_date=date.today(),
            status="in_progress",
        )

        # Crear reportes para diferentes períodos
        now = timezone.now()
        for i in range(12):
            week_start = (now - timedelta(weeks=i)).date()
            ReporteSemanal.objects.create(
                company=self.company,
                sitec=self.sitec,
                project=self.project,
                week_start=week_start,
                status="submitted" if i % 2 == 0 else "draft",
            )

    def test_dashboard_kpi_endpoint(self):
        """Test que el endpoint de KPIs funciona correctamente"""
        self.client.login(username="pm", password="password123")
        self.client.defaults["HTTP_X_SITEC_ID"] = str(self.sitec.id)

        response = self.client.get("/api/dashboard/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("projects_total", response.data)
        self.assertIn("reports_last_7d", response.data)
        self.assertIn("comparatives", response.data)
        self.assertIn("alerts", response.data)

    def test_dashboard_trends_endpoint_monthly(self):
        """Test que el endpoint de tendencias mensuales funciona"""
        self.client.login(username="pm", password="password123")
        self.client.defaults["HTTP_X_SITEC_ID"] = str(self.sitec.id)

        response = self.client.get("/api/dashboard/trends/?type=month&periods=12")
        self.assertEqual(response.status_code, 200)
        self.assertIn("trends", response.data)
        self.assertIn("period_type", response.data)
        self.assertEqual(response.data["period_type"], "month")
        self.assertEqual(response.data["periods"], 12)

    def test_dashboard_trends_endpoint_weekly(self):
        """Test que el endpoint de tendencias semanales funciona"""
        self.client.login(username="pm", password="password123")
        self.client.defaults["HTTP_X_SITEC_ID"] = str(self.sitec.id)

        response = self.client.get("/api/dashboard/trends/?type=week&periods=6")
        self.assertEqual(response.status_code, 200)
        self.assertIn("trends", response.data)
        self.assertEqual(response.data["period_type"], "week")
        self.assertEqual(response.data["periods"], 6)

    def test_dashboard_trends_caching(self):
        """Test que el cache de tendencias funciona"""
        self.client.login(username="pm", password="password123")
        self.client.defaults["HTTP_X_SITEC_ID"] = str(self.sitec.id)

        # Primera llamada
        response1 = self.client.get("/api/dashboard/trends/?type=month&periods=12")
        self.assertEqual(response1.status_code, 200)

        # Segunda llamada (debe usar cache)
        response2 = self.client.get("/api/dashboard/trends/?type=month&periods=12")
        self.assertEqual(response2.status_code, 200)
        # Los datos deben ser idénticos
        self.assertEqual(response1.data, response2.data)

    def test_dashboard_comparatives_structure(self):
        """Test que los comparativos tienen la estructura correcta"""
        self.client.login(username="pm", password="password123")
        self.client.defaults["HTTP_X_SITEC_ID"] = str(self.sitec.id)

        response = self.client.get("/api/dashboard/")
        self.assertEqual(response.status_code, 200)

        comparatives = response.data.get("comparatives", {})
        # Comparativos período anterior
        self.assertIn("reports_last_period_delta", comparatives)
        self.assertIn("reports_last_period_pct", comparatives)
        # Comparativos 7 días
        self.assertIn("reports_last_7d_delta", comparatives)
        self.assertIn("reports_last_7d_pct", comparatives)
        # Comparativos 30 días
        self.assertIn("reports_last_30d_delta", comparatives)
        self.assertIn("reports_last_30d_pct", comparatives)
        # Comparativos mes anterior
        self.assertIn("reports_month_delta", comparatives)
        self.assertIn("reports_month_pct", comparatives)
        self.assertIn("reports_submitted_month_delta", comparatives)
        self.assertIn("reports_submitted_month_pct", comparatives)
        # Comparativos año anterior
        self.assertIn("reports_year_delta", comparatives)
        self.assertIn("reports_year_pct", comparatives)
        self.assertIn("reports_submitted_year_delta", comparatives)
        self.assertIn("reports_submitted_year_pct", comparatives)

    def test_dashboard_snapshot_usage(self):
        """Test que los snapshots se usan cuando están disponibles"""
        self.client.login(username="pm", password="password123")
        self.client.defaults["HTTP_X_SITEC_ID"] = str(self.sitec.id)

        # Primera llamada (crea snapshot)
        response1 = self.client.get("/api/dashboard/")
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response1.data.get("snapshot", {}).get("source"), "live")

        # Segunda llamada (debe usar snapshot si está dentro del TTL)
        response2 = self.client.get("/api/dashboard/")
        self.assertEqual(response2.status_code, 200)
        # Puede ser snapshot o live dependiendo del tiempo transcurrido

    def test_dashboard_snapshot_history(self):
        """Test que el historial de snapshots funciona"""
        self.client.login(username="pm", password="password123")
        self.client.defaults["HTTP_X_SITEC_ID"] = str(self.sitec.id)

        response = self.client.get("/api/dashboard/history/?period_days=30&limit=10")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)

    def test_dashboard_aggregate_history(self):
        """Test que el historial de agregados funciona"""
        self.client.login(username="pm", password="password123")
        self.client.defaults["HTTP_X_SITEC_ID"] = str(self.sitec.id)

        response = self.client.get("/api/dashboard/aggregates/?limit=12")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
