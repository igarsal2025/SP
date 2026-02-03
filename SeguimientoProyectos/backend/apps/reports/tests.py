from datetime import date, timedelta
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import AccessPolicy, UserProfile
from apps.companies.models import Company, Sitec

from .models import Evidencia, Incidente, ReporteSemanal

User = get_user_model()


class ReporteSemanalTests(APITestCase):
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
        self.supervisor = User.objects.create_user(
            username="supervisor",
            email="supervisor@sitec.mx",
            password="password123",
        )
        UserProfile.objects.create(
            user=self.technician,
            company=self.company,
            role="tecnico",
        )
        UserProfile.objects.create(
            user=self.supervisor,
            company=self.company,
            role="supervisor",
        )
        AccessPolicy.objects.create(
            company=self.company,
            action="*",
            effect="allow",
            priority=0,
            is_active=True,
        )

    def test_create_reporte(self):
        """Verificar creación de reporte semanal"""
        self.client.login(username="tecnico", password="password123")
        response = self.client.post(
            "/api/reports/reportes/",
            {
                "project_name": "Proyecto Test",
                "week_start": "2026-01-01",
                "site_address": "Calle Test 123",
                "progress_pct": 50,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["project_name"], "Proyecto Test")
        self.assertEqual(response.data["status"], "draft")
        self.assertEqual(response.data["technician"], self.technician.id)

    def test_create_reporte_with_full_data(self):
        """Verificar creación de reporte con todos los campos"""
        self.client.login(username="tecnico", password="password123")
        response = self.client.post(
            "/api/reports/reportes/",
            {
                "project_name": "Proyecto Completo",
                "week_start": "2026-01-01",
                "site_address": "Calle Test 123",
                "progress_pct": 75,
                "schedule_status": "on_time",
                "cabling_nodes_total": 100,
                "cabling_nodes_ok": 95,
                "racks_installed": 5,
                "security_devices": 10,
                "tests_passed": True,
                "incidents": True,
                "incidents_count": 2,
                "incidents_severity": "medium",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["cabling_nodes_total"], 100)
        self.assertEqual(response.data["tests_passed"], True)
        self.assertEqual(response.data["incidents"], True)

    def test_submit_reporte(self):
        """Verificar envío de reporte"""
        self.client.login(username="tecnico", password="password123")
        reporte = ReporteSemanal.objects.create(
            company=self.company,
            sitec=self.sitec,
            technician=self.technician,
            project_name="Test",
            week_start="2026-01-01",
            site_address="Test",
            progress_pct=50,
        )
        response = self.client.post(f"/api/reports/reportes/{reporte.id}/submit/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "submitted")
        reporte.refresh_from_db()
        self.assertIsNotNone(reporte.submitted_at)

    def test_submit_reporte_not_draft(self):
        """Verificar que solo borradores pueden enviarse"""
        self.client.login(username="tecnico", password="password123")
        reporte = ReporteSemanal.objects.create(
            company=self.company,
            sitec=self.sitec,
            technician=self.technician,
            project_name="Test",
            week_start="2026-01-01",
            site_address="Test",
            progress_pct=50,
            status="submitted",
        )
        response = self.client.post(f"/api/reports/reportes/{reporte.id}/submit/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_approve_reporte(self):
        """Verificar aprobación de reporte"""
        self.client.login(username="supervisor", password="password123")
        reporte = ReporteSemanal.objects.create(
            company=self.company,
            sitec=self.sitec,
            technician=self.technician,
            project_name="Test",
            week_start="2026-01-01",
            site_address="Test",
            progress_pct=50,
            status="submitted",
        )
        response = self.client.post(f"/api/reports/reportes/{reporte.id}/approve/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "approved")
        reporte.refresh_from_db()
        self.assertIsNotNone(reporte.approved_at)
        self.assertEqual(reporte.supervisor, self.supervisor)

    def test_approve_reporte_not_submitted(self):
        """Verificar que solo reportes enviados pueden aprobarse"""
        self.client.login(username="supervisor", password="password123")
        reporte = ReporteSemanal.objects.create(
            company=self.company,
            sitec=self.sitec,
            technician=self.technician,
            project_name="Test",
            week_start="2026-01-01",
            site_address="Test",
            progress_pct=50,
            status="draft",
        )
        response = self.client.post(f"/api/reports/reportes/{reporte.id}/approve/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_reportes(self):
        """Verificar listado de reportes"""
        self.client.login(username="tecnico", password="password123")
        # Crear múltiples reportes
        for i in range(3):
            ReporteSemanal.objects.create(
                company=self.company,
                sitec=self.sitec,
                technician=self.technician,
                project_name=f"Proyecto {i}",
                week_start=date.today() - timedelta(weeks=i),
                site_address="Test",
                progress_pct=50,
            )

        response = self.client.get("/api/reports/reportes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get("results", response.data)
        self.assertGreaterEqual(len(data), 3)

    def test_filter_reportes_by_status(self):
        """Verificar filtrado de reportes por estado"""
        self.client.login(username="tecnico", password="password123")
        ReporteSemanal.objects.create(
            company=self.company,
            sitec=self.sitec,
            technician=self.technician,
            project_name="Draft",
            week_start="2026-01-01",
            site_address="Test",
            progress_pct=50,
            status="draft",
        )
        ReporteSemanal.objects.create(
            company=self.company,
            sitec=self.sitec,
            technician=self.technician,
            project_name="Submitted",
            week_start="2026-01-01",
            site_address="Test",
            progress_pct=50,
            status="submitted",
        )

        response = self.client.get("/api/reports/reportes/?status=draft")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get("results", response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["status"], "draft")

    def test_filter_reportes_by_week(self):
        """Verificar filtrado de reportes por semana"""
        self.client.login(username="tecnico", password="password123")
        week_start = date.today()
        ReporteSemanal.objects.create(
            company=self.company,
            sitec=self.sitec,
            technician=self.technician,
            project_name="This Week",
            week_start=week_start,
            site_address="Test",
            progress_pct=50,
        )

        response = self.client.get(f"/api/reports/reportes/?week_start={week_start}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get("results", response.data)
        self.assertGreaterEqual(len(data), 1)

    def test_update_reporte(self):
        """Verificar actualización de reporte"""
        self.client.login(username="tecnico", password="password123")
        reporte = ReporteSemanal.objects.create(
            company=self.company,
            sitec=self.sitec,
            technician=self.technician,
            project_name="Original",
            week_start="2026-01-01",
            site_address="Test",
            progress_pct=50,
        )

        response = self.client.patch(
            f"/api/reports/reportes/{reporte.id}/",
            {"progress_pct": 75, "project_name": "Updated"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["progress_pct"], 75)
        self.assertEqual(response.data["project_name"], "Updated")

    def test_reporte_is_complete_property(self):
        """Verificar propiedad is_complete del reporte"""
        reporte = ReporteSemanal.objects.create(
            company=self.company,
            sitec=self.sitec,
            technician=self.technician,
            project_name="Complete",
            week_start="2026-01-01",
            site_address="Test Address",
            progress_pct=50,
        )
        self.assertTrue(reporte.is_complete)

        reporte_incomplete = ReporteSemanal.objects.create(
            company=self.company,
            sitec=self.sitec,
            technician=self.technician,
            project_name="",
            week_start="2026-01-01",
            site_address="Test",
            progress_pct=50,
        )
        self.assertFalse(reporte_incomplete.is_complete)


class EvidenciaTests(APITestCase):
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
        self.reporte = ReporteSemanal.objects.create(
            company=self.company,
            sitec=self.sitec,
            technician=self.user,
            project_name="Test",
            week_start="2026-01-01",
            site_address="Test",
            progress_pct=50,
        )
        self.client.login(username="tecnico", password="password123")

    def test_create_evidencia(self):
        """Verificar creación de evidencia"""
        response = self.client.post(
            "/api/reports/evidencias/",
            {
                "reporte": str(self.reporte.id),
                "tipo": "photo",
                "file_path": "/media/evidencias/photo1.jpg",
                "file_name": "photo1.jpg",
                "file_size": 1024000,
                "mime_type": "image/jpeg",
                "description": "Foto de instalación",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["tipo"], "photo")
        self.assertEqual(response.data["file_name"], "photo1.jpg")

    def test_create_evidencia_with_geolocation(self):
        """Verificar creación de evidencia con geolocalización"""
        response = self.client.post(
            "/api/reports/evidencias/",
            {
                "reporte": str(self.reporte.id),
                "tipo": "photo",
                "file_path": "/media/evidencias/photo1.jpg",
                "file_name": "photo1.jpg",
                "latitude": "19.432608",
                "longitude": "-99.133209",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.data["latitude"])
        self.assertIsNotNone(response.data["longitude"])

    def test_filter_evidencias_by_reporte(self):
        """Verificar filtrado de evidencias por reporte"""
        Evidencia.objects.create(
            reporte=self.reporte,
            tipo="photo",
            file_path="/media/photo1.jpg",
            file_name="photo1.jpg",
        )

        response = self.client.get(f"/api/reports/evidencias/?reporte={self.reporte.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)


class IncidenteTests(APITestCase):
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
        self.reporte = ReporteSemanal.objects.create(
            company=self.company,
            sitec=self.sitec,
            technician=self.user,
            project_name="Test",
            week_start="2026-01-01",
            site_address="Test",
            progress_pct=50,
        )
        self.client.login(username="tecnico", password="password123")

    def test_create_incidente(self):
        """Verificar creación de incidente"""
        response = self.client.post(
            "/api/reports/incidentes/",
            {
                "reporte": str(self.reporte.id),
                "title": "Fallo en cableado",
                "description": "Se detectó fallo en el cableado de la sala 3",
                "severity": "high",
                "mitigation_plan": "Revisar y reemplazar cableado afectado",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Fallo en cableado")
        self.assertEqual(response.data["severity"], "high")
        self.assertFalse(response.data["resolved"])

    def test_resolve_incidente(self):
        """Verificar resolución de incidente"""
        incidente = Incidente.objects.create(
            reporte=self.reporte,
            title="Test Incident",
            description="Test",
            severity="medium",
        )

        response = self.client.patch(
            f"/api/reports/incidentes/{incidente.id}/",
            {"resolved": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        incidente.refresh_from_db()
        self.assertTrue(incidente.resolved)
        self.assertIsNotNone(incidente.resolved_at)

    def test_filter_incidentes_by_reporte(self):
        """Verificar filtrado de incidentes por reporte"""
        Incidente.objects.create(
            reporte=self.reporte,
            title="Test",
            description="Test",
            severity="medium",
        )

        response = self.client.get(f"/api/reports/incidentes/?reporte={self.reporte.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
