from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework.test import APITestCase

from apps.accounts.models import AccessPolicy, UserProfile
from apps.audit.models import AuditLog

from .models import Company, Sitec


User = get_user_model()


class CompanyModuleTests(APITestCase):
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
            username="tester",
            email="tester@sitec.mx",
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
        self.client.login(username="tester", password="password123")

    def test_seed_command_is_idempotent(self):
        call_command("seed_sitec")
        call_command("seed_sitec")
        self.assertGreaterEqual(Company.objects.filter(name="SITEC").count(), 1)
        self.assertGreaterEqual(Sitec.objects.filter(schema_name="sitec").count(), 1)
        self.assertGreaterEqual(AccessPolicy.objects.filter(action="*").count(), 1)

    def test_sitec_status_patch_invalid(self):
        response = self.client.patch(
            f"/api/sitec/{self.sitec.id}/status/",
            {"status": "invalid"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_company_create_writes_audit_log(self):
        response = self.client.post(
            "/api/companies/",
            {"name": "SITEC-TEST"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            AuditLog.objects.filter(action="company_created").exists()
        )
