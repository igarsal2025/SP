"""
Middlewares para accounts: CompanySitecMiddleware y RateLimitMiddleware
"""
import time
from collections import defaultdict
from django.core.cache import cache
from django.http import JsonResponse

from apps.companies.models import Sitec

from .models import UserProfile


class CompanySitecMiddleware:
    """Adjunta company y sitec al request para consumo uniforme."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.company = None
        request.sitec = None

        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            profile = UserProfile.objects.select_related("company").filter(user=user).first()
            if profile and profile.company:
                request.company = profile.company
                request.sitec = (
                    Sitec.objects.filter(company=profile.company, status="active")
                    .order_by("created_at")
                    .first()
                )

        if self._requires_company_sitec(request) and user and user.is_authenticated:
            if request.company is None or request.sitec is None:
                return JsonResponse(
                    {
                        "detail": "Configuracion SITEC incompleta. Ejecute seed_sitec.",
                    },
                    status=400,
                )

        return self.get_response(request)

    def _requires_company_sitec(self, request):
        if not request.path.startswith("/api/"):
            return False
        if request.path.startswith("/api/users/me/"):
            return False
        return True


class RateLimitMiddleware:
    """
    Middleware básico de rate limiting por IP
    Configurable vía settings: RATE_LIMIT_ENABLED, RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Cache en memoria como fallback (no usar en producción con múltiples workers)
        self._memory_cache = defaultdict(list)
    
    def __call__(self, request):
        # Solo aplicar rate limiting si está habilitado
        from django.conf import settings
        rate_limit_enabled = getattr(settings, "RATE_LIMIT_ENABLED", False)
        
        if not rate_limit_enabled:
            return self.get_response(request)
        
        # Obtener configuración
        max_requests = getattr(settings, "RATE_LIMIT_REQUESTS", 100)
        window_seconds = getattr(settings, "RATE_LIMIT_WINDOW", 60)
        
        # Obtener IP del cliente
        ip = self._get_client_ip(request)
        
        # Verificar rate limit
        if self._is_rate_limited(ip, max_requests, window_seconds):
            return JsonResponse(
                {
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Maximum {max_requests} requests per {window_seconds} seconds.",
                },
                status=429,
            )
        
        # Registrar request
        self._record_request(ip, window_seconds)
        
        return self.get_response(request)
    
    def _get_client_ip(self, request):
        """Obtiene la IP real del cliente"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR", "unknown")
        return ip
    
    def _is_rate_limited(self, ip, max_requests, window_seconds):
        """Verifica si la IP está rate limited"""
        cache_key = f"rate_limit:{ip}"
        
        # Intentar usar cache de Django
        try:
            requests = cache.get(cache_key, [])
        except Exception:
            # Fallback a memoria si cache falla
            requests = self._memory_cache.get(ip, [])
        
        # Limpiar requests fuera de la ventana
        now = time.time()
        requests = [req_time for req_time in requests if now - req_time < window_seconds]
        
        return len(requests) >= max_requests
    
    def _record_request(self, ip, window_seconds):
        """Registra una request para rate limiting"""
        cache_key = f"rate_limit:{ip}"
        now = time.time()
        
        try:
            requests = cache.get(cache_key, [])
            requests.append(now)
            # Limpiar requests fuera de la ventana
            requests = [req_time for req_time in requests if now - req_time < window_seconds]
            cache.set(cache_key, requests, timeout=window_seconds)
        except Exception:
            # Fallback a memoria si cache falla
            if ip not in self._memory_cache:
                self._memory_cache[ip] = []
            self._memory_cache[ip].append(now)
            # Limpiar memoria periódicamente (mantener solo últimos 1000 IPs)
            if len(self._memory_cache) > 1000:
                oldest_ip = min(self._memory_cache.keys(), key=lambda k: max(self._memory_cache[k]) if self._memory_cache[k] else 0)
                del self._memory_cache[oldest_ip]
