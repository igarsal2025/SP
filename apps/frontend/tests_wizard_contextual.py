"""
Tests para validar que el wizard se adapta según el rol del usuario.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.models import UserProfile
from apps.companies.models import Company


User = get_user_model()


class WizardContextualTests(TestCase):
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

    def test_wizard_uses_readonly_template_for_cliente(self):
        """Cliente debe ver el template readonly del wizard."""
        self._login_with_role("cliente_wizard", "cliente")
        resp = self.client.get("/wizard/1/")
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "frontend/wizard/wizard_readonly.html")

    def test_wizard_uses_full_template_for_admin(self):
        """Admin debe ver el template completo del wizard."""
        self._login_with_role("admin_wizard", "admin_empresa")
        resp = self.client.get("/wizard/1/")
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "frontend/wizard.html")

    def test_wizard_uses_full_template_for_pm(self):
        """PM debe ver el template completo del wizard."""
        self._login_with_role("pm_wizard", "pm")
        resp = self.client.get("/wizard/1/")
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "frontend/wizard.html")

    def test_wizard_uses_full_template_for_tecnico(self):
        """Técnico debe ver el template completo del wizard."""
        self._login_with_role("tecnico_wizard", "tecnico")
        resp = self.client.get("/wizard/1/")
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "frontend/wizard.html")

    def test_wizard_uses_full_template_for_supervisor(self):
        """Supervisor debe ver el template completo del wizard."""
        self._login_with_role("supervisor_wizard", "supervisor")
        resp = self.client.get("/wizard/1/")
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "frontend/wizard.html")

    def test_wizard_step_uses_correct_template(self):
        """Los pasos del wizard deben usar el template correcto según rol."""
        # Cliente
        self._login_with_role("cliente_step", "cliente")
        resp = self.client.get("/wizard/5/")
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "frontend/wizard/wizard_readonly.html")
        
        # Admin
        self._login_with_role("admin_step", "admin_empresa")
        resp = self.client.get("/wizard/5/")
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "frontend/wizard.html")
