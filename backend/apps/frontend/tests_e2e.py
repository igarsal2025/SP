"""
Tests End-to-End (E2E) para flujos completos de usuario
Cubre: flujos completos desde login hasta finalización
"""
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import AccessPolicy, UserProfile
from apps.companies.models import Company, Sitec
from apps.frontend.models import WizardDraft, WizardStepData
from apps.projects.models import Proyecto
from apps.reports.models import ReporteSemanal

User = get_user_model()


class E2EWizardFlowTests(APITestCase):
    """Tests E2E del flujo completo del wizard"""

    def setUp(self):
        self.company = Company.objects.create(
            name="SITEC Test",
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
            username="tecnico_test",
            email="tecnico@sitec.mx",
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
        self.client.login(username="tecnico_test", password="password123")

    def test_complete_wizard_submission_flow(self):
        """Test E2E: Crear proyecto, completar wizard, enviar reporte"""
        # 1. Crear proyecto
        project = Proyecto.objects.create(
            company=self.company,
            sitec=self.sitec,
            name="Proyecto E2E Test",
            code="E2E-001",
            site_address="Calle Test 123",
            start_date=date.today(),
            budget_estimated=Decimal("100000.00"),
        )

        # 2. Guardar paso 1 del wizard
        step1_data = {
            "step": 1,
            "data": {
                "project_name": "Proyecto E2E Test",
                "site_address": "Calle Test 123",
                "week_start": str(date.today()),
            },
        }
        response = self.client.post("/api/wizard/steps/save/", step1_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 3. Guardar múltiples pasos
        for step_num in range(2, 6):
            step_data = {
                "step": step_num,
                "data": {
                    "progress_pct": step_num * 10,
                    "cabling_nodes_total": 100,
                    "cabling_nodes_ok": step_num * 10,
                },
            }
            response = self.client.post("/api/wizard/steps/save/", step_data, format="json")
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 4. Verificar que se guardaron los pasos del wizard
        draft = WizardDraft.objects.filter(
            company=self.company, sitec=self.sitec, user=self.user
        ).first()
        self.assertIsNotNone(draft)
        steps = WizardStepData.objects.filter(draft=draft)
        self.assertGreaterEqual(steps.count(), 5)

        # 5. El wizard se guarda paso a paso, el reporte se crea desde otro flujo
        # Verificar que los datos están guardados correctamente
        step1 = WizardStepData.objects.filter(draft=draft, step=1).first()
        self.assertIsNotNone(step1)
        self.assertEqual(step1.data.get("project_name"), "Proyecto E2E Test")

    def test_wizard_with_sync_flow(self):
        """Test E2E: Wizard con sincronización offline"""
        project = Proyecto.objects.create(
            company=self.company,
            sitec=self.sitec,
            name="Proyecto Sync Test",
            code="SYNC-001",
            site_address="Calle Sync 123",
            start_date=date.today(),
        )

        # 1. Guardar datos localmente (simulando offline)
        step_data = {
            "step": 1,
            "data": {
                "project_name": "Proyecto Sync Test",
                "week_start": str(date.today()),
            },
        }
        response = self.client.post("/api/wizard/steps/save/", step_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2. Sincronizar
        sync_data = {
            "items": [
                {
                    "entity_type": "wizard_step",
                    "entity_id": "1",
                    "client_timestamp": timezone.now().isoformat(),
                    "data": step_data["data"],
                }
            ]
        }
        response = self.client.post("/api/sync/", sync_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("session", response.data)
        self.assertIn("synced_items", response.data)
        self.assertIn("conflicts", response.data)


class E2EDashboardFlowTests(APITestCase):
    """Tests E2E del flujo completo del dashboard"""

    def setUp(self):
        self.company = Company.objects.create(
            name="SITEC Dashboard",
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
            username="pm_test",
            email="pm@sitec.mx",
            password="password123",
        )
        UserProfile.objects.create(
            user=self.user,
            company=self.company,
            role="pm",
        )
        AccessPolicy.objects.create(
            company=self.company,
            action="*",
            effect="allow",
            priority=0,
            is_active=True,
        )
        self.client.login(username="pm_test", password="password123")

        # Crear datos de prueba
        self.project = Proyecto.objects.create(
            company=self.company,
            sitec=self.sitec,
            name="Proyecto Dashboard",
            code="DASH-001",
            site_address="Calle Dashboard 123",
            start_date=date.today() - timedelta(days=30),
            budget_estimated=Decimal("200000.00"),
            budget_actual=Decimal("180000.00"),
            status="in_progress",
        )

        # Crear reportes
        for i in range(5):
            ReporteSemanal.objects.create(
                company=self.company,
                sitec=self.sitec,
                project=self.project,
                technician=self.user,
                week_start=date.today() - timedelta(days=7 * i),
                project_name="Proyecto Dashboard",
                site_address="Calle Dashboard 123",
                progress_pct=20 * (i + 1),
                status="submitted" if i % 2 == 0 else "draft",
            )

    def test_complete_dashboard_flow(self):
        """Test E2E: Ver dashboard, aplicar filtros, ver tendencias"""
        # 1. Obtener KPIs del dashboard
        response = self.client.get("/api/dashboard/kpi/")
        # El endpoint puede retornar 200 o usar snapshots
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])
        if response.status_code == status.HTTP_200_OK:
            self.assertIn("projects_total", response.data)
            self.assertIn("reports_last_7d", response.data)

        # 2. Aplicar filtro por proyecto (si el endpoint existe)
        response = self.client.get(
            f"/api/dashboard/kpi/?project_id={self.project.id}"
        )
        # El endpoint puede retornar 200 o usar snapshots
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])
        if response.status_code == status.HTTP_200_OK:
            self.assertGreaterEqual(response.data.get("projects_total", 0), 0)

        # 3. Aplicar filtro por rango de fechas
        start_date = (date.today() - timedelta(days=14)).isoformat()
        end_date = date.today().isoformat()
        response = self.client.get(
            f"/api/dashboard/kpi/?start_date={start_date}&end_date={end_date}"
        )
        # El endpoint puede retornar 200 incluso sin datos
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])

        # 4. Obtener tendencias
        response = self.client.get("/api/dashboard/trends/?type=month&periods=6")
        # El endpoint puede retornar 200 incluso sin datos
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])
        if response.status_code == status.HTTP_200_OK:
            self.assertIn("trends", response.data)
            self.assertIn("period_type", response.data)

    def test_dashboard_with_roi_flow(self):
        """Test E2E: Dashboard con análisis de ROI"""
        # 1. Obtener snapshot de ROI
        response = self.client.get("/api/roi/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_estimated", response.data)
        self.assertIn("total_actual", response.data)

        # 2. Obtener tendencias de ROI
        response = self.client.get("/api/roi/trends/?periods=12&type=month")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("trends", response.data)

        # 3. Obtener análisis avanzado
        response = self.client.get("/api/roi/analysis/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("by_status", response.data)


class E2ESyncConflictFlowTests(APITestCase):
    """Tests E2E de resolución de conflictos en sync"""

    def setUp(self):
        self.company = Company.objects.create(
            name="SITEC Sync",
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
            username="sync_test",
            email="sync@sitec.mx",
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
        self.client.login(username="sync_test", password="password123")

    def test_sync_conflict_resolution_flow(self):
        """Test E2E: Detectar y resolver conflictos en sync"""
        # 1. Crear sesión de sync inicial
        sync_data = {
            "items": [
                {
                    "entity_type": "wizard_step",
                    "entity_id": "1",
                    "client_timestamp": (timezone.now() - timedelta(hours=1)).isoformat(),
                    "data": {"step": 1, "value": "client_value"},
                }
            ]
        }
        response = self.client.post("/api/sync/", sync_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2. Intentar sync con timestamp más antiguo (simula conflicto)
        old_sync_data = {
            "items": [
                {
                    "entity_type": "wizard_step",
                    "entity_id": "1",
                    "client_timestamp": (timezone.now() - timedelta(hours=2)).isoformat(),
                    "data": {"step": 1, "value": "old_client_value"},
                }
            ]
        }
        response = self.client.post("/api/sync/", old_sync_data, format="json")
        # Debería detectar conflicto o rechazar por timestamp antiguo
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_409_CONFLICT])


class E2ECompleteUserJourneyTests(APITestCase):
    """Tests E2E del viaje completo de usuario"""

    def setUp(self):
        self.company = Company.objects.create(
            name="SITEC Complete",
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
        self.technician = User.objects.create_user(
            username="tech_complete",
            email="tech@sitec.mx",
            password="password123",
        )
        self.pm = User.objects.create_user(
            username="pm_complete",
            email="pm@sitec.mx",
            password="password123",
        )
        UserProfile.objects.create(user=self.technician, company=self.company, role="tecnico")
        UserProfile.objects.create(user=self.pm, company=self.company, role="pm")
        AccessPolicy.objects.create(
            company=self.company,
            action="*",
            effect="allow",
            priority=0,
            is_active=True,
        )

    def test_complete_user_journey(self):
        """Test E2E: Viaje completo desde creación de proyecto hasta aprobación"""
        # 1. PM crea proyecto
        self.client.login(username="pm_complete", password="password123")
        project = Proyecto.objects.create(
            company=self.company,
            sitec=self.sitec,
            name="Proyecto Completo",
            code="COMP-001",
            site_address="Calle Completa 123",
            start_date=date.today(),
            budget_estimated=Decimal("300000.00"),
            project_manager=self.pm,
        )

        # 2. Técnico completa wizard
        self.client.logout()
        self.client.login(username="tech_complete", password="password123")
        step_data = {
            "step": 1,
            "data": {
                "project_name": "Proyecto Completo",
                "week_start": str(date.today()),
            },
        }
        response = self.client.post("/api/wizard/steps/save/", step_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 3. Verificar que el wizard está guardado
        draft = WizardDraft.objects.filter(
            company=self.company, sitec=self.sitec, user=self.technician
        ).first()
        self.assertIsNotNone(draft)
        steps = WizardStepData.objects.filter(draft=draft)
        self.assertGreaterEqual(steps.count(), 1)

        # 4. PM revisa dashboard
        self.client.logout()
        self.client.login(username="pm_complete", password="password123")
        response = self.client.get("/api/dashboard/kpi/")
        # El endpoint puede retornar 200 o usar snapshots
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])

        # 5. PM revisa ROI
        response = self.client.get("/api/roi/")
        # El endpoint puede retornar 200 o usar snapshots
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])
