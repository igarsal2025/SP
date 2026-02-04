from datetime import date, timedelta

from django.utils import timezone

from apps.projects.models import Proyecto, Riesgo
from apps.reports.models import ReporteSemanal

from .models import DashboardAggregate, DashboardSnapshot


def _pct_delta(current, previous):
    if previous == 0:
        return None
    return round(((current - previous) / previous) * 100, 1)


def build_dashboard_payload(company, sitec, period_days=7, project_id=None):
    now = timezone.now()
    start_date = now.date() - timedelta(days=period_days)
    prev_start = now.date() - timedelta(days=period_days * 2)
    prev_end = start_date
    return build_dashboard_payload_range(company, sitec, start_date, now.date(), prev_start, prev_end, project_id=project_id)


def build_dashboard_payload_range(company, sitec, start_date, end_date, prev_start, prev_end, project_id=None):
    # Optimizar consultas con select_related/prefetch_related
    # Usar only() para reducir datos transferidos cuando solo necesitamos campos específicos
    projects_qs = Proyecto.objects.filter(company=company, sitec=sitec)
    if project_id:
        projects_qs = projects_qs.filter(id=project_id)
    projects = (
        projects_qs
        .select_related("company", "sitec")
        .only("id", "status", "end_date", "created_at")
    )
    
    reports_qs = ReporteSemanal.objects.filter(company=company, sitec=sitec)
    if project_id:
        reports_qs = reports_qs.filter(project_id=project_id)
    reports = (
        reports_qs
        .select_related("company", "sitec")
        .only("id", "week_start", "status", "created_at")
    )
    
    risks_qs = Riesgo.objects.filter(project__company=company, project__sitec=sitec)
    if project_id:
        risks_qs = risks_qs.filter(project_id=project_id)
    risks = (
        risks_qs
        .select_related("project")
        .only("id", "severity", "created_at")
    )

    reports_last = reports.filter(week_start__gte=start_date, week_start__lt=end_date).count()
    reports_prev = reports.filter(week_start__gte=prev_start, week_start__lt=prev_end).count()
    reports_submitted_last = reports.filter(
        week_start__gte=start_date, week_start__lt=end_date, status__in=["submitted", "approved"]
    ).count()
    reports_submitted_prev = reports.filter(
        week_start__gte=prev_start, week_start__lt=prev_end, status__in=["submitted", "approved"]
    ).count()
    reports_last_30d = reports.filter(week_start__gte=end_date - timedelta(days=30)).count()
    reports_prev_30d = reports.filter(
        week_start__gte=end_date - timedelta(days=60),
        week_start__lt=end_date - timedelta(days=30),
    ).count()

    projects_overdue = projects.filter(status__in=["planning", "in_progress"], end_date__lt=end_date).count()
    risks_high = risks.filter(severity__in=["high", "critical"]).count()
    projects_created_last = projects.filter(
        created_at__date__gte=start_date, created_at__date__lt=end_date
    ).count()
    projects_created_prev = projects.filter(
        created_at__date__gte=prev_start, created_at__date__lt=prev_end
    ).count()
    risks_high_last = risks.filter(
        severity__in=["high", "critical"],
        created_at__date__gte=start_date,
        created_at__date__lt=end_date,
    ).count()
    risks_high_prev = risks.filter(
        severity__in=["high", "critical"],
        created_at__date__gte=prev_start,
        created_at__date__lt=prev_end,
    ).count()
    reports_pending_approval = reports.filter(status="submitted").count()

    alerts = []
    if projects_overdue:
        alerts.append({"level": "warning", "message": f"Proyectos retrasados: {projects_overdue}"})
    if risks_high:
        alerts.append({"level": "warning", "message": f"Riesgos altos: {risks_high}"})
    if reports_pending_approval:
        alerts.append(
            {
                "level": "info",
                "message": f"Reportes pendientes de aprobacion: {reports_pending_approval}",
            }
        )

    # Calcular comparativos mes anterior
    month_start = date(end_date.year, end_date.month, 1)
    if end_date.month == 12:
        month_end = date(end_date.year + 1, 1, 1)
        prev_month_start = date(end_date.year, 11, 1)
        prev_month_end = month_start
    else:
        month_end = date(end_date.year, end_date.month + 1, 1)
        if end_date.month == 1:
            prev_month_start = date(end_date.year - 1, 12, 1)
            prev_month_end = month_start
        else:
            prev_month_start = date(end_date.year, end_date.month - 1, 1)
            prev_month_end = month_start
    
    reports_month = reports.filter(week_start__gte=month_start, week_start__lt=month_end).count()
    reports_prev_month = reports.filter(week_start__gte=prev_month_start, week_start__lt=prev_month_end).count()
    reports_submitted_month = reports.filter(
        week_start__gte=month_start, week_start__lt=month_end, status__in=["submitted", "approved"]
    ).count()
    reports_submitted_prev_month = reports.filter(
        week_start__gte=prev_month_start, week_start__lt=prev_month_end, status__in=["submitted", "approved"]
    ).count()
    projects_created_month = projects.filter(
        created_at__date__gte=month_start, created_at__date__lt=month_end
    ).count()
    projects_created_prev_month = projects.filter(
        created_at__date__gte=prev_month_start, created_at__date__lt=prev_month_end
    ).count()
    
    # Calcular comparativos año anterior
    year_start = date(end_date.year, 1, 1)
    year_end = date(end_date.year + 1, 1, 1)
    prev_year_start = date(end_date.year - 1, 1, 1)
    prev_year_end = year_start
    
    reports_year = reports.filter(week_start__gte=year_start, week_start__lt=year_end).count()
    reports_prev_year = reports.filter(week_start__gte=prev_year_start, week_start__lt=prev_year_end).count()
    reports_submitted_year = reports.filter(
        week_start__gte=year_start, week_start__lt=year_end, status__in=["submitted", "approved"]
    ).count()
    reports_submitted_prev_year = reports.filter(
        week_start__gte=prev_year_start, week_start__lt=prev_year_end, status__in=["submitted", "approved"]
    ).count()
    projects_created_year = projects.filter(
        created_at__date__gte=year_start, created_at__date__lt=year_end
    ).count()
    projects_created_prev_year = projects.filter(
        created_at__date__gte=prev_year_start, created_at__date__lt=prev_year_end
    ).count()

    return {
        "projects_total": projects.count(),
        "projects_in_progress": projects.filter(status="in_progress").count(),
        "projects_overdue": projects_overdue,
        "reports_last_7d": reports_last,
        "reports_submitted_last_7d": reports_submitted_last,
        "reports_last_period": reports_last,
        "reports_submitted_last_period": reports_submitted_last,
        "period_days": (end_date - start_date).days,
        "risks_high": risks_high,
        "projects_created_last_period": projects_created_last,
        "risks_high_last_period": risks_high_last,
        "comparatives": {
            # Comparativos período anterior (básico)
            "reports_last_period_delta": reports_last - reports_prev,
            "reports_last_period_pct": _pct_delta(reports_last, reports_prev),
            "reports_submitted_last_period_delta": reports_submitted_last - reports_submitted_prev,
            "reports_submitted_last_period_pct": _pct_delta(
                reports_submitted_last, reports_submitted_prev
            ),
            "projects_created_last_period_delta": projects_created_last - projects_created_prev,
            "projects_created_last_period_pct": _pct_delta(
                projects_created_last, projects_created_prev
            ),
            "risks_high_last_period_delta": risks_high_last - risks_high_prev,
            "risks_high_last_period_pct": _pct_delta(risks_high_last, risks_high_prev),
            # Comparativos 7 días
            "reports_last_7d_delta": reports_last - reports_prev,
            "reports_last_7d_pct": _pct_delta(reports_last, reports_prev),
            "reports_submitted_last_7d_delta": reports_submitted_last - reports_submitted_prev,
            "reports_submitted_last_7d_pct": _pct_delta(reports_submitted_last, reports_submitted_prev),
            # Comparativos 30 días
            "reports_last_30d_delta": reports_last_30d - reports_prev_30d,
            "reports_last_30d_pct": _pct_delta(reports_last_30d, reports_prev_30d),
            # Comparativos mes anterior
            "reports_month": reports_month,
            "reports_month_delta": reports_month - reports_prev_month,
            "reports_month_pct": _pct_delta(reports_month, reports_prev_month),
            "reports_submitted_month": reports_submitted_month,
            "reports_submitted_month_delta": reports_submitted_month - reports_submitted_prev_month,
            "reports_submitted_month_pct": _pct_delta(reports_submitted_month, reports_submitted_prev_month),
            "projects_created_month": projects_created_month,
            "projects_created_month_delta": projects_created_month - projects_created_prev_month,
            "projects_created_month_pct": _pct_delta(projects_created_month, projects_created_prev_month),
            # Comparativos año anterior
            "reports_year": reports_year,
            "reports_year_delta": reports_year - reports_prev_year,
            "reports_year_pct": _pct_delta(reports_year, reports_prev_year),
            "reports_submitted_year": reports_submitted_year,
            "reports_submitted_year_delta": reports_submitted_year - reports_submitted_prev_year,
            "reports_submitted_year_pct": _pct_delta(reports_submitted_year, reports_submitted_prev_year),
            "projects_created_year": projects_created_year,
            "projects_created_year_delta": projects_created_year - projects_created_prev_year,
            "projects_created_year_pct": _pct_delta(projects_created_year, projects_created_prev_year),
        },
        "alerts": alerts,
    }


