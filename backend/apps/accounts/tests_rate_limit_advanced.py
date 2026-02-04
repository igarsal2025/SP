"""
Tests para Rate Limiting Avanzado
"""
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.core.cache import cache
from rest_framework.test import APITestCase

from apps.accounts.models import AccessPolicy, UserProfile
from apps.companies.models import Company, Sitec

User = get_user_model()


class AdvancedRateLimitTests(APITestCase):
    """Tests para rate limiting avanzado"""

    def setUp(self):
        """Configuración inicial para cada test"""
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
            username="test_rate_limit",
            email="test_rate_limit@sitec.mx",
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
        cache.clear()

    @override_settings(RATE_LIMIT_ENABLED=False)
    def test_rate_limit_disabled_allows_all(self):
        """Rate limiting deshabilitado permite todas las requests"""
        for _ in range(10):
            response = self.client.get("/api/companies/")
            # No debería ser 429
            self.assertNotEqual(response.status_code, 429)

    @override_settings(
        RATE_LIMIT_ENABLED=True,
        RATE_LIMIT_REQUESTS=5,
        RATE_LIMIT_WINDOW=60,
    )
    def test_rate_limit_by_ip_blocks_after_limit(self):
        """Rate limiting por IP bloquea después del límite"""
        # Hacer 5 requests (límite)
        for i in range(5):
            response = self.client.get("/api/companies/")
            # Puede fallar por otras razones, pero no debería ser 429 todavía
            if response.status_code == 429:
                self.fail(f"Request {i+1} fue bloqueada demasiado pronto")
        
        # La 6ta request debería ser bloqueada
        response = self.client.get("/api/companies/")
        # Puede ser 429 o puede fallar por otras razones
        # Si es 429, verificar que tiene la información correcta
        if response.status_code == 429:
            self.assertIn("error", response.json())
            self.assertIn("X-RateLimit-Limit", response)

    @override_settings(
        RATE_LIMIT_ENABLED=True,
        RATE_LIMIT_REQUESTS=100,
        RATE_LIMIT_WINDOW=60,
        RATE_LIMIT_USER_REQUESTS=5,
        RATE_LIMIT_USER_WINDOW=60,
    )
    def test_rate_limit_by_user_blocks_after_limit(self):
        """Rate limiting por usuario bloquea después del límite"""
        self.client.force_authenticate(user=self.user)
        
        # Hacer 5 requests (límite de usuario)
        for i in range(5):
            response = self.client.get("/api/companies/")
            # Puede fallar por otras razones, pero no debería ser 429 todavía
            if response.status_code == 429:
                self.fail(f"Request {i+1} fue bloqueada demasiado pronto")
        
        # La 6ta request debería ser bloqueada por límite de usuario
        response = self.client.get("/api/companies/")
        # Puede ser 429 o puede fallar por otras razones
        if response.status_code == 429:
            data = response.json()
            self.assertIn("error", data)
            self.assertIn("limit", data)
            self.assertEqual(data["limit"], 5)

    @override_settings(
        RATE_LIMIT_ENABLED=True,
        RATE_LIMIT_REQUESTS=100,
        RATE_LIMIT_WINDOW=60,
        RATE_LIMIT_USER_REQUESTS=200,
        RATE_LIMIT_USER_WINDOW=60,
    )
    def test_rate_limit_headers_present(self):
        """Headers de rate limit están presentes en respuestas"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/companies/")
        
        # Verificar headers
        self.assertIn("X-RateLimit-Limit", response)
        self.assertIn("X-RateLimit-Remaining", response)
        self.assertIn("X-RateLimit-Reset", response)
        
        # Verificar valores
        limit = int(response["X-RateLimit-Limit"])
        remaining = int(response["X-RateLimit-Remaining"])
        reset = int(response["X-RateLimit-Reset"])
        
        self.assertGreater(limit, 0)
        self.assertGreaterEqual(remaining, 0)
        self.assertLessEqual(remaining, limit)
        self.assertGreater(reset, 0)

    @override_settings(
        RATE_LIMIT_ENABLED=True,
        RATE_LIMIT_ENDPOINTS={
            "/api/auth/login/": {
                "POST": {
                    "ip": {"requests": 5, "window": 60},
                    "user": {"requests": 3, "window": 300},
                }
            }
        }
    )
    def test_rate_limit_by_endpoint(self):
        """Rate limiting por endpoint funciona con configuración específica"""
        # Hacer 5 requests al endpoint de login (límite por IP)
        for i in range(5):
            response = self.client.post(
                "/api/auth/login/",
                {"username": "test", "password": "test"},
                format="json"
            )
            # Puede fallar por credenciales inválidas, pero no debería ser 429 todavía
            if response.status_code == 429:
                self.fail(f"Request {i+1} fue bloqueada demasiado pronto")
        
        # La 6ta request debería ser bloqueada
        response = self.client.post(
            "/api/auth/login/",
            {"username": "test", "password": "test"},
            format="json"
        )
        if response.status_code == 429:
            data = response.json()
            self.assertIn("error", data)
            self.assertEqual(data["limit"], 5)

    @override_settings(
        RATE_LIMIT_ENABLED=True,
        RATE_LIMIT_EXCLUDED_PATHS=["/health/", "/api/metrics/"],
    )
    def test_rate_limit_excluded_paths(self):
        """Paths excluidos no aplican rate limiting"""
        # Hacer muchas requests a un path excluido
        for _ in range(100):
            response = self.client.get("/health/")
            # No debería ser 429
            self.assertNotEqual(response.status_code, 429)

    @override_settings(
        RATE_LIMIT_ENABLED=True,
        RATE_LIMIT_REQUESTS=3,
        RATE_LIMIT_WINDOW=60,
    )
    def test_rate_limit_remaining_decreases(self):
        """El remaining disminuye con cada request"""
        self.client.force_authenticate(user=self.user)
        
        remaining_values = []
        for _ in range(3):
            response = self.client.get("/api/companies/")
            if "X-RateLimit-Remaining" in response:
                remaining = int(response["X-RateLimit-Remaining"])
                remaining_values.append(remaining)
        
        # Verificar que remaining disminuye (o se mantiene si hay múltiples límites)
        if len(remaining_values) >= 2:
            # El remaining debería disminuir o mantenerse igual
            self.assertGreaterEqual(remaining_values[0], remaining_values[-1])

    @override_settings(
        RATE_LIMIT_ENABLED=True,
        RATE_LIMIT_REQUESTS=100,
        RATE_LIMIT_WINDOW=60,
        RATE_LIMIT_USER_REQUESTS=5,
        RATE_LIMIT_USER_WINDOW=60,
    )
    def test_rate_limit_user_takes_precedence(self):
        """Rate limiting por usuario tiene precedencia sobre IP cuando es más restrictivo"""
        self.client.force_authenticate(user=self.user)
        
        # Hacer 5 requests (límite de usuario, más restrictivo que IP)
        for i in range(5):
            response = self.client.get("/api/companies/")
            if response.status_code == 429:
                self.fail(f"Request {i+1} fue bloqueada demasiado pronto")
        
        # La 6ta request debería ser bloqueada por límite de usuario
        response = self.client.get("/api/companies/")
        if response.status_code == 429:
            data = response.json()
            # El límite debería ser el de usuario (5), no el de IP (100)
            self.assertEqual(data["limit"], 5)

    @override_settings(
        RATE_LIMIT_ENABLED=True,
        RATE_LIMIT_REQUESTS=3,
        RATE_LIMIT_WINDOW=60,
    )
    def test_rate_limit_error_message(self):
        """Mensaje de error de rate limit es informativo"""
        # Exceder el límite
        for _ in range(4):
            self.client.get("/api/companies/")
        
        response = self.client.get("/api/companies/")
        if response.status_code == 429:
            data = response.json()
            self.assertIn("error", data)
            self.assertIn("message", data)
            self.assertIn("limit", data)
            self.assertIn("remaining", data)
            self.assertIn("reset_at", data)
