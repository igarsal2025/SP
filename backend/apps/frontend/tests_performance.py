"""
Tests de Performance para el módulo Frontend
Cubre: tiempo de respuesta, tamaño de bundles, queries N+1
"""
import os
import time
from pathlib import Path

from django.contrib.auth import get_user_model
from django.db import connection, reset_queries
from django.test import TestCase, override_settings
from rest_framework.test import APITestCase

from apps.accounts.models import AccessPolicy, UserProfile
from apps.audit.models import AuditLog
from apps.companies.models import Company, Sitec

User = get_user_model()

# Límites de performance
PERFORMANCE_LIMITS = {
    "endpoint_response_time_ms": 500,  # 500ms por endpoint
    "js_bundle_size_kb": 100,  # 100KB
    "max_queries_per_request": 10,  # Máximo 10 queries por request
}


class PerformanceEndpointTests(APITestCase):
    """Tests de tiempo de respuesta de endpoints"""

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
            username="testuser",
            email="test@sitec.mx",
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
        self.client.login(username="testuser", password="password123")

    def test_save_step_response_time(self):
        """Verificar que save_step responde en < 500ms"""
        start = time.time()
        response = self.client.post(
            "/api/wizard/steps/save/",
            {"step": 1, "data": {"project_name": "Test", "week_start": "2026-01-01"}},
            format="json",
        )
        elapsed = (time.time() - start) * 1000  # en ms

        self.assertEqual(response.status_code, 200)
        self.assertLess(
            elapsed,
            PERFORMANCE_LIMITS["endpoint_response_time_ms"],
            f"save_step tardó {elapsed:.2f}ms, esperado < {PERFORMANCE_LIMITS['endpoint_response_time_ms']}ms",
        )

    def test_validate_step_response_time(self):
        """Verificar que validate_step responde en < 500ms"""
        start = time.time()
        response = self.client.post(
            "/api/wizard/validate/",
            {"step": 1, "data": {"project_name": "Test"}},
            format="json",
        )
        elapsed = (time.time() - start) * 1000

        self.assertEqual(response.status_code, 200)
        self.assertLess(
            elapsed,
            PERFORMANCE_LIMITS["endpoint_response_time_ms"],
            f"validate_step tardó {elapsed:.2f}ms, esperado < {PERFORMANCE_LIMITS['endpoint_response_time_ms']}ms",
        )

    def test_sync_response_time(self):
        """Verificar que sync responde en < 500ms"""
        start = time.time()
        response = self.client.post(
            "/api/wizard/sync/",
            {
                "steps": [
                    {"step": 1, "data": {"project_name": "Test", "week_start": "2026-01-01"}},
                    {"step": 2, "data": {"progress_pct": 20}},
                ]
            },
            format="json",
        )
        elapsed = (time.time() - start) * 1000

        self.assertEqual(response.status_code, 200)
        self.assertLess(
            elapsed,
            PERFORMANCE_LIMITS["endpoint_response_time_ms"],
            f"sync tardó {elapsed:.2f}ms, esperado < {PERFORMANCE_LIMITS['endpoint_response_time_ms']}ms",
        )

    def test_verify_password_response_time(self):
        """Verificar que verify_password responde en < 500ms"""
        start = time.time()
        response = self.client.post(
            "/api/wizard/verify-password/",
            {"password": "password123"},
            format="json",
        )
        elapsed = (time.time() - start) * 1000

        self.assertEqual(response.status_code, 200)
        self.assertLess(
            elapsed,
            PERFORMANCE_LIMITS["endpoint_response_time_ms"],
            f"verify_password tardó {elapsed:.2f}ms, esperado < {PERFORMANCE_LIMITS['endpoint_response_time_ms']}ms",
        )


class PerformanceQueryTests(APITestCase):
    """Tests de optimización de queries (N+1)"""

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
            username="testuser",
            email="test@sitec.mx",
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
        self.client.login(username="testuser", password="password123")

    def test_save_step_query_count(self):
        """Verificar que save_step no hace queries N+1"""
        reset_queries()
        response = self.client.post(
            "/api/wizard/steps/save/",
            {"step": 1, "data": {"project_name": "Test", "week_start": "2026-01-01"}},
            format="json",
        )
        query_count = len(connection.queries)

        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(
            query_count,
            PERFORMANCE_LIMITS["max_queries_per_request"],
            f"save_step ejecutó {query_count} queries, esperado <= {PERFORMANCE_LIMITS['max_queries_per_request']}",
        )

    def test_sync_query_count(self):
        """Verificar que sync no hace queries N+1"""
        reset_queries()
        response = self.client.post(
            "/api/wizard/sync/",
            {
                "steps": [
                    {"step": 1, "data": {"project_name": "Test", "week_start": "2026-01-01"}},
                    {"step": 2, "data": {"progress_pct": 20}},
                ]
            },
            format="json",
        )
        query_count = len(connection.queries)

        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(
            query_count,
            PERFORMANCE_LIMITS["max_queries_per_request"] * 2,  # Permite más para múltiples steps
            f"sync ejecutó {query_count} queries, esperado <= {PERFORMANCE_LIMITS['max_queries_per_request'] * 2}",
        )


