"""
Tests para validar que DashboardView selecciona el template correcto según rol.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.models import UserProfile
from apps.companies.models import Company


User = get_user_model()


class DashboardTemplateSelectionTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="Test Company",
            rfc="TEST123456ABC",
            tax_regime="601",
        )

    def _login_with_role(self, username: str, role: str):
        user = User.objects.create_user(username=username, password="test123")
        UserProfile.objects.create(user=user, company=self.company, role=role)
        self.client.force_login(user)
        return user

    def test_admin_uses_admin_template(self):
        self._login_with_role("admin_role", "admin_empresa")
        resp = self.client.get("/dashboard/")
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "frontend/dashboard/admin.html")

    def test_pm_uses_pm_template(self):
        self._login_with_role("pm_role", "pm")
        resp = self.client.get("/dashboard/")
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "frontend/dashboard/pm.html")

    def test_supervisor_uses_supervisor_template(self):
        self._login_with_role("supervisor_role", "supervisor")
        resp = self.client.get("/dashboard/")
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "frontend/dashboard/supervisor.html")

    def test_tecnico_uses_tecnico_template(self):
        self._login_with_role("tecnico_role", "tecnico")
        resp = self.client.get("/dashboard/")
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "frontend/dashboard/tecnico.html")

    def test_cliente_uses_cliente_template(self):
        self._login_with_role("cliente_role", "cliente")
        resp = self.client.get("/dashboard/")
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "frontend/dashboard/cliente.html")

