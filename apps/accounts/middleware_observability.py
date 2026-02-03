"""
Middleware para métricas de observabilidad
- Request timing
- Error rates
- Request counts por endpoint
"""
import time
from django.core.cache import cache
from django.conf import settings


class ObservabilityMiddleware:
    """
    Middleware para recopilar métricas de observabilidad básicas
    - Tiempo de respuesta por endpoint
    - Contador de requests por endpoint
    - Contador de errores por endpoint
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.metrics_enabled = getattr(settings, "OBSERVABILITY_ENABLED", True)
    
    def __call__(self, request):
        if not self.metrics_enabled:
            return self.get_response(request)
        
        # Iniciar timer
        start_time = time.time()
        
        # Obtener respuesta
        response = self.get_response(request)
        
        # Calcular tiempo de respuesta
        duration_ms = (time.time() - start_time) * 1000
        
        # Registrar métricas
        self._record_metrics(request, response, duration_ms)
        
        # Agregar header de timing
        response["X-Response-Time-ms"] = f"{duration_ms:.2f}"
        
        return response
    
    def _record_metrics(self, request, response, duration_ms):
        """Registra métricas en cache (para análisis posterior)"""
        try:
            endpoint = self._get_endpoint_name(request)
            
            # Métricas de timing
            timing_key = f"metrics:timing:{endpoint}"
            timings = cache.get(timing_key, [])
            timings.append(duration_ms)
            # Mantener solo últimos 100 timings
            if len(timings) > 100:
                timings = timings[-100:]
            cache.set(timing_key, timings, timeout=3600)  # 1 hora
            
            # Métricas de conteo
            count_key = f"metrics:count:{endpoint}"
            count = cache.get(count_key, 0)
            cache.set(count_key, count + 1, timeout=3600)
            
            # Métricas de errores
            if response.status_code >= 400:
                error_key = f"metrics:errors:{endpoint}"
                error_count = cache.get(error_key, 0)
                cache.set(error_key, error_count + 1, timeout=3600)
                
                # Registrar errores por código de estado
                status_key = f"metrics:status:{response.status_code}:{endpoint}"
                status_count = cache.get(status_key, 0)
                cache.set(status_key, status_count + 1, timeout=3600)
        except Exception:
            # Silenciar errores de métricas para no afectar la aplicación
            pass
    
    def _get_endpoint_name(self, request):
        """Obtiene un nombre identificable del endpoint"""
        path = request.path
        method = request.method
        
        # Normalizar path
        if path.startswith("/api/"):
            # Extraer nombre del endpoint
            parts = path.split("/")
            if len(parts) >= 3:
                # Ejemplo: /api/dashboard/kpi/ -> dashboard.kpi
                endpoint = ".".join(parts[2:-1] if parts[-1] == "" else parts[2:])
            else:
                endpoint = "unknown"
        else:
            endpoint = "static"
        
        return f"{method}:{endpoint}"


class RequestMetricsView:
    """
    View helper para obtener métricas de observabilidad
    (Se puede usar como endpoint o en admin)
    """
    
    @staticmethod
    def get_metrics(endpoint=None, hours=1):
        """
        Obtiene métricas de observabilidad
        
        Args:
            endpoint: Endpoint específico (opcional)
            hours: Horas de datos a obtener (default: 1)
        
        Returns:
            dict con métricas
        """
        metrics = {
            "endpoints": {},
            "summary": {
                "total_requests": 0,
                "total_errors": 0,
                "avg_response_time_ms": 0,
            }
        }
        
        try:
            # Obtener todos los endpoints si no se especifica uno
            if endpoint:
                endpoints = [endpoint]
            else:
                # Obtener todos los endpoints conocidos (simplificado)
                endpoints = [
                    "GET:dashboard.kpi",
                    "GET:dashboard.trends",
                    "GET:roi",
                    "POST:wizard.steps.save",
                    "POST:wizard.submit",
                    "POST:sync",
                ]
            
            total_requests = 0
            total_errors = 0
            total_timing = 0
            timing_count = 0
            
            for ep in endpoints:
                count_key = f"metrics:count:{ep}"
                error_key = f"metrics:errors:{ep}"
                timing_key = f"metrics:timing:{ep}"
                
                count = cache.get(count_key, 0)
                errors = cache.get(error_key, 0)
                timings = cache.get(timing_key, [])
                
                avg_timing = sum(timings) / len(timings) if timings else 0
                
                metrics["endpoints"][ep] = {
                    "requests": count,
                    "errors": errors,
                    "error_rate": (errors / count * 100) if count > 0 else 0,
                    "avg_response_time_ms": round(avg_timing, 2),
                    "min_response_time_ms": round(min(timings), 2) if timings else 0,
                    "max_response_time_ms": round(max(timings), 2) if timings else 0,
                }
                
                total_requests += count
                total_errors += errors
                total_timing += sum(timings)
                timing_count += len(timings)
            
            # Calcular resumen
            metrics["summary"]["total_requests"] = total_requests
            metrics["summary"]["total_errors"] = total_errors
            metrics["summary"]["error_rate"] = (total_errors / total_requests * 100) if total_requests > 0 else 0
            metrics["summary"]["avg_response_time_ms"] = round(total_timing / timing_count, 2) if timing_count > 0 else 0
            
        except Exception as e:
            metrics["error"] = str(e)
        
        return metrics
