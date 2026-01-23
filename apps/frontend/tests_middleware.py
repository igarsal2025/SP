"""
Tests para el middleware de contexto de usuario.
Valida que el middleware agrega correctamente el contexto a las requests.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase

from apps.companies.models import Company
from apps.accounts.models import UserProfile
from apps.frontend.middleware import UserContextMiddleware

User = get_user_model()


class UserContextMiddlewareTests(TestCase):
    """Tests para UserContextMiddleware."""

    def setUp(self):
        """Configuración inicial para los tests."""
        self.factory = RequestFactory()
        self.company = Company.objects.create(
            name="Test Company",
            rfc="TEST123456ABC",
            tax_regime="601",
        )

        self.user = User.objects.create_user(
            username="testuser",
            password="test123",
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            company=self.company,
            role="pm",
        )

    def get_response(self, request):
        """Función de respuesta dummy para el middleware."""
        return request

    def test_middleware_adds_context_for_authenticated_user(self):
        """El middleware agrega contexto para usuarios autenticados."""
        middleware = UserContextMiddleware(self.get_response)
        request = self.factory.get("/")
        request.user = self.user

        response = middleware(request)

        self.assertIsNotNone(request.user_context)
        self.assertEqual(request.user_context["profile"]["role"], "pm")
        self.assertIn("permissions", request.user_context)
        self.assertIn("ui_config", request.user_context)

    def test_middleware_no_context_for_unauthenticated_user(self):
        """El middleware no agrega contexto para usuarios no autenticados."""
        middleware = UserContextMiddleware(self.get_response)
        request = self.factory.get("/")
        request.user = AnonymousUser()

        response = middleware(request)

        self.assertIsNone(request.user_context)

    def test_middleware_no_context_for_user_without_profile(self):
        """El middleware maneja usuarios sin perfil."""
        middleware = UserContextMiddleware(self.get_response)
        user_no_profile = User.objects.create_user(
            username="noprofile",
            password="test123",
        )
        request = self.factory.get("/")
        request.user = user_no_profile

        response = middleware(request)

        self.assertIsNone(request.user_context)

    def test_middleware_context_includes_ui_config(self):
        """El contexto incluye configuración de UI."""
        middleware = UserContextMiddleware(self.get_response)
        request = self.factory.get("/")
        request.user = self.user

        response = middleware(request)

        ui_config = request.user_context["ui_config"]
        self.assertIn("navigation", ui_config)
        self.assertIn("dashboard_sections", ui_config)
        self.assertIn("wizard_mode", ui_config)

    def test_middleware_context_includes_permissions(self):
        """El contexto incluye permisos del usuario."""
        middleware = UserContextMiddleware(self.get_response)
        request = self.factory.get("/")
        request.user = self.user

        response = middleware(request)

        permissions = request.user_context["permissions"]
        self.assertIsInstance(permissions, dict)
        self.assertIn("dashboard.view", permissions)
