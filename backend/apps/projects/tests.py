from datetime import date, timedelta
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import AccessPolicy, UserProfile
from apps.companies.models import Company, Sitec

from .models import Presupuesto, Proyecto, Riesgo, Tarea

User = get_user_model()


class ProyectoTests(APITestCase):
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
        UserProfile.objects.create(
            user=self.pm,
            company=self.company,
            role="pm",
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

    def test_create_proyecto(self):
        """Verificar creación de proyecto"""
        self.client.login(username="pm", password="password123")
        response = self.client.post(
            "/api/projects/proyectos/",
            {
                "name": "Proyecto Test",
                "code": "PROJ-001",
                "site_address": "Calle Test 123",
                "start_date": "2026-01-01",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Proyecto Test")
        self.assertEqual(response.data["status"], "planning")
        self.assertEqual(response.data["code"], "PROJ-001")

    def test_create_proyecto_with_full_data(self):
        """Verificar creación de proyecto con todos los campos"""
        self.client.login(username="pm", password="password123")
        response = self.client.post(
            "/api/projects/proyectos/",
            {
                "name": "Proyecto Completo",
                "code": "PROJ-002",
                "description": "Descripción del proyecto",
                "site_address": "Calle Test 123",
                "client_name": "Cliente Test",
                "client_contact": "contacto@cliente.com",
                "start_date": "2026-01-01",
                "end_date": "2026-12-31",
                "estimated_end_date": "2026-12-31",
                "project_manager": self.pm.id,
                "status": "in_progress",
                "priority": "high",
                "progress_pct": 25,
                "budget_estimated": "1000000.00",
                "budget_actual": "250000.00",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["priority"], "high")
        self.assertEqual(response.data["progress_pct"], 25)

    def test_update_proyecto(self):
        """Verificar actualización de proyecto"""
        self.client.login(username="pm", password="password123")
        proyecto = Proyecto.objects.create(
            company=self.company,
            sitec=self.sitec,
            name="Original",
            code="PROJ-003",
            site_address="Test",
            start_date=date.today(),
        )

        response = self.client.patch(
            f"/api/projects/proyectos/{proyecto.id}/",
            {"progress_pct": 50, "status": "in_progress"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["progress_pct"], 50)
        self.assertEqual(response.data["status"], "in_progress")

    def test_complete_proyecto(self):
        """Verificar completar proyecto"""
        self.client.login(username="pm", password="password123")
        proyecto = Proyecto.objects.create(
            company=self.company,
            sitec=self.sitec,
            name="Test",
            code="PROJ-004",
            site_address="Test",
            start_date=date.today(),
            status="in_progress",
        )

        response = self.client.post(f"/api/projects/proyectos/{proyecto.id}/complete/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "completed")
        self.assertEqual(response.data["progress_pct"], 100)
        proyecto.refresh_from_db()
        self.assertIsNotNone(proyecto.completed_at)

    def test_complete_proyecto_already_completed(self):
        """Verificar error al completar proyecto ya completado"""
        self.client.login(username="pm", password="password123")
        proyecto = Proyecto.objects.create(
            company=self.company,
            sitec=self.sitec,
            name="Test",
            code="PROJ-005",
            site_address="Test",
            start_date=date.today(),
            status="completed",
        )

        response = self.client.post(f"/api/projects/proyectos/{proyecto.id}/complete/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_proyectos(self):
        """Verificar listado de proyectos"""
        self.client.login(username="pm", password="password123")
        # Crear múltiples proyectos
        for i in range(3):
            Proyecto.objects.create(
                company=self.company,
                sitec=self.sitec,
                name=f"Proyecto {i}",
                code=f"PROJ-{i:03d}",
                site_address="Test",
                start_date=date.today(),
            )

        response = self.client.get("/api/projects/proyectos/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get("results", response.data)
        self.assertGreaterEqual(len(data), 3)

    def test_filter_proyectos_by_status(self):
        """Verificar filtrado de proyectos por estado"""
        self.client.login(username="pm", password="password123")
        Proyecto.objects.create(
            company=self.company,
            sitec=self.sitec,
            name="Planning",
            code="PROJ-P",
            site_address="Test",
            start_date=date.today(),
            status="planning",
        )
        Proyecto.objects.create(
            company=self.company,
            sitec=self.sitec,
            name="In Progress",
            code="PROJ-I",
            site_address="Test",
            start_date=date.today(),
            status="in_progress",
        )

        response = self.client.get("/api/projects/proyectos/?status=planning")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get("results", response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["status"], "planning")

    def test_proyecto_is_overdue_property(self):
        """Verificar propiedad is_overdue del proyecto"""
        proyecto_overdue = Proyecto.objects.create(
            company=self.company,
            sitec=self.sitec,
            name="Overdue",
            code="PROJ-O",
            site_address="Test",
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() - timedelta(days=1),
            status="in_progress",
        )
        self.assertTrue(proyecto_overdue.is_overdue)

        proyecto_ontime = Proyecto.objects.create(
            company=self.company,
            sitec=self.sitec,
            name="On Time",
            code="PROJ-OT",
            site_address="Test",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            status="in_progress",
        )
        self.assertFalse(proyecto_ontime.is_overdue)

    def test_proyecto_days_remaining_property(self):
        """Verificar propiedad days_remaining del proyecto"""
        proyecto = Proyecto.objects.create(
            company=self.company,
            sitec=self.sitec,
            name="Test",
            code="PROJ-DR",
            site_address="Test",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10),
        )
        self.assertEqual(proyecto.days_remaining, 10)


class TareaTests(APITestCase):
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
        self.proyecto = Proyecto.objects.create(
            company=self.company,
            sitec=self.sitec,
            name="Test Project",
            code="PROJ-T",
            site_address="Test",
            start_date=date.today(),
        )
        self.client.login(username="pm", password="password123")

    def test_create_tarea(self):
        """Verificar creación de tarea"""
        response = self.client.post(
            "/api/projects/tareas/",
            {
                "project": str(self.proyecto.id),
                "title": "Instalar cableado",
                "description": "Instalar cableado en sala 1",
                "status": "pending",
                "priority": "high",
                "assigned_to": self.technician.id,
                "due_date": "2026-02-01",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Instalar cableado")
        self.assertEqual(response.data["status"], "pending")

    def test_complete_tarea(self):
        """Verificar completar tarea"""
        tarea = Tarea.objects.create(
            project=self.proyecto,
            title="Test Task",
            status="in_progress",
        )

        response = self.client.patch(
            f"/api/projects/tareas/{tarea.id}/",
            {"status": "completed"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tarea.refresh_from_db()
        self.assertEqual(tarea.status, "completed")
        self.assertIsNotNone(tarea.completed_at)

    def test_filter_tareas_by_project(self):
        """Verificar filtrado de tareas por proyecto"""
        Tarea.objects.create(
            project=self.proyecto,
            title="Task 1",
        )

        response = self.client.get(f"/api/projects/tareas/?project={self.proyecto.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)


class RiesgoTests(APITestCase):
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
        UserProfile.objects.create(user=self.pm, company=self.company, role="pm")
        AccessPolicy.objects.create(
            company=self.company, action="*", effect="allow", priority=0, is_active=True
        )
        self.proyecto = Proyecto.objects.create(
            company=self.company,
            sitec=self.sitec,
            name="Test Project",
            code="PROJ-R",
            site_address="Test",
            start_date=date.today(),
        )
        self.client.login(username="pm", password="password123")

    def test_create_riesgo(self):
        """Verificar creación de riesgo"""
        response = self.client.post(
            "/api/projects/riesgos/",
            {
                "project": str(self.proyecto.id),
                "title": "Retraso en materiales",
                "description": "Posible retraso en entrega de materiales",
                "severity": "high",
                "probability": "medium",
                "mitigation_plan": "Ordenar materiales con anticipación",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Retraso en materiales")
        self.assertEqual(response.data["severity"], "high")

    def test_update_mitigation_status(self):
        """Verificar actualización de estado de mitigación"""
        riesgo = Riesgo.objects.create(
            project=self.proyecto,
            title="Test Risk",
            description="Test",
            severity="medium",
            probability="low",
        )

        response = self.client.patch(
            f"/api/projects/riesgos/{riesgo.id}/",
            {"mitigation_status": "in_progress"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        riesgo.refresh_from_db()
        self.assertEqual(riesgo.mitigation_status, "in_progress")

    def test_filter_riesgos_by_project(self):
        """Verificar filtrado de riesgos por proyecto"""
        Riesgo.objects.create(
            project=self.proyecto,
            title="Risk 1",
            description="Test",
            severity="medium",
        )

        response = self.client.get(f"/api/projects/riesgos/?project={self.proyecto.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)


class PresupuestoTests(APITestCase):
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
        UserProfile.objects.create(user=self.pm, company=self.company, role="pm")
        AccessPolicy.objects.create(
            company=self.company, action="*", effect="allow", priority=0, is_active=True
        )
        self.proyecto = Proyecto.objects.create(
            company=self.company,
            sitec=self.sitec,
            name="Test Project",
            code="PROJ-P",
            site_address="Test",
            start_date=date.today(),
        )
        self.client.login(username="pm", password="password123")

    def test_create_presupuesto(self):
        """Verificar creación de presupuesto"""
        response = self.client.post(
            "/api/projects/presupuestos/",
            {
                "project": str(self.proyecto.id),
                "category": "materiales",
                "description": "Cableado UTP Cat6",
                "amount_estimated": "50000.00",
                "amount_actual": "48000.00",
                "notes": "Precio negociado con proveedor",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["category"], "materiales")
        self.assertEqual(response.data["amount_estimated"], "50000.00")

    def test_presupuesto_variance_property(self):
        """Verificar propiedad variance del presupuesto"""
        presupuesto = Presupuesto.objects.create(
            project=self.proyecto,
            category="materiales",
            description="Test",
            amount_estimated=100000.00,
            amount_actual=95000.00,
        )
        self.assertEqual(presupuesto.variance, -5000.00)

    def test_filter_presupuestos_by_project(self):
        """Verificar filtrado de presupuestos por proyecto"""
        Presupuesto.objects.create(
            project=self.proyecto,
            category="materiales",
            description="Test",
            amount_estimated=10000.00,
        )

        response = self.client.get(
            f"/api/projects/presupuestos/?project={self.proyecto.id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
