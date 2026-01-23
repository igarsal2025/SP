"""
Servicios para throttling y tracking de costos de IA
"""
from datetime import datetime, timedelta
from django.core.cache import cache
from django.conf import settings
from django.db.models import Sum, Count, Q
from django.utils import timezone

from .models import AiSuggestion


def check_ai_throttle(company, user, mode="quick"):
    """
    Verifica si el usuario/company puede hacer una request de IA según límites configurados.
    
    Returns:
        (allowed: bool, reason: str, retry_after: int)
    """
    # Obtener configuración de límites
    throttle_enabled = getattr(settings, "AI_THROTTLE_ENABLED", False)
    if not throttle_enabled:
        return True, "throttle_disabled", 0
    
    # Límites por modo
    if mode == "quick":
        max_per_hour = getattr(settings, "AI_THROTTLE_QUICK_PER_HOUR", 100)
        max_per_day = getattr(settings, "AI_THROTTLE_QUICK_PER_DAY", 1000)
    elif mode == "heavy":
        max_per_hour = getattr(settings, "AI_THROTTLE_HEAVY_PER_HOUR", 10)
        max_per_day = getattr(settings, "AI_THROTTLE_HEAVY_PER_DAY", 100)
    else:
        return True, "unknown_mode", 0
    
    now = timezone.now()
    hour_ago = now - timedelta(hours=1)
    day_ago = now - timedelta(days=1)
    
    # Verificar límites por hora
    cache_key_hour = f"ai_throttle:{company.id}:{user.id}:{mode}:hour"
    count_hour = cache.get(cache_key_hour, 0)
    
    if count_hour >= max_per_hour:
        return False, "hourly_limit_exceeded", 3600
    
    # Verificar límites por día (usando DB para precisión)
    count_day = AiSuggestion.objects.filter(
        company=company,
        user=user,
        mode=mode,
        created_at__gte=day_ago
    ).count()
    
    if count_day >= max_per_day:
        return False, "daily_limit_exceeded", 86400
    
    return True, "allowed", 0


def record_ai_usage(company, user, mode="quick", cost_estimate=0.0):
    """
    Registra el uso de IA para throttling y tracking de costos.
    """
    throttle_enabled = getattr(settings, "AI_THROTTLE_ENABLED", False)
    if not throttle_enabled:
        return
    
    # Incrementar contador por hora en cache
    cache_key_hour = f"ai_throttle:{company.id}:{user.id}:{mode}:hour"
    count = cache.get(cache_key_hour, 0)
    cache.set(cache_key_hour, count + 1, timeout=3600)  # 1 hora
    
    # Registrar costo estimado (si está habilitado)
    cost_tracking_enabled = getattr(settings, "AI_COST_TRACKING_ENABLED", False)
    if cost_tracking_enabled and cost_estimate > 0:
        cache_key_cost = f"ai_cost:{company.id}:{user.id}:{timezone.now().date()}"
        total_cost = cache.get(cache_key_cost, 0.0)
        cache.set(cache_key_cost, total_cost + cost_estimate, timeout=86400)  # 1 día


def get_ai_usage_stats(company, user=None, days=30):
    """
    Obtiene estadísticas de uso de IA.
    
    Returns:
        dict con estadísticas de uso y costos
    """
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    query = Q(company=company, created_at__gte=start_date)
    if user:
        query &= Q(user=user)
    
    suggestions = AiSuggestion.objects.filter(query)
    
    stats = {
        "total_requests": suggestions.count(),
        "quick_requests": suggestions.filter(mode="quick").count(),
        "heavy_requests": suggestions.filter(mode="heavy").count(),
        "success_count": suggestions.filter(status="success").count(),
        "error_count": suggestions.filter(status="error").count(),
        "avg_latency_ms": suggestions.aggregate(
            avg=Sum("latency_ms") / Count("id")
        )["avg"] or 0,
        "total_cost_estimate": 0.0,  # Se calcularía según proveedor
        "by_day": {},
    }
    
    # Agrupar por día
    for day_offset in range(days):
        day = end_date - timedelta(days=day_offset)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        day_suggestions = suggestions.filter(created_at__gte=day_start, created_at__lt=day_end)
        stats["by_day"][day_start.date().isoformat()] = {
            "total": day_suggestions.count(),
            "quick": day_suggestions.filter(mode="quick").count(),
            "heavy": day_suggestions.filter(mode="heavy").count(),
        }
    
    return stats


def estimate_ai_cost(mode, model_name, latency_ms=0):
    """
    Estima el costo de una request de IA.
    
    Costos estimados (en USD):
    - quick (rule_engine): $0.0001 por request
    - quick (light_model): $0.001 por request
    - heavy: $0.01 por request
    - proveedor externo: según configuración
    """
    if mode == "quick":
        if "rule" in model_name.lower():
            return 0.0001
        else:
            return 0.001
    elif mode == "heavy":
        return 0.01
    else:
        return 0.0
