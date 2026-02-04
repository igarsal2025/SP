from celery import shared_task
from django.conf import settings
from django.utils import timezone

from apps.companies.models import Sitec

from .services import create_snapshot


@shared_task
def refresh_roi_snapshots(period_days=None):
    active_sitecs = Sitec.objects.filter(status="active", company__status="active")
    periods = period_days if isinstance(period_days, list) else None
    if period_days is None:
        periods = getattr(settings, "ROI_SNAPSHOT_PERIOD_DAYS", [30])
    if isinstance(period_days, int):
        periods = [period_days]
    computed_at = timezone.now()
    count = 0
    for sitec in active_sitecs:
        for period in periods:
            create_snapshot(sitec.company, sitec, period_days=period, computed_at=computed_at)
            count += 1
    return {"snapshots": count, "period_days": periods}