def get_recent_snapshot(company, sitec, ttl_minutes=15):
    ttl = timezone.now() - timedelta(minutes=ttl_minutes)
    return (
        DashboardSnapshot.objects.filter(company=company, sitec=sitec, computed_at__gte=ttl)
        .order_by("-computed_at")
        .first()
    )


def create_snapshot(company, sitec, period_days=7, computed_at=None):
    computed_at = computed_at or timezone.now()
    computed_at = computed_at.replace(second=0, microsecond=0)
    payload = build_dashboard_payload(company, sitec, period_days=period_days)
    snapshot, _ = DashboardSnapshot.objects.update_or_create(
        company=company,
        sitec=sitec,
        period_days=period_days,
        computed_at=computed_at,
        defaults={"payload": payload},
    )
    return snapshot


def _month_range(anchor):
    start = date(anchor.year, anchor.month, 1)
    if anchor.month == 12:
        end = date(anchor.year + 1, 1, 1)
    else:
        end = date(anchor.year, anchor.month + 1, 1)
    return start, end


def create_monthly_aggregate(company, sitec, anchor_date=None):
    anchor_date = anchor_date or timezone.now().date()
    start, end = _month_range(anchor_date)
    prev_start, prev_end = _month_range(start - timedelta(days=1))
    payload = build_dashboard_payload_range(company, sitec, start, end, prev_start, prev_end)
    aggregate, _ = DashboardAggregate.objects.update_or_create(
        company=company,
        sitec=sitec,
        period_label="month",
        period_start=start,
        defaults={
            "period_end": end,
            "payload": payload,
            "computed_at": timezone.now(),
        },
    )
    return aggregate


