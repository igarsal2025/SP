from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.accounts.models import AccessPolicy, UserProfile
from apps.companies.models import Company, Sitec
from apps.rules.models import RuleItem, RuleSet

User = get_user_model()


class RulesModuleTests(APITestCase):
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
            username="rules-user",
            email="rules@sitec.mx",
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
        self.client.login(username="rules-user", password="password123")

        self.ruleset = RuleSet.objects.create(
            company=self.company,
            sitec=self.sitec,
            name="Reglas Wizard v1",
            version=1,
            scope="wizard",
            is_active=True,
        )
        RuleItem.objects.create(
            ruleset=self.ruleset,
            code="progress_pct_negative",
            field="progress_pct",
            severity="critical",
            message="Porcentaje de avance no puede ser negativo.",
            step=2,
            condition={"field": "progress_pct", "op": "lt", "value": 0},
        )

    def test_rule_evaluate_endpoint(self):
        response = self.client.post(
            "/api/rules/evaluate/",
            {"step": 2, "data": {"progress_pct": -1}},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["rules_version"], 1)
        self.assertEqual(len(response.data["results"]), 1)

    def test_wizard_validate_includes_rules(self):
        response = self.client.post(
            "/api/wizard/validate/",
            {"step": 2, "data": {"progress_pct": -1}},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("progress_pct_negative", response.data["critical"])

    def test_rules_cache_returns_ruleset(self):
        from apps.rules.services import get_active_ruleset

        ruleset = get_active_ruleset(self.company, self.sitec, "wizard")
        self.assertIsNotNone(ruleset)
