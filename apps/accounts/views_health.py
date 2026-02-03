"""
Health check endpoints con verificación de dependencias
"""
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    """
    Health check básico - siempre accesible sin autenticación
    """
    permission_classes = []  # Sin autenticación requerida

    def get(self, request):
        return Response({
            "status": "ok",
            "service": "SITEC",
            "version": "1.0.0",
        })


class HealthCheckDetailedView(APIView):
    """
    Health check detallado con verificación de dependencias
    """
    permission_classes = []  # Sin autenticación requerida

    def get(self, request):
        checks = {
            "status": "ok",
            "service": "SITEC",
            "version": "1.0.0",
            "dependencies": {}
        }
        
        overall_status = "ok"
        
        # Verificar base de datos
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            checks["dependencies"]["database"] = {
                "status": "ok",
                "message": "Database connection successful"
            }
        except Exception as e:
            checks["dependencies"]["database"] = {
                "status": "error",
                "message": str(e)
            }
            overall_status = "degraded"
        
        # Verificar cache
        try:
            cache.set("health_check_test", "ok", 10)
            cache.get("health_check_test")
            cache.delete("health_check_test")
            checks["dependencies"]["cache"] = {
                "status": "ok",
                "message": "Cache connection successful"
            }
        except Exception as e:
            checks["dependencies"]["cache"] = {
                "status": "error",
                "message": str(e)
            }
            overall_status = "degraded"
        
        # Verificar proveedores opcionales
        nom151_configured = bool(getattr(settings, "NOM151_PROVIDER_URL", ""))
        ai_configured = bool(getattr(settings, "AI_TRAIN_PROVIDER_URL", ""))
        
        checks["dependencies"]["nom151"] = {
            "status": "configured" if nom151_configured else "optional",
            "message": "NOM-151 provider configured" if nom151_configured else "NOM-151 provider not configured (optional)"
        }
        
        checks["dependencies"]["ai"] = {
            "status": "configured" if ai_configured else "optional",
            "message": "AI provider configured" if ai_configured else "AI provider not configured (using local providers)"
        }
        
        checks["status"] = overall_status
        
        status_code = 200 if overall_status == "ok" else 503
        return Response(checks, status=status_code)
