import csv
from io import StringIO

from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import AccessPolicyPermission

from .services import (
    build_roi_payload,
    create_snapshot,
    get_recent_snapshot,
    get_recent_snapshots,
)


class RoiSnapshotView(APIView):
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def get(self, request):
        company = request.company
        sitec = request.sitec
        period_days = int(request.query_params.get("period_days", 30))
        snapshot = get_recent_snapshot(company, sitec, period_days=period_days)
        if snapshot:
            payload = snapshot.payload or {}
            payload["snapshot"] = {"computed_at": snapshot.computed_at, "source": "snapshot"}
            return Response(payload)
        payload = build_roi_payload(company, sitec, period_days=period_days)
        snapshot = create_snapshot(company, sitec, period_days=period_days)
        payload["snapshot"] = {"computed_at": snapshot.computed_at, "source": "live"}
        return Response(payload)


class RoiHistoryView(APIView):
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def get(self, request):
        company = request.company
        sitec = request.sitec
        period_days = int(request.query_params.get("period_days", 30))
        limit = int(request.query_params.get("limit", 12))
        snapshots = get_recent_snapshots(company, sitec, period_days=period_days, limit=limit)
        payload = [
            {
                "computed_at": snapshot.computed_at,
                "period_days": snapshot.period_days,
                "payload": snapshot.payload,
            }
            for snapshot in snapshots
        ]
        return Response(payload)


class RoiExportView(APIView):
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def get(self, request):
        company = request.company
        sitec = request.sitec
        period_days = int(request.query_params.get("period_days", 30))
        limit = int(request.query_params.get("limit", 50))
        snapshots = get_recent_snapshots(company, sitec, period_days=period_days, limit=limit)
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow(
            [
                "computed_at",
                "period_days",
                "projects_total",
                "total_estimated",
                "total_actual",
                "avg_roi_pct",
                "overruns",
            ]
        )
        for snapshot in snapshots:
            payload = snapshot.payload or {}
            writer.writerow(
                [
                    snapshot.computed_at.isoformat(),
                    snapshot.period_days,
                    payload.get("projects_total"),
                    payload.get("total_estimated"),
                    payload.get("total_actual"),
                    payload.get("avg_roi_pct"),
                    payload.get("overruns"),
                ]
            )
        response = HttpResponse(buffer.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="roi_history_{period_days}d.csv"'
        return response
