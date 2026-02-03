from datetime import timedelta

from django.utils import timezone

from apps.projects.models import Proyecto

from .models import RoiSnapshot


def _roi_pct(estimated, actual):
    if not estimated or estimated <= 0 or actual is None:
        return None
    return round(((estimated - actual) / estimated) * 100, 1)


def build_roi_payload(company, sitec, period_days=30):
    now = timezone.now()
    start = now - timedelta(days=period_days)
    projects = Proyecto.objects.filter(company=company, sitec=sitec, created_at__gte=start)

    items = []
    total_estimated = 0
    total_actual = 0
    roi_values = []
    overruns = 0

    for project in projects:
        estimated = project.budget_estimated
        actual = project.budget_actual
        roi_pct = _roi_pct(estimated, actual)
        if roi_pct is not None:
            roi_values.append(roi_pct)
        if estimated:
            total_estimated += float(estimated)
        if actual:
            total_actual += float(actual)
            if estimated and actual > estimated:
                overruns += 1
        items.append(
            {
                "id": str(project.id),
                "code": project.code,
                "name": project.name,
                "estimated": float(estimated) if estimated is not None else None,
                "actual": float(actual) if actual is not None else None,
                "roi_pct": roi_pct,
                "progress_pct": project.progress_pct,
            }
        )

    avg_roi = round(sum(roi_values) / len(roi_values), 1) if roi_values else None
    payload = {
        "period_days": period_days,
        "projects_total": projects.count(),
        "total_estimated": round(total_estimated, 2),
        "total_actual": round(total_actual, 2),
        "avg_roi_pct": avg_roi,
        "overruns": overruns,
        "projects": items[:50],
    }
    return payload


def get_recent_snapshot(company, sitec, period_days=30):
    return (
        RoiSnapshot.objects.filter(company=company, sitec=sitec, period_days=period_days)
        .order_by("-computed_at")
        .first()
    )


def get_recent_snapshots(company, sitec, period_days=30, limit=12):
    return (
        RoiSnapshot.objects.filter(company=company, sitec=sitec, period_days=period_days)
        .order_by("-computed_at")[:limit]
    )


def create_snapshot(company, sitec, period_days=30, computed_at=None):
    computed_at = computed_at or timezone.now()
    payload = build_roi_payload(company, sitec, period_days=period_days)
    snapshot, _ = RoiSnapshot.objects.update_or_create(
        company=company,
        sitec=sitec,
        period_days=period_days,
        computed_at=computed_at,
        defaults={"payload": payload},
    )
    return snapshot
