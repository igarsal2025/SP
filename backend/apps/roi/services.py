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
        # Convertir Decimal a float para evitar problemas de serialización JSON
        estimated = float(project.budget_estimated) if project.budget_estimated is not None else None
        actual = float(project.budget_actual) if project.budget_actual is not None else None
        roi_pct = _roi_pct(estimated, actual)
        if roi_pct is not None:
            roi_values.append(roi_pct)
        if estimated:
            total_estimated += estimated
        if actual:
            total_actual += actual
            if estimated and actual > estimated:
                overruns += 1
        items.append(
            {
                "id": str(project.id),
                "code": project.code,
                "name": project.name,
                "estimated": estimated,
                "actual": actual,
                "roi_pct": roi_pct,
                "progress_pct": float(project.progress_pct) if project.progress_pct is not None else None,
            }
        )

    avg_roi = round(sum(roi_values) / len(roi_values), 1) if roi_values else None
    
    # Calcular comparativos históricos
    prev_start = start - timedelta(days=period_days)
    prev_projects = Proyecto.objects.filter(
        company=company, 
        sitec=sitec, 
        created_at__gte=prev_start,
        created_at__lt=start
    )
    
    prev_total_estimated = sum(
        float(p.budget_estimated) if p.budget_estimated is not None else 0 
        for p in prev_projects
    )
    prev_total_actual = sum(
        float(p.budget_actual) if p.budget_actual is not None else 0 
        for p in prev_projects
    )
    prev_avg_roi = None
    if prev_projects.exists():
        prev_roi_values = [
            _roi_pct(float(p.budget_estimated), float(p.budget_actual))
            for p in prev_projects
            if p.budget_estimated is not None and p.budget_actual is not None
        ]
        if prev_roi_values:
            prev_avg_roi = round(sum(prev_roi_values) / len(prev_roi_values), 1)
    
    # Calcular deltas
    total_estimated_delta = total_estimated - prev_total_estimated if prev_total_estimated > 0 else None
    total_actual_delta = total_actual - prev_total_actual if prev_total_actual > 0 else None
    avg_roi_delta = avg_roi - prev_avg_roi if avg_roi is not None and prev_avg_roi is not None else None
    
    # Calcular porcentajes de cambio
    def _pct_change(current, previous):
        if not previous or previous == 0:
            return None
        return round(((current - previous) / previous) * 100, 1)
    
    total_estimated_pct = _pct_change(total_estimated, prev_total_estimated)
    total_actual_pct = _pct_change(total_actual, prev_total_actual)
    
    payload = {
        "period_days": period_days,
        "projects_total": projects.count(),
        "total_estimated": round(total_estimated, 2),
        "total_actual": round(total_actual, 2),
        "avg_roi_pct": avg_roi,
        "overruns": overruns,
        "projects": items[:50],
        # Comparativos históricos
        "comparatives": {
            "total_estimated_delta": round(total_estimated_delta, 2) if total_estimated_delta is not None else None,
            "total_estimated_pct": total_estimated_pct,
            "total_actual_delta": round(total_actual_delta, 2) if total_actual_delta is not None else None,
            "total_actual_pct": total_actual_pct,
            "avg_roi_delta": avg_roi_delta,
            "prev_period": {
                "total_estimated": round(prev_total_estimated, 2),
                "total_actual": round(prev_total_actual, 2),
                "avg_roi_pct": prev_avg_roi,
            },
        },
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
