"""
Vistas para estadísticas de uso y costos de IA
"""
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import AccessPolicyPermission

from .services import get_ai_usage_stats


class AiUsageStatsView(APIView):
    """
    Endpoint para obtener estadísticas de uso de IA
    GET /api/ai/stats/?days=30&user_id=<uuid>
    """
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def get(self, request):
        days = int(request.query_params.get("days", 30))
        user_id = request.query_params.get("user_id")
        
        # Solo admins pueden ver stats de otros usuarios
        user = None
        if user_id and hasattr(request.user, "userprofile"):
            profile = request.user.userprofile
            if profile.role in ["admin_empresa", "pm"]:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    user = User.objects.get(id=user_id, userprofile__company=request.company)
                except User.DoesNotExist:
                    pass
        
        stats = get_ai_usage_stats(request.company, user, days=days)
        return Response(stats, status=status.HTTP_200_OK)
