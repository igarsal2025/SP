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


class AccessPolicyEvaluateViewTests(APITestCase):
    """Tests para el endpoint de evaluación de políticas ABAC"""

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
            username="tecnico_user",
            email="tecnico@sitec.mx",
            password="password123",
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            company=self.company,
            role="tecnico",
        )
        # Política base: permitir todo
        AccessPolicy.objects.create(
            company=self.company,
            action="*",
            effect="allow",
            priority=0,
            is_active=True,
        )
        self.client.login(username="tecnico_user", password="password123")
        # Agregar header de sitec para las requests
        self.client.defaults["HTTP_X_SITEC_ID"] = str(self.sitec.id)

    def test_evaluate_action_allowed(self):
        """Test que evalúa una acción permitida"""
        response = self.client.post(
            "/api/policies/evaluate/",
            {"action": "wizard.save"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["allowed"])
        self.assertEqual(data["action"], "wizard.save")

    def test_evaluate_action_denied(self):
        """Test que evalúa una acción denegada"""
        # Crear política que deniega wizard.save para técnicos
        AccessPolicy.objects.create(
            company=self.company,
            action="wizard.save",
            conditions={"role": "tecnico"},
            effect="deny",
            priority=10,
            is_active=True,
        )
        response = self.client.post(
            "/api/policies/evaluate/",
            {"action": "wizard.save"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["allowed"])
        self.assertEqual(data["policy_effect"], "deny")

    def test_evaluate_action_with_conditions(self):
        """Test que evalúa una acción con condiciones"""
        # Política que permite solo a PMs
        AccessPolicy.objects.create(
            company=self.company,
            action="dashboard.view",
            conditions={"role": "pm"},
            effect="allow",
            priority=10,
            is_active=True,
        )
        # Como técnico, debe ser denegado
        response = self.client.post(
            "/api/policies/evaluate/",
            {"action": "dashboard.view"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["allowed"])

    def test_evaluate_action_without_action_param(self):
        """Test que evalúa usando la acción del request"""
        response = self.client.post(
            "/api/policies/evaluate/",
            {},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("action", data)
        self.assertIn("allowed", data)

    def test_evaluate_multiple_actions(self):
        """Test que evalúa múltiples acciones"""
        # Crear políticas específicas
        AccessPolicy.objects.create(
            company=self.company,
            action="wizard.save",
            effect="allow",
            priority=10,
            is_active=True,
        )
        AccessPolicy.objects.create(
            company=self.company,
            action="wizard.submit",
            conditions={"role": "pm"},
            effect="allow",
            priority=10,
            is_active=True,
        )
        
        # wizard.save debe estar permitido
        response1 = self.client.post(
            "/api/policies/evaluate/",
            {"action": "wizard.save"},
            format="json",
        )
        self.assertEqual(response1.status_code, 200)
        self.assertTrue(response1.json()["allowed"])
        
        # wizard.submit debe estar denegado (solo PM)
        response2 = self.client.post(
            "/api/policies/evaluate/",
            {"action": "wizard.submit"},
            format="json",
        )
        self.assertEqual(response2.status_code, 200)
        self.assertFalse(response2.json()["allowed"])

    def test_evaluate_wildcard_action(self):
        """Test que evalúa acciones con wildcard"""
        AccessPolicy.objects.create(
            company=self.company,
            action="wizard.*",
            effect="allow",
            priority=10,
            is_active=True,
        )
        
        response = self.client.post(
            "/api/policies/evaluate/",
            {"action": "wizard.save"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["allowed"])

    def test_evaluate_unauthenticated(self):
        """Test que requiere autenticación"""
        self.client.logout()
        response = self.client.post(
            "/api/policies/evaluate/",
            {"action": "wizard.save"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    def test_admin_empresa_always_allowed(self):
        """Test que admin_empresa siempre tiene acceso"""
        admin_user = User.objects.create_user(
            username="admin_user",
            email="admin@sitec.mx",
            password="password123",
        )
        UserProfile.objects.create(
            user=admin_user,
            company=self.company,
            role="admin_empresa",
        )
        self.client.login(username="admin_user", password="password123")
        
        # Crear política que deniega todo
        AccessPolicy.objects.create(
            company=self.company,
            action="*",
            effect="deny",
            priority=100,
            is_active=True,
        )
        
        response = self.client.post(
            "/api/policies/evaluate/",
            {"action": "wizard.save"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Admin siempre tiene acceso
        self.assertTrue(data["allowed"])