"""
Smoke tests: verifica que las rutas de secciones renderizan y no dan 404.
No valida permisos ABAC (eso se hace en APIs), solo que el frontend sirve páginas.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.models import UserProfile
from apps.companies.models import Company


User = get_user_model()


class SectionsSmokeTests(TestCase):
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

    def test_projects_page_renders(self):
        self._login_with_role("pm_projects", "pm")
        resp = self.client.get("/projects/")
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "frontend/projects/list.html")

    def test_reports_page_renders(self):
        self._login_with_role("pm_reports", "pm")
        resp = self.client.get("/reports/")
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "frontend/reports/list.html")

    def test_documents_page_renders(self):
        self._login_with_role("cliente_docs", "cliente")
        resp = self.client.get("/documents/")
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "frontend/documents/list.html")

    def test_approvals_page_renders(self):
        self._login_with_role("supervisor_appr", "supervisor")
        resp = self.client.get("/reports/approvals/")
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "frontend/reports/approvals.html")

