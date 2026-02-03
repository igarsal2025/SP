from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import AccessPolicy, UserProfile
from apps.companies.models import Company, Sitec
from apps.sync.models import SyncItem, SyncSession

User = get_user_model()


class SyncTests(APITestCase):
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

    def test_sync_creates_session(self):
        """Verificar que sync crea una sesión"""
        response = self.client.post(
            "/api/sync/",
            {
                "items": [
                    {
                        "entity_type": "wizard_step",
                        "entity_id": "1",
                        "data": {"project_name": "Test"},
                    }
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("session", response.data)
        self.assertEqual(response.data["session"]["status"], "completed")
        self.assertEqual(response.data["session"]["items_synced"], 1)
        self.assertEqual(response.data["session"]["conflicts_detected"], 0)

    def test_sync_multiple_items(self):
        """Verificar sincronización de múltiples items"""
        response = self.client.post(
            "/api/sync/",
            {
                "items": [
                    {"entity_type": "wizard_step", "entity_id": "1", "data": {"step": 1}},
                    {"entity_type": "wizard_step", "entity_id": "2", "data": {"step": 2}},
                    {"entity_type": "wizard_step", "entity_id": "3", "data": {"step": 3}},
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["synced_items"]), 3)
        self.assertEqual(response.data["session"]["items_synced"], 3)

    def test_sync_detects_conflicts(self):
        """Verificar detección de conflictos por timestamp"""
        # Crear item existente con timestamp más reciente
        session1 = SyncSession.objects.create(
            company=self.company,
            sitec=self.sitec,
            user=self.user,
            status="completed",
        )
        existing_item = SyncItem.objects.create(
            session=session1,
            entity_type="wizard_step",
            entity_id="1",
            status="synced",
            data={"project_name": "Server Version"},
            server_timestamp=timezone.now(),
        )

        # Intentar sync con timestamp más antiguo
        old_timestamp = (timezone.now() - timedelta(hours=1)).isoformat()
        response = self.client.post(
            "/api/sync/",
            {
                "items": [
                    {
                        "entity_type": "wizard_step",
                        "entity_id": "1",
                        "data": {"project_name": "Client Version"},
                        "updatedAt": old_timestamp,
                    }
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data["conflicts"]), 0)
        self.assertEqual(response.data["session"]["status"], "conflict")
        self.assertEqual(response.data["session"]["conflicts_detected"], 1)

    def test_sync_resolves_conflict_with_client_choice(self):
        """Verificar resolución de conflicto eligiendo versión cliente"""
        # Crear item existente
        session1 = SyncSession.objects.create(
            company=self.company,
            sitec=self.sitec,
            user=self.user,
            status="completed",
        )
        SyncItem.objects.create(
            session=session1,
            entity_type="wizard_step",
            entity_id="1",
            status="synced",
            data={"project_name": "Server Version"},
            server_timestamp=timezone.now(),
        )

        # Resolver conflicto eligiendo cliente
        response = self.client.post(
            "/api/sync/",
            {
                "items": [
                    {
                        "entity_type": "wizard_step",
                        "entity_id": "1",
                        "data": {"project_name": "Client Version"},
                    }
                ],
                "resolution": {"1": "client"},
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["conflicts"]), 0)
        self.assertEqual(response.data["session"]["status"], "completed")

    def test_sync_resolves_conflict_with_server_choice(self):
        """Verificar resolución de conflicto eligiendo versión servidor"""
        # Crear item existente
        session1 = SyncSession.objects.create(
            company=self.company,
            sitec=self.sitec,
            user=self.user,
            status="completed",
        )
        existing_item = SyncItem.objects.create(
            session=session1,
            entity_type="wizard_step",
            entity_id="1",
            status="synced",
            data={"project_name": "Server Version"},
            server_timestamp=timezone.now(),
        )

        # Resolver conflicto eligiendo servidor
        response = self.client.post(
            "/api/sync/",
            {
                "items": [
                    {
                        "entity_type": "wizard_step",
                        "entity_id": "1",
                        "data": {"project_name": "Client Version"},
                    }
                ],
                "resolution": {"1": "server"},
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["conflicts"]), 0)
        # Verificar que se usó la versión del servidor
        synced_item = SyncItem.objects.get(
            session__id=response.data["session"]["id"],
            entity_id="1",
        )
        self.assertEqual(synced_item.data["project_name"], "Server Version")

    def test_sync_continues_existing_session(self):
        """Verificar continuación de sesión existente"""
        # Crear sesión inicial
        session = SyncSession.objects.create(
            company=self.company,
            sitec=self.sitec,
            user=self.user,
            status="syncing",
        )
        session_id = str(session.id)

        # Continuar sync en la misma sesión
        response = self.client.post(
            "/api/sync/",
            {
                "session_id": session_id,
                "items": [
                    {"entity_type": "wizard_step", "entity_id": "2", "data": {"step": 2}},
                ],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["session"]["id"], session_id)
        self.assertEqual(response.data["session"]["items_synced"], 1)

    def test_sync_session_not_found(self):
        """Verificar error cuando sesión no existe"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = self.client.post(
            "/api/sync/",
            {
                "session_id": fake_id,
                "items": [{"entity_type": "wizard_step", "entity_id": "1", "data": {}}],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_sync_different_entity_types(self):
        """Verificar sync de diferentes tipos de entidades"""
        response = self.client.post(
            "/api/sync/",
            {
                "items": [
                    {"entity_type": "wizard_step", "entity_id": "1", "data": {"step": 1}},
                    {"entity_type": "report", "entity_id": "r1", "data": {"title": "Report"}},
                    {"entity_type": "project", "entity_id": "p1", "data": {"name": "Project"}},
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["synced_items"]), 3)

    def test_get_sync_session(self):
        """Verificar consulta de sesión de sync"""
        session = SyncSession.objects.create(
            company=self.company,
            sitec=self.sitec,
            user=self.user,
            status="completed",
        )
        SyncItem.objects.create(
            session=session,
            entity_type="wizard_step",
            entity_id="1",
            status="synced",
            data={"step": 1},
        )

        response = self.client.get(f"/api/sync/sessions/{session.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(session.id))
        self.assertEqual(len(response.data["items"]), 1)

    def test_list_sync_sessions(self):
        """Verificar listado de sesiones de sync"""
        # Crear múltiples sesiones
        for i in range(3):
            SyncSession.objects.create(
                company=self.company,
                sitec=self.sitec,
                user=self.user,
                status="completed",
            )

        response = self.client.get("/api/sync/sessions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 3)

    def test_sync_updates_existing_item(self):
        """Verificar actualización de item existente en misma sesión"""
        session = SyncSession.objects.create(
            company=self.company,
            sitec=self.sitec,
            user=self.user,
            status="syncing",
        )
        SyncItem.objects.create(
            session=session,
            entity_type="wizard_step",
            entity_id="1",
            status="pending",
            data={"step": 1, "old": True},
        )        # Sincronizar con datos actualizados
        response = self.client.post(
            "/api/sync/",
            {
                "session_id": str(session.id),
                "items": [
                    {"entity_type": "wizard_step", "entity_id": "1", "data": {"step": 1, "new": True}},
                ],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item = SyncItem.objects.get(session=session, entity_id="1")
        self.assertIn("new", item.data)
        self.assertEqual(item.status, "synced")
