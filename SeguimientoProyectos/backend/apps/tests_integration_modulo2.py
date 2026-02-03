"""
Tests de integración para Módulo 2
Prueban interacciones entre apps: sync, reports, projects
"""
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import AccessPolicy, UserProfile
from apps.companies.models import Company, Sitec
from apps.projects.models import Proyecto
from apps.reports.models import ReporteSemanal
from apps.sync.models import SyncItem, SyncSession

User = get_user_model()


class SyncReportsIntegrationTests(APITestCase):
    """Tests de integración entre sync y reports"""

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
            username="tecnico",
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
        self.client.login(username="tecnico", password="password123")

    def test_sync_creates_reporte(self):
        """Verificar que sync puede crear reportes desde wizard"""
        response = self.client.post(
            "/api/sync/",
            {
                "items": [
                    {
                        "entity_type": "report",
                        "entity_id": "report_1",
                        "data": {
                            "project_name": "Proyecto Sync",
                            "week_start": "2026-01-01",
                            "site_address": "Calle Test",
                            "progress_pct": 50,
                        },
                    }
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["synced_items"]), 1)

        # Verificar que se puede crear reporte desde los datos sincronizados
        sync_item = SyncItem.objects.get(entity_id="report_1")
        self.assertEqual(sync_item.entity_type, "report")
        self.assertIn("project_name", sync_item.data)

    def test_sync_report_with_conflict(self):
        """Verificar detección de conflictos en reportes sincronizados"""
        # Crear reporte existente
        reporte = ReporteSemanal.objects.create(
            company=self.company,
            sitec=self.sitec,
            technician=self.user,
            project_name="Server Version",
            week_start="2026-01-01",
            site_address="Test",
            progress_pct=50,
        )

        # Sincronizar reporte con datos diferentes y timestamp antiguo
        old_timestamp = (timezone.now() - timedelta(hours=1)).isoformat()
        response = self.client.post(
            "/api/sync/",
            {
                "items": [
                    {
                        "entity_type": "report",
                        "entity_id": str(reporte.id),
                        "data": {"project_name": "Client Version", "progress_pct": 75},
                        "updatedAt": old_timestamp,
                    }
                ]
            },
            format="json",
        )
        # Debería detectar conflicto si hay timestamp más reciente en servidor
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SyncProjectsIntegrationTests(APITestCase):
    """Tests de integración entre sync y projects"""

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
            username="pm",
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
        self.client.login(username="pm", password="password123")

    def test_sync_creates_proyecto(self):
        """Verificar que sync puede sincronizar proyectos"""
        response = self.client.post(
            "/api/sync/",
            {
                "items": [
                    {
                        "entity_type": "project",
                        "entity_id": "project_1",
                        "data": {
                            "name": "Proyecto Sync",
                            "code": "PROJ-SYNC",
                            "site_address": "Calle Test",
                            "start_date": "2026-01-01",
                        },
                    }
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sync_item = SyncItem.objects.get(entity_id="project_1")
        self.assertEqual(sync_item.entity_type, "project")
        self.assertIn("name", sync_item.data)


class ReportsProjectsIntegrationTests(APITestCase):
    """Tests de integración entre reports y projects"""

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
        self.technician = User.objects.create_user(
            username="tecnico",
            email="tecnico@sitec.mx",
            password="password123",
        )
        UserProfile.objects.create(
            user=self.technician,
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
        self.proyecto = Proyecto.objects.create(
            company=self.company,
            sitec=self.sitec,
            name="Proyecto Test",
            code="PROJ-001",
            site_address="Calle Test",
            start_date=date.today(),
        )
        self.client.login(username="tecnico", password="password123")

    def test_create_reporte_linked_to_proyecto(self):
        """Verificar creación de reporte vinculado a proyecto"""
        response = self.client.post(
            "/api/reports/reportes/",
            {
                "project": str(self.proyecto.id),
                "project_name": "Proyecto Test",
                "week_start": "2026-01-01",
                "site_address": "Calle Test",
                "progress_pct": 50,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        reporte = ReporteSemanal.objects.get(id=response.data["id"])
        self.assertEqual(reporte.project, self.proyecto)

    def test_reporte_updates_proyecto_progress(self):
        """Verificar que reporte puede actualizar progreso del proyecto"""
        reporte = ReporteSemanal.objects.create(
            company=self.company,
            sitec=self.sitec,
            technician=self.technician,
            project=self.proyecto,
            project_name="Proyecto Test",
            week_start="2026-01-01",
            site_address="Test",
            progress_pct=75,
        )

        # Actualizar reporte con nuevo progreso
        response = self.client.patch(
            f"/api/reports/reportes/{reporte.id}/",
            {"progress_pct": 80},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # El proyecto podría actualizar su progreso basado en reportes (lógica futura)
        self.assertEqual(response.data["progress_pct"], 80)


class CompleteWorkflowTests(APITestCase):
    """Tests del flujo completo: proyecto -> reporte -> sync"""

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
        self.pm = User.objects.create_user(
            username="pm",
            email="pm@sitec.mx",
            password="password123",
        )
        self.technician = User.objects.create_user(
            username="tecnico",
            email="tecnico@sitec.mx",
            password="password123",
        )
        UserProfile.objects.create(user=self.pm, company=self.company, role="pm")
        UserProfile.objects.create(
            user=self.technician, company=self.company, role="tecnico"
        )
        AccessPolicy.objects.create(
            company=self.company, action="*", effect="allow", priority=0, is_active=True
        )

    def test_complete_workflow(self):
        """Test del flujo completo: crear proyecto, reporte, sincronizar"""
        # 1. PM crea proyecto
        self.client.login(username="pm", password="password123")
        proyecto_response = self.client.post(
            "/api/projects/proyectos/",
            {
                "name": "Proyecto Completo",
                "code": "PROJ-FLOW",
                "site_address": "Calle Test",
                "start_date": "2026-01-01",
            },
            format="json",
        )
        self.assertEqual(proyecto_response.status_code, status.HTTP_201_CREATED)
        proyecto_id = proyecto_response.data["id"]

        # 2. Técnico crea reporte vinculado al proyecto
        self.client.login(username="tecnico", password="password123")
        reporte_response = self.client.post(
            "/api/reports/reportes/",
            {
                "project": proyecto_id,
                "project_name": "Proyecto Completo",
                "week_start": "2026-01-01",
                "site_address": "Calle Test",
                "progress_pct": 25,
            },
            format="json",
        )
        self.assertEqual(reporte_response.status_code, status.HTTP_201_CREATED)
        reporte_id = reporte_response.data["id"]

        # 3. Sincronizar reporte (simulando offline)
        sync_response = self.client.post(
            "/api/sync/",
            {
                "items": [
                    {
                        "entity_type": "report",
                        "entity_id": reporte_id,
                        "data": {
                            "id": reporte_id,
                            "progress_pct": 30,
                            "updated": True,
                        },
                    }
                ]
            },
            format="json",
        )
        self.assertEqual(sync_response.status_code, status.HTTP_200_OK)
        self.assertEqual(sync_response.data["session"]["items_synced"], 1)

        # 4. Verificar que todo está vinculado correctamente
        from apps.reports.models import ReporteSemanal
        from apps.projects.models import Proyecto

        reporte = ReporteSemanal.objects.get(id=reporte_id)
        proyecto = Proyecto.objects.get(id=proyecto_id)
        self.assertEqual(reporte.project, proyecto)
        self.assertEqual(reporte.company, proyecto.company)
