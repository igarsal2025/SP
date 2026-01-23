"""
Vistas avanzadas de ROI: metas, tendencias y análisis extendido
"""
from datetime import date, timedelta

from django.core.cache import cache
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import AccessPolicyPermission
from apps.projects.models import Proyecto

from .services import build_roi_payload


class RoiTrendsView(APIView):
    """Endpoint para tendencias históricas de ROI"""
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def get(self, request):
        company = request.company
        sitec = request.sitec
        periods = int(request.query_params.get("periods", 12))
        period_type = request.query_params.get("type", "month")  # 'month' o 'week'
        
        if period_type not in ["month", "week"]:
            period_type = "month"
        
        # Cache key único
        cache_key = f"roi_trends_{company.id}_{sitec.id}_{periods}_{period_type}"
        cache_ttl = 60 * 15  # 15 minutos
        
        # Intentar obtener del cache
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        # Construir datos de tendencias
        trends = self._build_trends_data(company, sitec, periods=periods, period_type=period_type)
        response_data = {
            "period_type": period_type,
            "periods": periods,
            "trends": trends,
        }
        
        # Guardar en cache
        cache.set(cache_key, response_data, cache_ttl)
        
        return Response(response_data)
    
    def _build_trends_data(self, company, sitec, periods=12, period_type="month"):
        """Construir datos de tendencias de ROI"""
        now = timezone.now()
        trends = []
        
        for i in range(periods - 1, -1, -1):
            if period_type == "month":
                period_start = (now - timedelta(days=30 * i)).replace(day=1).date()
                period_end = (period_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            else:  # week
                period_start = (now - timedelta(weeks=i)).date()
                period_end = period_start + timedelta(days=6)
            
            # Calcular ROI para este período
            projects = Proyecto.objects.filter(
                company=company,
                sitec=sitec,
                created_at__date__gte=period_start,
                created_at__date__lte=period_end
            )
            
            total_estimated = sum(
                float(p.budget_estimated) if p.budget_estimated is not None else 0 
                for p in projects
            )
            total_actual = sum(
                float(p.budget_actual) if p.budget_actual is not None else 0 
                for p in projects
            )
            
            roi_pct = None
            if total_estimated > 0:
                roi_pct = round(((total_estimated - total_actual) / total_estimated) * 100, 1)
            
            trends.append({
                "period": period_start.strftime("%Y-%m-%d"),
                "period_label": period_start.strftime("%b %Y") if period_type == "month" else f"Semana {period_start.isocalendar()[1]}",
                "total_estimated": round(total_estimated, 2),
                "total_actual": round(total_actual, 2),
                "roi_pct": roi_pct,
                "projects_count": projects.count(),
            })
        
        # Calcular deltas
        for i in range(1, len(trends)):
            prev = trends[i - 1]
            curr = trends[i]
            if prev["roi_pct"] is not None and curr["roi_pct"] is not None:
                curr["delta"] = round(curr["roi_pct"] - prev["roi_pct"], 1)
            else:
                curr["delta"] = None
        
        return trends


class RoiGoalsView(APIView):
    """Endpoint para gestionar metas de ROI"""
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def get(self, request):
        """Obtener metas de ROI configuradas"""
        company = request.company
        sitec = request.sitec
        
        # Por ahora, usar configuración simple desde settings o defaults
        # En el futuro, podría ser un modelo RoiGoal
        goals = {
            "target_roi_pct": float(request.query_params.get("target_roi_pct", 10.0)),
            "target_projects": int(request.query_params.get("target_projects", 0)),
            "max_overruns": int(request.query_params.get("max_overruns", 5)),
        }
        
        # Obtener ROI actual para comparar
        period_days = int(request.query_params.get("period_days", 30))
        current_roi = build_roi_payload(company, sitec, period_days=period_days)
        
        # Evaluar cumplimiento de metas
        goals["status"] = {
            "roi_met": current_roi.get("avg_roi_pct", 0) >= goals["target_roi_pct"] if current_roi.get("avg_roi_pct") else False,
            "projects_met": current_roi.get("projects_total", 0) >= goals["target_projects"] if goals["target_projects"] > 0 else None,
            "overruns_ok": current_roi.get("overruns", 0) <= goals["max_overruns"],
        }
        
        return Response({
            "goals": goals,
            "current": {
                "avg_roi_pct": current_roi.get("avg_roi_pct"),
                "projects_total": current_roi.get("projects_total"),
                "overruns": current_roi.get("overruns"),
            },
        })


class RoiAnalysisView(APIView):
    """Endpoint para análisis avanzado de ROI"""
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def get(self, request):
        """Análisis avanzado de ROI con insights"""
        company = request.company
        sitec = request.sitec
        period_days = int(request.query_params.get("period_days", 30))
        
        now = timezone.now()
        start = now - timedelta(days=period_days)
        projects = Proyecto.objects.filter(company=company, sitec=sitec, created_at__gte=start)
        
        # Análisis por estado
        by_status = {}
        for status in ["planning", "in_progress", "on_hold", "completed", "cancelled"]:
            status_projects = projects.filter(status=status)
            if status_projects.exists():
                total_est = sum(float(p.budget_estimated) if p.budget_estimated is not None else 0 for p in status_projects)
                total_act = sum(float(p.budget_actual) if p.budget_actual is not None else 0 for p in status_projects)
                roi_pct = None
                if total_est > 0:
                    roi_pct = round(((total_est - total_act) / total_est) * 100, 1)
                
                by_status[status] = {
                    "count": status_projects.count(),
                    "total_estimated": round(total_est, 2),
                    "total_actual": round(total_act, 2),
                    "avg_roi_pct": roi_pct,
                }
        
        # Proyectos con mejor/peor ROI
        projects_with_roi = [
            p for p in projects 
            if p.budget_estimated is not None and p.budget_actual is not None
        ]
        
        def _roi_key(p):
            if p.budget_estimated and p.budget_estimated > 0:
                return (float(p.budget_estimated) - float(p.budget_actual)) / float(p.budget_estimated)
            return 0
        
        best_projects = sorted(
            projects_with_roi,
            key=_roi_key,
            reverse=True
        )[:5]
        
        worst_projects = sorted(
            projects_with_roi,
            key=_roi_key,
        )[:5]
        
        return Response({
            "period_days": period_days,
            "by_status": by_status,
            "top_performers": [
                {
                    "id": str(p.id),
                    "code": p.code,
                    "name": p.name,
                    "roi_pct": round(((float(p.budget_estimated) - float(p.budget_actual)) / float(p.budget_estimated)) * 100, 1) if p.budget_estimated and p.budget_estimated > 0 else None,
                }
                for p in best_projects
            ],
            "underperformers": [
                {
                    "id": str(p.id),
                    "code": p.code,
                    "name": p.name,
                    "roi_pct": round(((float(p.budget_estimated) - float(p.budget_actual)) / float(p.budget_estimated)) * 100, 1) if p.budget_estimated and p.budget_estimated > 0 else None,
                }
                for p in worst_projects
            ],
        })
