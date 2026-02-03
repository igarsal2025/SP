from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import AccessPolicyPermission
from .models import DashboardSnapshot
from .services import (
    build_dashboard_payload,
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
        ttl_minutes = int(getattr(settings, "DASHBOARD_SNAPSHOT_TTL_MINUTES", 15))
        snapshot = get_recent_snapshot(company, sitec, ttl_minutes=ttl_minutes) if use_snapshot else None
        if snapshot:
            payload = snapshot.payload or {}
            payload["snapshot"] = {
                "computed_at": snapshot.computed_at,
                "source": "snapshot",
            }
            return Response(payload)

        payload = build_dashboard_payload(company, sitec, period_days=7)
        snapshot = create_snapshot(company, sitec, period_days=7)
        payload["snapshot"] = {"computed_at": snapshot.computed_at, "source": "live"}
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
