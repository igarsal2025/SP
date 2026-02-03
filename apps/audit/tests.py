from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from apps.companies.models import Company

from .models import AuditLog
from .services import log_audit_event


User = get_user_model()


class AuditLogTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="SITEC",
            timezone="America/Mexico_City",
            locale="es-MX",
            plan="enterprise",
            status="active",
        )
        self.user = User.objects.create_user(
            username="auditor",
            email="auditor@sitec.mx",
            password="password123",
        )

    def test_log_audit_event_records_company_and_actor(self):
        factory = APIRequestFactory()
        request = factory.get("/api/companies/")
        request.user = self.user
        request.company = self.company

        log_audit_event(request, "custom_event", self.company)
        log = AuditLog.objects.first()

        self.assertIsNotNone(log)
        self.assertEqual(log.company, self.company)
        self.assertEqual(log.actor, self.user)
        self.assertEqual(log.action, "custom_event")
