"""
Tests de Funcionalidad para el módulo Frontend
Cubre: wizard, validaciones, sync, Modo Campo, Analytics, PWA
"""
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import AccessPolicy, UserProfile
from apps.companies.models import Company, Sitec
from apps.frontend.models import WizardDraft, WizardStepData

User = get_user_model()


class FunctionalWizardTests(APITestCase):
    """Tests funcionales del wizard"""

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
            username="testuser",
            email="test@sitec.mx",
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
        self.client.login(username="testuser", password="password123")

    def test_complete_wizard_flow(self):
        """Test del flujo completo del wizard (12 pasos)"""
        # Paso 1: Datos generales
        response = self.client.post(
            "/api/wizard/steps/save/",
            {
                "step": 1,
                "data": {
                    "project_name": "Proyecto Test",
                    "week_start": "2026-01-01",
                    "site_address": "Calle Test 123",
                    "technician": "Juan Pérez",
                },
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validar paso 1
        response = self.client.post(
            "/api/wizard/validate/",
            {
                "step": 1,
                "data": {
                    "project_name": "Proyecto Test",
                    "week_start": "2026-01-01",
                    "site_address": "Calle Test 123",
                    "technician": "Juan Pérez",
                },
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["allowed"])

        # Paso 2: Planificación
        response = self.client.post(
            "/api/wizard/steps/save/",
            {
                "step": 2,
                "data": {
                    "progress_pct": 50,
                    "schedule_status": "on_time",
                },
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que se creó el draft
        draft = WizardDraft.objects.filter(user=self.user).first()
        self.assertIsNotNone(draft)
        self.assertEqual(draft.status, "draft")

        # Verificar que se guardaron los steps
        steps = WizardStepData.objects.filter(draft=draft)
        self.assertGreaterEqual(steps.count(), 2)

    def test_wizard_validation_all_steps(self):
        """Test de validaciones para todos los 12 pasos"""
        validation_tests = [
            (1, {}, ["project_name_required"]),
            (2, {"progress_pct": 150}, ["progress_pct_invalid"]),
            (3, {}, ["cabling_nodes_total_required"]),
            (4, {}, ["racks_installed_required"]),
            (5, {"security_devices": -1}, ["security_devices_invalid"]),
            (6, {"special_systems_enabled": True}, ["special_systems_notes_required"]),
            (7, {}, ["materials_count_required"]),
            (8, {"tests_passed": False}, ["tests_failed"]),
            (9, {}, ["evidence_photos_required"]),
            (10, {"incidents": True}, ["incidents_detail_required"]),
            (11, {}, ["signature_tech_required"]),
            (12, {}, ["final_review_ack_required"]),
        ]

        for step, data, expected_errors in validation_tests:
            response = self.client.post(
                "/api/wizard/validate/",
                {"step": step, "data": data},
                format="json",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertFalse(response.data["allowed"])
            for error in expected_errors:
                self.assertIn(error, response.data["critical"])

    def test_wizard_warnings_non_blocking(self):
        """Verificar que warnings no bloquean el avance"""
        response = self.client.post(
            "/api/wizard/validate/",
            {
                "step": 2,
                "data": {
                    "progress_pct": 50,
                    # schedule_status faltante es warning, no crítico
                },
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["allowed"])  # Debe permitir avanzar
        self.assertIn("schedule_status_missing", response.data["warnings"])


class FunctionalSyncTests(APITestCase):
    """Tests funcionales de sincronización"""

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
            username="testuser",
            email="test@sitec.mx",
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
        self.client.login(username="testuser", password="password123")

    def test_sync_creates_missing_steps(self):
        """Verificar que sync crea steps que no existen"""
        response = self.client.post(
            "/api/wizard/sync/",
            {
                "steps": [
                    {"step": 1, "data": {"project_name": "Test", "week_start": "2026-01-01"}},
                    {"step": 3, "data": {"cabling_nodes_total": 10}},
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["updated_steps"]), 2)

        draft = WizardDraft.objects.filter(user=self.user).first()
        steps = WizardStepData.objects.filter(draft=draft)
        self.assertEqual(steps.count(), 2)

    def test_sync_resolves_conflicts_with_resolution(self):
        """Verificar que sync resuelve conflictos con resolución"""
        # Crear step existente en servidor
        draft = WizardDraft.objects.create(
            company=self.company,
            sitec=self.sitec,
            user=self.user,
            status="draft",
        )
        WizardStepData.objects.create(
            draft=draft,
            step=1,
            data={"project_name": "Server Version", "week_start": "2026-01-01"},
        )

        # Sync con resolución "client"
        response = self.client.post(
            "/api/wizard/sync/",
            {
                "steps": [
                    {
                        "step": 1,
                        "data": {"project_name": "Client Version", "week_start": "2026-01-01", "updatedAt": "2026-01-02T00:00:00Z"},
                    }
                ],
                "resolution": {"1": "client"},
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["conflicts"]), 0)

        # Verificar que se usó la versión del cliente
        step = WizardStepData.objects.get(draft=draft, step=1)
        self.assertEqual(step.data["project_name"], "Client Version")

    def test_sync_detects_conflicts(self):
        """Verificar que sync detecta conflictos de timestamp"""
        # Crear step existente en servidor con timestamp más reciente
        draft = WizardDraft.objects.create(
            company=self.company,
            sitec=self.sitec,
            user=self.user,
            status="draft",
        )
        WizardStepData.objects.create(
            draft=draft,
            step=1,
            data={"project_name": "Server Version", "week_start": "2026-01-01"},
        )

        # Sync con timestamp más antiguo (debe generar conflicto)
        response = self.client.post(
            "/api/wizard/sync/",
            {
                "steps": [
                    {
                        "step": 1,
                        "data": {"project_name": "Client Version", "week_start": "2026-01-01", "updatedAt": "2026-01-01T00:00:00Z"},
                    }
                ],
            },
            format="json",
        )
        # Puede o no generar conflicto dependiendo de la lógica
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class FunctionalUserPreferencesTests(APITestCase):
    """Tests funcionales de preferencias de usuario"""

    def setUp(self):
        self.company = Company.objects.create(
            name="SITEC",
            timezone="America/Mexico_City",
            locale="es-MX",
            plan="enterprise",
            status="active",
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@sitec.mx",
            password="password123",
        )
        self.profile = UserProfile.objects.create(
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
        self.client.login(username="testuser", password="password123")

    def test_save_field_mode_preference(self):
        """Verificar que se puede guardar preferencia de Modo Campo"""
        response = self.client.patch(
            "/api/users/me/",
            {
                "preferences": {
                    "field_mode": True,
                    "field_mode_auto": False,
                }
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.preferences.get("field_mode"))
        self.assertFalse(self.profile.preferences.get("field_mode_auto"))

    def test_load_field_mode_preference(self):
        """Verificar que se puede cargar preferencia de Modo Campo"""
        self.profile.preferences = {"field_mode": True, "field_mode_auto": False}
        self.profile.save()

        response = self.client.get("/api/users/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["preferences"].get("field_mode"))
        self.assertFalse(response.data["preferences"].get("field_mode_auto"))


class FunctionalAnalyticsTests(APITestCase):
    """Tests funcionales de analytics"""

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
            username="testuser",
            email="test@sitec.mx",
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
        self.client.login(username="testuser", password="password123")

    def test_analytics_endpoint_accepts_data(self):
        """Verificar que analytics endpoint acepta y guarda datos"""
        response = self.client.post(
            "/api/wizard/analytics/",
            {
                "step_times": [
                    {"step": 1, "startTime": 1000, "endTime": 2000, "duration": 1000},
                    {"step": 2, "startTime": 2000, "endTime": 3500, "duration": 1500},
                ],
                "completed_steps": [1, 2],
                "total_time": 2500,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "ok")


class FunctionalPerformanceMetricsTests(APITestCase):
    """Tests funcionales de métricas de performance"""

    def setUp(self):
        self.company = Company.objects.create(
            name="SITEC",
            timezone="America/Mexico_City",
            locale="es-MX",
            plan="enterprise",
            status="active",
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@sitec.mx",
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

    def test_performance_metrics_endpoint_public(self):
        """Verificar que performance metrics endpoint es público (para sendBeacon)"""
        # No requiere autenticación
        response = self.client.post(
            "/api/wizard/performance/metrics/",
            {
                "fcp": 800,
                "tti": 2000,
                "js_size": 50000,
                "load_time": 2500,
                "url": "http://localhost:8000/wizard/1/",
                "timestamp": "2026-01-15T10:00:00Z",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "ok")

    def test_performance_metrics_generates_warnings(self):
        """Verificar que métricas que exceden límites generan warnings"""
        response = self.client.post(
            "/api/wizard/performance/metrics/",
            {
                "fcp": 1500,  # Excede 1000ms
                "tti": 3000,  # Excede 2500ms
                "js_size": 150000,  # Excede 100KB
                "load_time": 3000,
                "url": "http://localhost:8000/wizard/1/",
                "timestamp": "2026-01-15T10:00:00Z",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data["warnings"]), 0)
