import time

from celery import shared_task

from apps.audit.services import log_audit_event

from .models import AiSuggestion
from .providers import HeavyProvider
from .pipeline import run_training_pipeline


@shared_task
def run_heavy_suggestion(suggestion_id):
    start = time.perf_counter()
    suggestion = AiSuggestion.objects.filter(id=suggestion_id).first()
    if not suggestion:
        return None

    provider = HeavyProvider()
    suggestions = provider.suggest(suggestion.step or 1, suggestion.input_snapshot or {})
    output = {
        "status": "success",
        "fallback": False,
        "model": {"name": provider.name, "version": provider.version},
        "latency_ms": None,
        "suggestions": suggestions,
    }

    latency_ms = int((time.perf_counter() - start) * 1000)
    output["latency_ms"] = latency_ms

    suggestion.output = output
    suggestion.confidence = suggestion.confidence or None
    suggestion.latency_ms = latency_ms
    suggestion.status = "success"
    suggestion.save(update_fields=["output", "confidence", "latency_ms", "status"])

    log_audit_event(
        None,
        "ai_suggest_heavy_completed",
        suggestion,
        extra_data={"suggestion_id": str(suggestion.id)},
    )
    return output


@shared_task
def run_ai_training(company_id, sitec_id, created_by_id=None, since_days=180, limit=5000):
    from apps.companies.models import Company, Sitec
    from django.contrib.auth import get_user_model

    company = Company.objects.filter(id=company_id).first()
    sitec = Sitec.objects.filter(id=sitec_id).first()
    if not company or not sitec:
        return None
    user = None
    if created_by_id:
        user = get_user_model().objects.filter(id=created_by_id).first()
    job = run_training_pipeline(company, sitec, created_by=user, since_days=since_days, limit=limit)
    return str(job.id)
