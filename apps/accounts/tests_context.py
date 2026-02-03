"""
Tests para el endpoint de contexto de usuario (/api/user/context/).
Valida que el endpoint devuelve correctamente la información del usuario,
permisos y configuración de UI según el rol.
"""
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.companies.models import Company
from apps.accounts.models import UserProfile

User = get_user_model()


class UserContextViewTests(APITestCase):
    """Tests para UserContextView."""

    def setUp(self):
        """Configuración inicial para los tests."""
        self.company = Company.objects.create(
            name="Test Company",
            rfc="TEST123456ABC",
            tax_regime="601",
        )

        # Crear usuarios de prueba con diferentes roles
        self.admin_user = User.objects.create_user(
            username="admin_test",
            password="test123",
            email="admin@test.com",
        )
        self.admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            company=self.company,
            role="admin_empresa",
        )

        self.pm_user = User.objects.create_user(
            username="pm_test",
            password="test123",
            email="pm@test.com",
        )
        self.pm_profile = UserProfile.objects.create(
            user=self.pm_user,
            company=self.company,
            role="pm",
        )

        self.tecnico_user = User.objects.create_user(
            username="tecnico_test",
            password="test123",
            email="tecnico@test.com",
        )
        self.tecnico_profile = UserProfile.objects.create(
            user=self.tecnico_user,
            company=self.company,
            role="tecnico",
        )

        self.cliente_user = User.objects.create_user(
            username="cliente_test",
            password="test123",
            email="cliente@test.com",
        )
        self.cliente_profile = UserProfile.objects.create(
            user=self.cliente_user,
            company=self.company,
            role="cliente",
        )

    def test_user_context_requires_authentication(self):
        """El endpoint requiere autenticación."""
        response = self.client.get("/api/user/context/")
        # Dependiendo del esquema de autenticación (SessionAuth/CSRF), DRF puede responder 401 o 403.
        self.assertIn(response.status_code, [401, 403])

    def test_user_context_returns_user_info(self):
        """El endpoint devuelve información del usuario."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/api/user/context/")
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["username"], "admin_test")
        self.assertEqual(response.data["user"]["email"], "admin@test.com")

    def test_user_context_returns_profile_info(self):
        """El endpoint devuelve información del perfil."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/api/user/context/")
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("profile", response.data)
        self.assertEqual(response.data["profile"]["role"], "admin_empresa")
        self.assertIsNotNone(response.data["profile"]["company"])

    def test_user_context_returns_permissions(self):
        """El endpoint devuelve permisos del usuario."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/api/user/context/")
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("permissions", response.data)
        self.assertIsInstance(response.data["permissions"], dict)
        # Admin debería tener todos los permisos
        self.assertTrue(response.data["permissions"].get("dashboard.view", False))
        self.assertTrue(response.data["permissions"].get("projects.create", False))

    def test_user_context_returns_ui_config(self):
        """El endpoint devuelve configuración de UI."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/api/user/context/")
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("ui_config", response.data)
        self.assertIn("navigation", response.data["ui_config"])
        self.assertIn("dashboard_sections", response.data["ui_config"])
        self.assertIn("wizard_mode", response.data["ui_config"])

    def test_admin_ui_config(self):
        """Admin tiene configuración completa de UI."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/api/user/context/")
        
        ui_config = response.data["ui_config"]
        self.assertIn("configuration", ui_config["navigation"])
        self.assertIn("users", ui_config["navigation"])
        self.assertIn("roi", ui_config["dashboard_sections"])
        self.assertEqual(ui_config["wizard_mode"], "full")
        self.assertTrue(ui_config["can_create_projects"])
        self.assertTrue(ui_config["can_approve_reports"])

    def test_pm_ui_config(self):
        """PM tiene configuración gerencial de UI."""
        self.client.force_authenticate(user=self.pm_user)
        response = self.client.get("/api/user/context/")
        
        ui_config = response.data["ui_config"]
        self.assertNotIn("configuration", ui_config["navigation"])
        self.assertNotIn("users", ui_config["navigation"])
        self.assertIn("roi", ui_config["dashboard_sections"])
        self.assertEqual(ui_config["wizard_mode"], "full")
        self.assertTrue(ui_config["can_create_projects"])
        self.assertTrue(ui_config["can_approve_reports"])
        self.assertFalse(ui_config["can_use_field_mode"])

    def test_tecnico_ui_config(self):
        """Técnico tiene configuración operativa de UI."""
        self.client.force_authenticate(user=self.tecnico_user)
        response = self.client.get("/api/user/context/")
        
        ui_config = response.data["ui_config"]
        self.assertIn("wizard", ui_config["navigation"])
        self.assertNotIn("roi", ui_config["dashboard_sections"])
        self.assertEqual(ui_config["wizard_mode"], "full")
        self.assertFalse(ui_config["can_create_projects"])
        self.assertFalse(ui_config["can_approve_reports"])
        self.assertTrue(ui_config["can_use_field_mode"])

    def test_cliente_ui_config(self):
        """Cliente tiene configuración de solo lectura."""
        self.client.force_authenticate(user=self.cliente_user)
        response = self.client.get("/api/user/context/")
        
        ui_config = response.data["ui_config"]
        self.assertNotIn("wizard", ui_config["navigation"])
        self.assertNotIn("roi", ui_config["dashboard_sections"])
        self.assertEqual(ui_config["wizard_mode"], "readonly")
        self.assertFalse(ui_config["can_create_projects"])
        self.assertFalse(ui_config["can_approve_reports"])
        self.assertFalse(ui_config["can_use_field_mode"])
        self.assertFalse(ui_config["can_use_ai_chat"])
        self.assertFalse(ui_config["can_generate_pdf"])

    def test_user_context_without_profile(self):
        """El endpoint maneja usuarios sin perfil."""
        user_no_profile = User.objects.create_user(
            username="noprofile",
            password="test123",
        )
        self.client.force_authenticate(user=user_no_profile)
        response = self.client.get("/api/user/context/")
        
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.data)

    def test_permissions_reflect_abac_policies(self):
        """Los permisos reflejan las políticas ABAC."""
        self.client.force_authenticate(user=self.pm_user)
        response = self.client.get("/api/user/context/")
        
        permissions = response.data["permissions"]
        # PM debería poder ver dashboard y crear proyectos
        # (depende de las políticas configuradas)
        self.assertIn("dashboard.view", permissions)
        self.assertIn("projects.create", permissions)
