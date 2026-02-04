"""
Tests de throttling y costos de IA
"""
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from rest_framework.test import APITestCase
from unittest.mock import patch

from apps.companies.models import Company, Sitec
from apps.accounts.models import UserProfile

from .models import AiSuggestion
from .services import check_ai_throttle, record_ai_usage, get_ai_usage_stats, estimate_ai_cost

User = get_user_model()


class AiThrottlingTests(APITestCase):
    """Tests de throttling de IA"""

    def setUp(self):
        self.company = Company.objects.create(
            name="Test Company",
            timezone="America/Mexico_City",
            locale="es-MX",
            plan="enterprise",
            status="active",
        )
        self.sitec = Sitec.objects.create(
            company=self.company,
            schema_name="test",
            status="active",
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            company=self.company,
            role="tecnico",
        )
        self.client.login(username="testuser", password="password123")
        self.client.defaults["HTTP_X_SITEC_ID"] = str(self.sitec.id)
        cache.clear()

    @patch("apps.ai.services.settings")
    def test_throttle_disabled_allows_all(self, mock_settings):
        """Test que cuando throttling está deshabilitado, permite todas las requests"""
        mock_settings.AI_THROTTLE_ENABLED = False
        
        allowed, reason, retry_after = check_ai_throttle(self.company, self.user, "quick")
        self.assertTrue(allowed)
        self.assertEqual(reason, "throttle_disabled")

    @patch("apps.ai.services.settings")
    def test_throttle_quick_per_hour(self, mock_settings):
        """Test límite por hora para modo quick"""
        mock_settings.AI_THROTTLE_ENABLED = True
        mock_settings.AI_THROTTLE_QUICK_PER_HOUR = 5
        mock_settings.AI_THROTTLE_QUICK_PER_DAY = 100
        
        # Hacer 5 requests (límite)
        for i in range(5):
            allowed, reason, retry_after = check_ai_throttle(self.company, self.user, "quick")
            self.assertTrue(allowed, f"Request {i+1} debería estar permitida")
            record_ai_usage(self.company, self.user, "quick", 0.0)
        
        # La 6ta request debería ser bloqueada
        allowed, reason, retry_after = check_ai_throttle(self.company, self.user, "quick")
        self.assertFalse(allowed)
        self.assertEqual(reason, "hourly_limit_exceeded")
        self.assertGreater(retry_after, 0)

    @patch("apps.ai.services.settings")
    def test_throttle_heavy_per_day(self, mock_settings):
        """Test límite por día para modo heavy"""
        mock_settings.AI_THROTTLE_ENABLED = True
        mock_settings.AI_THROTTLE_HEAVY_PER_HOUR = 100
        mock_settings.AI_THROTTLE_HEAVY_PER_DAY = 3
        
        # Crear 3 requests en la base de datos (simulando día anterior)
        for i in range(3):
            AiSuggestion.objects.create(
                company=self.company,
                sitec=self.sitec,
                user=self.user,
                mode="heavy",
                status="success",
            )
        
        # La siguiente request debería ser bloqueada
        allowed, reason, retry_after = check_ai_throttle(self.company, self.user, "heavy")
        self.assertFalse(allowed)
        self.assertEqual(reason, "daily_limit_exceeded")

    def test_estimate_cost_rule_engine(self):
        """Test estimación de costos para rule engine"""
        cost = estimate_ai_cost("quick", "rule_engine", 10)
        self.assertEqual(cost, 0.0001)

    def test_estimate_cost_light_model(self):
        """Test estimación de costos para light model"""
        cost = estimate_ai_cost("quick", "light_model", 10)
        self.assertEqual(cost, 0.001)

    def test_estimate_cost_heavy(self):
        """Test estimación de costos para heavy model"""
        cost = estimate_ai_cost("heavy", "heavy_model", 100)
        self.assertEqual(cost, 0.01)

    @patch("apps.ai.services.settings")
    def test_record_usage_updates_cache(self, mock_settings):
        """Test que record_ai_usage actualiza el cache"""
        mock_settings.AI_THROTTLE_ENABLED = True
        
        cache_key = f"ai_throttle:{self.company.id}:{self.user.id}:quick:hour"
        initial_count = cache.get(cache_key, 0)
        
        record_ai_usage(self.company, self.user, "quick", 0.0)
        
        new_count = cache.get(cache_key, 0)
        self.assertEqual(new_count, initial_count + 1)

    def test_get_usage_stats(self):
        """Test obtención de estadísticas de uso"""
        # Crear algunas sugerencias
        for i in range(5):
            AiSuggestion.objects.create(
                company=self.company,
                sitec=self.sitec,
                user=self.user,
                mode="quick" if i < 3 else "heavy",
                status="success",
                latency_ms=50,
            )
        
        stats = get_ai_usage_stats(self.company, self.user, days=30)
        
        self.assertEqual(stats["total_requests"], 5)
        self.assertEqual(stats["quick_requests"], 3)
        self.assertEqual(stats["heavy_requests"], 2)
        self.assertEqual(stats["success_count"], 5)
        self.assertIn("by_day", stats)


class AiThrottlingIntegrationTests(APITestCase):
    """Tests de integración de throttling en endpoint"""

    def setUp(self):
        self.company = Company.objects.create(
            name="Test Company",
            timezone="America/Mexico_City",
            locale="es-MX",
            plan="enterprise",
            status="active",
        )
        self.sitec = Sitec.objects.create(
            company=self.company,
            schema_name="test",
            status="active",
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
        )
        UserProfile.objects.create(
            user=self.user,
            company=self.company,
            role="tecnico",
        )
        self.client.login(username="testuser", password="password123")
        self.client.defaults["HTTP_X_SITEC_ID"] = str(self.sitec.id)
        cache.clear()

    @patch("apps.ai.services.settings")
    @patch("apps.ai.views.check_ai_throttle")
    def test_endpoint_returns_429_when_throttled(self, mock_check, mock_settings):
        """Test que el endpoint retorna 429 cuando está throttled"""
        mock_settings.AI_THROTTLE_ENABLED = True
        mock_check.return_value = (False, "hourly_limit_exceeded", 3600)
        
        response = self.client.post(
            "/api/ai/suggest/",
            {"step": 1, "data": {}, "mode": "quick"},
            format="json",
        )
        
        self.assertEqual(response.status_code, 429)
        self.assertIn("error", response.data)
        self.assertIn("retry_after", response.data)

    @patch("apps.ai.services.settings")
    def test_endpoint_allows_when_not_throttled(self, mock_settings):
        """Test que el endpoint permite requests cuando no está throttled"""
        mock_settings.AI_THROTTLE_ENABLED = False
        
        response = self.client.post(
            "/api/ai/suggest/",
            {"step": 1, "data": {}, "mode": "quick"},
            format="json",
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("suggestions", response.data)
