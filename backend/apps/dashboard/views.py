from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import AccessPolicyPermission
from .models import DashboardSnapshot
from .services import (
    build_dashboard_payload,
    build_trends_data,
    create_snapshot,
    get_recent_aggregates,
    get_recent_snapshot,
)


class DashboardKpiView(APIView):
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def get(self, request):
        company = request.company
        sitec = request.sitec
        use_snapshot = request.query_params.get("snapshot") != "0"
        
        # Filtros opcionales
        project_id = request.query_params.get("project_id")
        # Validar que project_id es un UUID válido si está presente
        if project_id:
            try:
                from uuid import UUID
                UUID(project_id)  # Validar formato UUID
            except (ValueError, TypeError):
                project_id = None  # Ignorar si no es válido
        
        start_date_str = request.query_params.get("start_date")
        end_date_str = request.query_params.get("end_date")
        period_days = int(request.query_params.get("period_days", 7))
        
        # Si hay filtros personalizados, no usar snapshot
        has_custom_filters = project_id or start_date_str or end_date_str or period_days != 7
        
        ttl_minutes = int(getattr(settings, "DASHBOARD_SNAPSHOT_TTL_MINUTES", 15))
        snapshot = get_recent_snapshot(company, sitec, ttl_minutes=ttl_minutes) if use_snapshot and not has_custom_filters else None
        if snapshot:
            payload = snapshot.payload or {}
            payload["snapshot"] = {
                "computed_at": snapshot.computed_at,
                "source": "snapshot",
            }
            return Response(payload)

        # Construir payload con filtros opcionales
        if start_date_str and end_date_str:
            from datetime import datetime
            from django.utils import timezone
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                # Calcular período anterior para comparativos
                period_days = (end_date - start_date).days
                prev_start = start_date - timedelta(days=period_days)
                prev_end = start_date
                from .services import build_dashboard_payload_range
                payload = build_dashboard_payload_range(
                    company, sitec, start_date, end_date, prev_start, prev_end, project_id=project_id
                )
            except ValueError:
                from .services import build_dashboard_payload
                payload = build_dashboard_payload(company, sitec, period_days=period_days, project_id=project_id)
        else:
            from .services import build_dashboard_payload
            payload = build_dashboard_payload(company, sitec, period_days=period_days, project_id=project_id)
        
        if not has_custom_filters:
            snapshot = create_snapshot(company, sitec, period_days=period_days)
            payload["snapshot"] = {"computed_at": snapshot.computed_at, "source": "live"}
        else:
            payload["snapshot"] = {"source": "live", "filters_applied": True}
        return Response(payload)


class DashboardSnapshotHistoryView(APIView):
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def get(self, request):
        company = request.company
        sitec = request.sitec
        period_days = int(request.query_params.get("period_days", 30))
        limit = int(request.query_params.get("limit", 12))
        snapshots = (
            DashboardSnapshot.objects.filter(company=company, sitec=sitec, period_days=period_days)
            .select_related("company", "sitec")
            .order_by("-computed_at")[:limit]
        )
        payload = [
            {
                "computed_at": snapshot.computed_at,
                "period_days": snapshot.period_days,
                "payload": snapshot.payload,
            }
            for snapshot in snapshots
        ]
        return Response(payload)


class DashboardAggregateHistoryView(APIView):
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def get(self, request):
        company = request.company
        sitec = request.sitec
        limit = int(request.query_params.get("limit", 12))
        aggregates = get_recent_aggregates(company, sitec, period_label="month", limit=limit)
        payload = [
            {
                "period_start": agg.period_start,
                "period_end": agg.period_end,
                "payload": agg.payload,
            }
            for agg in aggregates
        ]
        return Response(payload)


class DashboardTrendsView(APIView):
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def get(self, request):
        company = request.company
        sitec = request.sitec
        periods = int(request.query_params.get("periods", 12))
        period_type = request.query_params.get("type", "month")  # 'month' o 'week'
        
        if period_type not in ["month", "week"]:
            period_type = "month"
        
        # Cache key único por company, sitec, periods y period_type
        cache_key = f"dashboard_trends_{company.id}_{sitec.id}_{periods}_{period_type}"
        cache_ttl = 60 * 15  # 15 minutos
        
        # Intentar obtener del cache
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        # Construir datos de tendencias
        trends = build_trends_data(company, sitec, periods=periods, period_type=period_type)
        response_data = {
            "period_type": period_type,
            "periods": periods,
            "trends": trends,
        }
        
        # Guardar en cache
        cache.set(cache_key, response_data, cache_ttl)
        
        return Response(response_data)
