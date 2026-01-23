"""
Rate Limiting Avanzado
- Rate limiting por IP
- Rate limiting por usuario autenticado
- Rate limiting por endpoint con límites configurables
- Headers de rate limit en respuestas
"""
import time
import logging
from collections import defaultdict
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings

logger = logging.getLogger(__name__)


class AdvancedRateLimitMiddleware:
    """
    Middleware avanzado de rate limiting con soporte para:
    - Rate limiting por IP
    - Rate limiting por usuario autenticado
    - Rate limiting por endpoint con límites configurables
    - Headers informativos en respuestas
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Cache en memoria como fallback (no usar en producción con múltiples workers)
        self._memory_cache = defaultdict(dict)
    
    def __call__(self, request):
        # Solo aplicar rate limiting si está habilitado
        rate_limit_enabled = getattr(settings, "RATE_LIMIT_ENABLED", False)
        
        if not rate_limit_enabled:
            return self.get_response(request)
        
        # Obtener configuración de rate limit para este endpoint
        endpoint_config = self._get_endpoint_config(request.path, request.method)
        
        # Si el endpoint está excluido, no aplicar rate limiting
        if endpoint_config is None:
            return self.get_response(request)
        
        # Obtener identificadores para rate limiting
        ip = self._get_client_ip(request)
        user_id = self._get_user_id(request)
        
        # Verificar rate limits
        rate_limit_result = self._check_rate_limits(
            ip=ip,
            user_id=user_id,
            endpoint=request.path,
            method=request.method,
            config=endpoint_config
        )
        
        # Si está rate limited, retornar error
        if rate_limit_result["limited"]:
            logger.warning(
                f"Rate limit exceeded: IP={ip}, User={user_id}, Endpoint={request.path}, "
                f"Limit={rate_limit_result['limit']}, Remaining={rate_limit_result['remaining']}"
            )
            
            response = JsonResponse(
                {
                    "error": "Rate limit exceeded",
                    "message": rate_limit_result["message"],
                    "limit": rate_limit_result["limit"],
                    "remaining": rate_limit_result["remaining"],
                    "reset_at": rate_limit_result["reset_at"],
                },
                status=429,
            )
            
            # Agregar headers informativos
            self._add_rate_limit_headers(response, rate_limit_result)
            return response
        
        # Registrar request
        self._record_request(
            ip=ip,
            user_id=user_id,
            endpoint=request.path,
            method=request.method,
            config=endpoint_config
        )
        
        # Procesar request
        response = self.get_response(request)
        
        # Agregar headers informativos a la respuesta
        rate_limit_info = self._get_rate_limit_info(
            ip=ip,
            user_id=user_id,
            endpoint=request.path,
            method=request.method,
            config=endpoint_config
        )
        self._add_rate_limit_headers(response, rate_limit_info)
        
        return response
    
    def _get_client_ip(self, request):
        """Obtiene la IP real del cliente"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR", "unknown")
        return ip
    
    def _get_user_id(self, request):
        """Obtiene el ID del usuario si está autenticado"""
        user = getattr(request, "user", None)
        if user and user.is_authenticated and hasattr(user, "pk"):
            return f"user:{user.pk}"
        return None
    
    def _get_endpoint_config(self, path, method):
        """
        Obtiene la configuración de rate limit para un endpoint específico.
        Retorna None si el endpoint está excluido del rate limiting.
        """
        # Configuración por endpoint (desde settings)
        endpoint_configs = getattr(settings, "RATE_LIMIT_ENDPOINTS", {})
        
        # Buscar configuración específica para este endpoint
        for pattern, config in endpoint_configs.items():
            if self._path_matches(pattern, path):
                # Puede tener configuración por método
                if isinstance(config, dict) and method in config:
                    return config[method]
                elif isinstance(config, dict) and "default" in config:
                    return config["default"]
                elif isinstance(config, dict):
                    return config
                else:
                    return config
        
        # Endpoints excluidos del rate limiting
        excluded_paths = getattr(settings, "RATE_LIMIT_EXCLUDED_PATHS", [
            "/health/",
            "/health/detailed/",
            "/api/metrics/",
        ])
        
        for excluded in excluded_paths:
            if self._path_matches(excluded, path):
                return None
        
        # Configuración global por defecto
        return {
            "ip": {
                "requests": getattr(settings, "RATE_LIMIT_REQUESTS", 100),
                "window": getattr(settings, "RATE_LIMIT_WINDOW", 60),
            },
            "user": {
                "requests": getattr(settings, "RATE_LIMIT_USER_REQUESTS", 200),
                "window": getattr(settings, "RATE_LIMIT_USER_WINDOW", 60),
            },
        }
    
    def _path_matches(self, pattern, path):
        """Verifica si un path coincide con un patrón"""
        if pattern == path:
            return True
        if pattern.endswith("*") and path.startswith(pattern[:-1]):
            return True
        if pattern.startswith("*") and path.endswith(pattern[1:]):
            return True
        return False
    
    def _check_rate_limits(self, ip, user_id, endpoint, method, config):
        """
        Verifica todos los rate limits aplicables y retorna el resultado más restrictivo
        """
        now = time.time()
        result = {
            "limited": False,
            "limit": 0,
            "remaining": 0,
            "reset_at": now,
            "message": "",
            "type": None,  # "ip" o "user"
        }
        
        # Verificar rate limit por IP
        if "ip" in config:
            ip_config = config["ip"]
            ip_key = f"rate_limit:ip:{ip}:{endpoint}:{method}"
            ip_result = self._check_single_rate_limit(
                key=ip_key,
                max_requests=ip_config["requests"],
                window_seconds=ip_config["window"],
                now=now
            )
            
            if ip_result["limited"]:
                result.update({
                    "limited": True,
                    "limit": ip_result["limit"],
                    "remaining": ip_result["remaining"],
                    "reset_at": ip_result["reset_at"],
                    "message": f"Too many requests from this IP. Maximum {ip_result['limit']} requests per {ip_config['window']} seconds.",
                    "type": "ip",
                })
                return result
        
        # Verificar rate limit por usuario (si está autenticado)
        if user_id and "user" in config:
            user_config = config["user"]
            user_key = f"rate_limit:user:{user_id}:{endpoint}:{method}"
            user_result = self._check_single_rate_limit(
                key=user_key,
                max_requests=user_config["requests"],
                window_seconds=user_config["window"],
                now=now
            )
            
            if user_result["limited"]:
                result.update({
                    "limited": True,
                    "limit": user_result["limit"],
                    "remaining": user_result["remaining"],
                    "reset_at": user_result["reset_at"],
                    "message": f"Too many requests. Maximum {user_result['limit']} requests per {user_config['window']} seconds.",
                    "type": "user",
                })
                return result
        
        # Si no está limitado, calcular remaining basado en el límite más restrictivo
        if "ip" in config and "user" in config:
            # Usar el límite más restrictivo
            ip_limit = config["ip"]["requests"]
            user_limit = config["user"]["requests"]
            min_limit = min(ip_limit, user_limit)
            
            # Calcular remaining basado en ambos
            ip_key = f"rate_limit:ip:{ip}:{endpoint}:{method}"
            user_key = f"rate_limit:user:{user_id}:{endpoint}:{method}" if user_id else None
            
            ip_count = self._get_request_count(ip_key, config["ip"]["window"], now)
            user_count = self._get_request_count(user_key, config["user"]["window"], now) if user_key else 0
            
            # Remaining es el mínimo de los dos
            remaining = min(
                config["ip"]["requests"] - ip_count,
                config["user"]["requests"] - user_count if user_id else float('inf')
            )
            
            result.update({
                "limit": min_limit,
                "remaining": max(0, int(remaining)),
                "reset_at": now + min(config["ip"]["window"], config["user"]["window"]),
            })
        elif "ip" in config:
            ip_key = f"rate_limit:ip:{ip}:{endpoint}:{method}"
            ip_count = self._get_request_count(ip_key, config["ip"]["window"], now)
            result.update({
                "limit": config["ip"]["requests"],
                "remaining": max(0, config["ip"]["requests"] - ip_count),
                "reset_at": now + config["ip"]["window"],
            })
        elif "user" in config and user_id:
            user_key = f"rate_limit:user:{user_id}:{endpoint}:{method}"
            user_count = self._get_request_count(user_key, config["user"]["window"], now)
            result.update({
                "limit": config["user"]["requests"],
                "remaining": max(0, config["user"]["requests"] - user_count),
                "reset_at": now + config["user"]["window"],
            })
        
        return result
    
    def _check_single_rate_limit(self, key, max_requests, window_seconds, now):
        """Verifica un rate limit individual"""
        requests = self._get_requests(key, window_seconds, now)
        count = len(requests)
        
        return {
            "limited": count >= max_requests,
            "limit": max_requests,
            "remaining": max(0, max_requests - count),
            "reset_at": now + window_seconds,
        }
    
    def _get_requests(self, key, window_seconds, now):
        """Obtiene las requests dentro de la ventana de tiempo"""
        try:
            requests = cache.get(key, [])
        except Exception:
            # Fallback a memoria si cache falla
            requests = self._memory_cache.get(key, {}).get("requests", [])
        
        # Limpiar requests fuera de la ventana
        requests = [req_time for req_time in requests if now - req_time < window_seconds]
        return requests
    
    def _get_request_count(self, key, window_seconds, now):
        """Obtiene el conteo de requests dentro de la ventana"""
        requests = self._get_requests(key, window_seconds, now)
        return len(requests)
    
    def _record_request(self, ip, user_id, endpoint, method, config):
        """Registra una request para rate limiting"""
        now = time.time()
        
        # Registrar por IP
        if "ip" in config:
            ip_key = f"rate_limit:ip:{ip}:{endpoint}:{method}"
            self._record_single_request(ip_key, config["ip"]["window"], now)
        
        # Registrar por usuario
        if user_id and "user" in config:
            user_key = f"rate_limit:user:{user_id}:{endpoint}:{method}"
            self._record_single_request(user_key, config["user"]["window"], now)
    
    def _record_single_request(self, key, window_seconds, now):
        """Registra una request individual"""
        try:
            requests = cache.get(key, [])
            requests.append(now)
            # Limpiar requests fuera de la ventana
            requests = [req_time for req_time in requests if now - req_time < window_seconds]
            cache.set(key, requests, timeout=window_seconds + 10)  # +10 para margen
        except Exception:
            # Fallback a memoria si cache falla
            if key not in self._memory_cache:
                self._memory_cache[key] = {"requests": []}
            self._memory_cache[key]["requests"].append(now)
            # Limpiar memoria periódicamente
            if len(self._memory_cache) > 1000:
                oldest_key = min(
                    self._memory_cache.keys(),
                    key=lambda k: max(self._memory_cache[k]["requests"]) if self._memory_cache[k]["requests"] else 0
                )
                del self._memory_cache[oldest_key]
    
    def _get_rate_limit_info(self, ip, user_id, endpoint, method, config):
        """Obtiene información de rate limit para headers"""
        now = time.time()
        
        # Calcular remaining y limit basado en configuración
        if "ip" in config and "user" in config and user_id:
            # Usar el límite más restrictivo
            ip_limit = config["ip"]["requests"]
            user_limit = config["user"]["requests"]
            min_limit = min(ip_limit, user_limit)
            
            ip_key = f"rate_limit:ip:{ip}:{endpoint}:{method}"
            user_key = f"rate_limit:user:{user_id}:{endpoint}:{method}"
            
            ip_count = self._get_request_count(ip_key, config["ip"]["window"], now)
            user_count = self._get_request_count(user_key, config["user"]["window"], now)
            
            remaining = min(
                config["ip"]["requests"] - ip_count,
                config["user"]["requests"] - user_count
            )
            
            return {
                "limit": min_limit,
                "remaining": max(0, int(remaining)),
                "reset_at": now + min(config["ip"]["window"], config["user"]["window"]),
            }
        elif "ip" in config:
            ip_key = f"rate_limit:ip:{ip}:{endpoint}:{method}"
            ip_count = self._get_request_count(ip_key, config["ip"]["window"], now)
            return {
                "limit": config["ip"]["requests"],
                "remaining": max(0, config["ip"]["requests"] - ip_count),
                "reset_at": now + config["ip"]["window"],
            }
        elif "user" in config and user_id:
            user_key = f"rate_limit:user:{user_id}:{endpoint}:{method}"
            user_count = self._get_request_count(user_key, config["user"]["window"], now)
            return {
                "limit": config["user"]["requests"],
                "remaining": max(0, config["user"]["requests"] - user_count),
                "reset_at": now + config["user"]["window"],
            }
        
        return {
            "limit": 0,
            "remaining": 0,
            "reset_at": now,
        }
    
    def _add_rate_limit_headers(self, response, rate_limit_info):
        """Agrega headers informativos de rate limit a la respuesta"""
        # Agregar headers a cualquier tipo de respuesta HTTP
        if hasattr(response, "__setitem__"):
            response["X-RateLimit-Limit"] = str(rate_limit_info.get("limit", 0))
            response["X-RateLimit-Remaining"] = str(rate_limit_info.get("remaining", 0))
            response["X-RateLimit-Reset"] = str(int(rate_limit_info.get("reset_at", time.time())))
