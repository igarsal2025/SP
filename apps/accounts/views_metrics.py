"""
Endpoint para métricas de observabilidad
"""
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .middleware_observability import RequestMetricsView


class MetricsView(APIView):
    """
    Endpoint para obtener métricas de observabilidad
    Requiere autenticación
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Obtiene métricas de observabilidad
        
        Query params:
        - endpoint: Endpoint específico (opcional)
        - hours: Horas de datos (default: 1)
        """
        endpoint = request.query_params.get("endpoint")
        hours = int(request.query_params.get("hours", 1))
        
        metrics = RequestMetricsView.get_metrics(endpoint=endpoint, hours=hours)
        
        return Response(metrics)
