from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.companies.models import Company, Sitec

from .models import AccessPolicy, UserProfile


User = get_user_model()


class AccessPolicyPermissionTests(APITestCase):
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
            username="pm_user",
            email="pm@sitec.mx",
            password="password123",
        )
        self.profile = UserProfile.objects.create(
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
        self.client.login(username="pm_user", password="password123")

    def test_policy_deny_overrides_allow(self):
        AccessPolicy.objects.create(
            company=self.company,
            action="list",
            conditions={"role": "pm"},
            effect="deny",
            priority=10,
            is_active=True,
        )
        response = self.client.get("/api/companies/")
        self.assertEqual(response.status_code, 403)

    def test_policy_allows_when_no_specific_rule(self):
        response = self.client.get("/api/companies/")
        self.assertEqual(response.status_code, 200)

    def test_me_endpoint_updates_preferences(self):
        response = self.client.patch(
            "/api/users/me/",
            {"preferences": {"theme": "dark"}},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.preferences.get("theme"), "dark")


class CompanySitecMiddlewareTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="SITEC",
            timezone="America/Mexico_City",
            locale="es-MX",
            plan="enterprise",
            status="active",
        )
        self.user = User.objects.create_user(
            username="user",
            email="user@sitec.mx",
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
        self.client.login(username="user", password="password123")

    def test_requires_sitec_for_api_routes(self):
        response = self.client.get("/api/companies/")
        self.assertEqual(response.status_code, 400)