def get_recent_aggregates(company, sitec, period_label="month", limit=12):
    return (
        DashboardAggregate.objects.filter(company=company, sitec=sitec, period_label=period_label)
        .select_related("company", "sitec")
        .order_by("-period_start")[:limit]
    )


def build_trends_data(company, sitec, periods=12, period_type="month"):
    """
    Construye datos de tendencias para los últimos N períodos
    period_type: 'month' o 'week'
    """
    if period_type == "month":
        aggregates = get_recent_aggregates(company, sitec, period_label="month", limit=periods)
        trends = []
        for agg in reversed(aggregates):  # Orden cronológico
            payload = agg.payload or {}
            comparatives = payload.get("comparatives", {})
            trends.append({
                "period_start": agg.period_start,
                "period_end": agg.period_end,
                "reports": payload.get("reports_last_period", 0),
                "reports_submitted": payload.get("reports_submitted_last_period", 0),
                "projects_created": payload.get("projects_created_last_period", 0),
                "risks_high": payload.get("risks_high_last_period", 0),
                "delta_pct": comparatives.get("reports_last_period_pct"),
            })
        return trends
    else:
        # Para semanas, usar snapshots
        from datetime import timedelta
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=periods * 7)
        snapshots = (
            DashboardSnapshot.objects.filter(
                company=company, sitec=sitec, period_days=7, computed_at__date__gte=start_date
            )
            .select_related("company", "sitec")
            .order_by("computed_at")[:periods]
        )
        trends = []
        for snapshot in snapshots:
            payload = snapshot.payload or {}
            comparatives = payload.get("comparatives", {})
            trends.append({
                "computed_at": snapshot.computed_at,
                "reports": payload.get("reports_last_7d", 0),
                "reports_submitted": payload.get("reports_submitted_last_7d", 0),
                "delta_pct": comparatives.get("reports_last_7d_pct"),
            })
        return trends
