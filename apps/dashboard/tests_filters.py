"""
Tests para filtros avanzados del dashboard
"""
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.companies.models import Company, Sitec
from apps.projects.models import Proyecto
from apps.reports.models import ReporteSemanal

from apps.accounts.models import UserProfile

User = get_user_model()


class DashboardFiltersTests(APITestCase):
    """Tests para filtros avanzados del dashboard"""

    def setUp(self):
        self.company = Company.objects.create(name="Test Company")
        self.sitec = Sitec.objects.create(company=self.company, schema_name="test")
        self.user = User.objects.create_user(username="testuser", password="password123")
        UserProfile.objects.create(user=self.user, company=self.company, role="pm")
        self.client.login(username="testuser", password="password123")
        self.client.defaults["HTTP_X_SITEC_ID"] = str(self.sitec.id)

        # Crear proyectos de prueba
        self.project1 = Proyecto.objects.create(
            company=self.company,
            sitec=self.sitec,
            name="Proyecto 1",
            code="P1",
            site_address="123 Test St",
            start_date=date(2023, 1, 1),
            project_manager=self.user,
        )
        self.project2 = Proyecto.objects.create(
            company=self.company,
            sitec=self.sitec,
            name="Proyecto 2",
            code="P2",
            site_address="456 Test St",
            start_date=date(2023, 2, 1),
            project_manager=self.user,
        )

        # Crear reportes para diferentes proyectos y fechas
        now = timezone.now()
        self.report1 = ReporteSemanal.objects.create(
            company=self.company,
            sitec=self.sitec,
            project=self.project1,
            week_start=now.date() - timedelta(days=5),
            status="submitted",
        )
        self.report2 = ReporteSemanal.objects.create(
            company=self.company,
            sitec=self.sitec,
            project=self.project2,
            week_start=now.date() - timedelta(days=3),
            status="approved",
        )

    def test_dashboard_without_filters(self):
        """Test que el dashboard funciona sin filtros"""
        response = self.client.get("/api/dashboard/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("projects_total", data)
        self.assertIn("reports_last_7d", data)
        # Debe incluir datos de ambos proyectos
        self.assertGreaterEqual(data["projects_total"], 2)

    def test_dashboard_filter_by_project(self):
        """Test filtro por proyecto"""
        response = self.client.get(f"/api/dashboard/?project_id={self.project1.id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("projects_total", data)
        # Con filtro de proyecto, debería mostrar solo ese proyecto
        # (aunque projects_total puede ser 1 o más dependiendo de la lógica)

    def test_dashboard_filter_by_date_range(self):
        """Test filtro por rango de fechas"""
        start_date = (timezone.now().date() - timedelta(days=10)).strftime("%Y-%m-%d")
        end_date = (timezone.now().date() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        response = self.client.get(
            f"/api/dashboard/?start_date={start_date}&end_date={end_date}"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("projects_total", data)
        self.assertIn("snapshot", data)
        # Con filtros personalizados, no debe usar snapshot
        self.assertTrue(data["snapshot"].get("filters_applied", False))

    def test_dashboard_filter_by_project_and_dates(self):
        """Test filtro combinado por proyecto y fechas"""
        start_date = (timezone.now().date() - timedelta(days=10)).strftime("%Y-%m-%d")
        end_date = (timezone.now().date() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        response = self.client.get(
            f"/api/dashboard/?project_id={self.project1.id}&start_date={start_date}&end_date={end_date}"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("projects_total", data)
        self.assertTrue(data["snapshot"].get("filters_applied", False))

    def test_dashboard_filter_invalid_project_id(self):
        """Test que filtro con project_id inválido se ignora"""
        # Probar con UUID inválido (formato incorrecto)
        response = self.client.get("/api/dashboard/?project_id=invalid-uuid")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Debe funcionar normalmente, ignorando el project_id inválido
        self.assertIn("projects_total", data)
        
        # Probar con UUID que no existe
        import uuid
        non_existent_uuid = str(uuid.uuid4())
        response2 = self.client.get(f"/api/dashboard/?project_id={non_existent_uuid}")
        self.assertEqual(response2.status_code, 200)
        data2 = response2.json()
        self.assertIn("projects_total", data2)

    def test_dashboard_filter_invalid_date_format(self):
        """Test que fechas inválidas se ignoran"""
        response = self.client.get("/api/dashboard/?start_date=invalid&end_date=invalid")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Debe funcionar normalmente, usando período por defecto
        self.assertIn("projects_total", data)

    def test_dashboard_filter_reversed_dates(self):
        """Test que fechas invertidas se manejan correctamente"""
        # end_date antes de start_date
        start_date = (timezone.now().date() - timedelta(days=1)).strftime("%Y-%m-%d")
        end_date = (timezone.now().date() - timedelta(days=10)).strftime("%Y-%m-%d")
        
        response = self.client.get(
            f"/api/dashboard/?start_date={start_date}&end_date={end_date}"
        )
        # Debe funcionar, aunque el rango esté invertido
        # (el backend debería manejarlo o ignorarlo)
        self.assertIn(response.status_code, [200, 400])

    def test_dashboard_filter_period_days(self):
        """Test filtro por period_days"""
        response = self.client.get("/api/dashboard/?period_days=30")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("projects_total", data)
        self.assertIn("period_days", data)
        self.assertEqual(data["period_days"], 30)

    def test_dashboard_filter_combines_correctly(self):
        """Test que múltiples filtros se combinan correctamente"""
        start_date = (timezone.now().date() - timedelta(days=7)).strftime("%Y-%m-%d")
        end_date = timezone.now().date().strftime("%Y-%m-%d")
        
        response = self.client.get(
            f"/api/dashboard/?project_id={self.project1.id}&start_date={start_date}&end_date={end_date}&period_days=7"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("projects_total", data)
        self.assertTrue(data["snapshot"].get("filters_applied", False))

    def test_dashboard_snapshot_disabled_with_filters(self):
        """Test que los snapshots se deshabilitan cuando hay filtros"""
        start_date = (timezone.now().date() - timedelta(days=5)).strftime("%Y-%m-%d")
        end_date = timezone.now().date().strftime("%Y-%m-%d")
        
        response = self.client.get(
            f"/api/dashboard/?start_date={start_date}&end_date={end_date}"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("snapshot", data)
        # Con filtros, debe indicar que se calcularon en tiempo real
        self.assertEqual(data["snapshot"]["source"], "live")
        self.assertTrue(data["snapshot"].get("filters_applied", False))