class PerformanceBundleSizeTests(TestCase):
    """Tests de tamaño de bundles JavaScript"""

    def test_js_bundle_size_within_limits(self):
        """Verificar que el tamaño total de JS no excede 100KB"""
        js_dir = Path(__file__).parent.parent.parent / "static" / "frontend" / "js"
        js_files = ["wizard.js", "pwa.js", "sync.js", "analytics.js", "performance.js"]

        total_size = 0
        for js_file in js_files:
            file_path = js_dir / js_file
            if file_path.exists():
                total_size += file_path.stat().st_size

        total_kb = total_size / 1024
        limit_kb = PERFORMANCE_LIMITS["js_bundle_size_kb"]

        self.assertLessEqual(
            total_kb,
            limit_kb,
            f"Tamaño total de JS ({total_kb:.2f}KB) excede límite ({limit_kb}KB)",
        )

    def test_individual_js_file_sizes(self):
        """Verificar tamaño de archivos JS individuales"""
        js_dir = Path(__file__).parent.parent.parent / "static" / "frontend" / "js"
        js_files = {
            "wizard.js": 150,  # KB - puede ser el más grande
            "pwa.js": 5,
            "sync.js": 10,
            "analytics.js": 10,
            "performance.js": 8,
        }

        for js_file, max_kb in js_files.items():
            file_path = js_dir / js_file
            if file_path.exists():
                size_kb = file_path.stat().st_size / 1024
                self.assertLessEqual(
                    size_kb,
                    max_kb,
                    f"{js_file} ({size_kb:.2f}KB) excede límite sugerido ({max_kb}KB)",
                )


class PerformanceConcurrentRequestsTests(APITestCase):
    """Tests de performance bajo carga concurrente"""

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
            username="testuser",
            email="test@sitec.mx",
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
        self.client.login(username="testuser", password="password123")

    def test_multiple_save_operations_performance(self):
        """Verificar que múltiples operaciones de guardado mantienen performance"""
        start = time.time()
        for i in range(10):
            response = self.client.post(
                "/api/wizard/steps/save/",
                {"step": i % 12 + 1, "data": {"project_name": f"Test {i}", "week_start": "2026-01-01"}},
                format="json",
            )
            self.assertEqual(response.status_code, 200)
        elapsed = (time.time() - start) * 1000

        avg_time = elapsed / 10
        self.assertLess(
            avg_time,
            PERFORMANCE_LIMITS["endpoint_response_time_ms"],
            f"Tiempo promedio ({avg_time:.2f}ms) excede límite ({PERFORMANCE_LIMITS['endpoint_response_time_ms']}ms)",
        )


class PerformanceMetricsEndpointTests(APITestCase):
    """Tests del endpoint de métricas de performance"""

    def test_performance_metrics_warnings(self):
        response = self.client.post(
            "/api/wizard/performance/metrics/",
            {
                "fcp": 1200,
                "tti": 3000,
                "lcp": 3200,
                "cls": 0.2,
                "ttfb": 1200,
                "js_size": 150 * 1024,
                "resource_count": 80,
                "load_time": 5000,
                "url": "http://testserver/wizard/1/",
                "timestamp": "2026-01-18T10:00:00Z",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        warnings = response.data.get("warnings", [])
        self.assertTrue(any("FCP" in warning for warning in warnings))
        self.assertTrue(any("TTI" in warning for warning in warnings))
        self.assertTrue(any("LCP" in warning for warning in warnings))
        self.assertTrue(any("CLS" in warning for warning in warnings))
        self.assertTrue(any("TTFB" in warning for warning in warnings))
        self.assertTrue(any("JS size" in warning for warning in warnings))
        self.assertTrue(
            AuditLog.objects.filter(action="performance_metrics").exists()
        )


class RequestMetricsMiddlewareTests(APITestCase):
    """Tests de headers y auditoría de métricas"""

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
            username="testuser",
            email="test@sitec.mx",
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
        self.client.login(username="testuser", password="password123")

    @override_settings(OBS_SLOW_REQUEST_MS=0)
    def test_request_metrics_headers_and_audit(self):
        response = self.client.get("/api/wizard/schema/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("X-Request-ID", response.headers)
        self.assertIn("X-Response-Time-ms", response.headers)
        entry = AuditLog.objects.filter(action="request_metrics").order_by("-created_at").first()
        self.assertIsNotNone(entry)
        self.assertEqual(entry.after.get("path"), "/api/wizard/schema/")
