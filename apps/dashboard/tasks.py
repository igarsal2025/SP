from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from apps.companies.models import Sitec

from .services import create_monthly_aggregate, create_snapshot


@shared_task
def refresh_dashboard_snapshots(period_days=None):
    active_sitecs = Sitec.objects.filter(status="active", company__status="active")
    computed_at = timezone.now()
    periods = period_days if isinstance(period_days, list) else None
    if period_days is None:
        periods = getattr(settings, "DASHBOARD_SNAPSHOT_PERIOD_DAYS", [7])
    if isinstance(period_days, int):
        periods = [period_days]
    count = 0
    for sitec in active_sitecs:
        for period in periods:
            create_snapshot(sitec.company, sitec, period_days=period, computed_at=computed_at)
            count += 1
    return {"snapshots": count, "period_days": periods}


@shared_task
def refresh_dashboard_aggregates(months=None):
    active_sitecs = Sitec.objects.filter(status="active", company__status="active")
    total = 0
    months_back = months or int(getattr(settings, "DASHBOARD_AGGREGATE_MONTHS", 12))
    today = timezone.now().date()
    for sitec in active_sitecs:
        for offset in range(months_back):
            year = today.year
            month = today.month - offset
            while month <= 0:
                month += 12
                year -= 1
            anchor = today.replace(year=year, month=month, day=1)
            create_monthly_aggregate(sitec.company, sitec, anchor_date=anchor)
            total += 1
    return {"aggregates": total, "months": months_back}
