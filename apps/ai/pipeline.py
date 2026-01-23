import base64
import hashlib
import json
import os
import ssl
import time
from datetime import timedelta
from pathlib import Path
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError

from django.conf import settings
from django.utils import timezone

from apps.reports.models import ReporteSemanal

from .models import AiTrainingJob


def _ensure_dataset_dir(company_id):
    storage_root = Path(settings.BASE_DIR) / "storage" / "ai" / "datasets" / str(company_id)
    storage_root.mkdir(parents=True, exist_ok=True)
    return storage_root


def _compute_sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_training_dataset(company, sitec, since_days=180, limit=5000):
    start_date = timezone.now() - timedelta(days=since_days)
    reports = (
        ReporteSemanal.objects.filter(company=company, sitec=sitec, created_at__gte=start_date)
        .order_by("-created_at")[:limit]
    )
    rows = []
    for report in reports:
        payload = report.wizard_data or {}
        rows.append(
            {
                "input": payload,
                "output": {
                    "status": report.status,
                    "progress_pct": report.progress_pct,
                    "incidents": report.incidents,
                    "incidents_severity": report.incidents_severity,
                    "submitted_at": report.submitted_at.isoformat() if report.submitted_at else None,
                    "approved_at": report.approved_at.isoformat() if report.approved_at else None,
                },
                "meta": {
                    "report_id": str(report.id),
                    "project_id": str(report.project_id) if report.project_id else None,
                    "created_at": report.created_at.isoformat(),
                    "schema_version": report.wizard_schema_version,
                },
            }
        )
    return rows


def export_dataset_to_jsonl(company, sitec, rows):
    dataset_dir = _ensure_dataset_dir(company.id)
    filename = f"dataset_{sitec.schema_name}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
    file_path = dataset_dir / filename
    with file_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")
    return file_path


def submit_training_job(job, dataset_path):
    provider_url = getattr(settings, "AI_TRAIN_PROVIDER_URL", "")
    api_key = getattr(settings, "AI_TRAIN_API_KEY", "")
    timeout = getattr(settings, "AI_TRAIN_TIMEOUT", 20)
    verify_ssl = getattr(settings, "AI_TRAIN_VERIFY_SSL", True)
    max_retries = getattr(settings, "AI_TRAIN_RETRIES", 1)
    backoff_base = getattr(settings, "AI_TRAIN_BACKOFF_BASE", 0.5)
    send_file = getattr(settings, "AI_TRAIN_SEND_FILE", False)

    if not provider_url:
        # Proveedor ML no configurado - el sistema funciona con proveedores locales
        import logging
        logging.getLogger(__name__).info(
            f"AI training provider no configurado para job {job.id} - "
            "el sistema funciona con proveedores locales (RuleProvider, LightModelProvider)"
        )
        job.status = "dataset_ready"
        job.provider_name = "disabled"
        job.metadata = {
            **(job.metadata or {}),
            "message": "Proveedor ML externo no configurado. El sistema funciona con proveedores locales.",
            "local_providers": ["RuleProvider", "LightModelProvider", "HeavyProvider"]
        }
        job.save(update_fields=["status", "provider_name", "metadata", "updated_at"])
        return job

    payload = {
        "job_id": str(job.id),
        "company_id": str(job.company_id),
        "sitec_id": str(job.sitec_id),
        "dataset_path": str(dataset_path),
        "dataset_size": job.dataset_size,
        "dataset_checksum": job.dataset_checksum,
    }

    if send_file:
        with open(dataset_path, "rb") as handle:
            payload["dataset_base64"] = base64.b64encode(handle.read()).decode("ascii")
        payload["dataset_filename"] = os.path.basename(dataset_path)

    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    ssl_context = ssl.create_default_context() if verify_ssl else ssl._create_unverified_context()
    req = urlrequest.Request(provider_url, data=data, headers=headers, method="POST")
    start = time.monotonic()
    last_error = None
    for attempt in range(max(0, int(max_retries)) + 1):
        try:
            with urlrequest.urlopen(req, timeout=timeout, context=ssl_context) as response:
                body = response.read().decode("utf-8")
                payload = json.loads(body) if body else {}
                job_id = payload.get("job_id") or payload.get("id")
                job.status = "submitted"
                job.provider_name = payload.get("provider", "external")
                job.provider_job_id = job_id or ""
                job.metadata = {
                    **(job.metadata or {}),
                    "provider_response": payload,
                    "latency_ms": int((time.monotonic() - start) * 1000),
                    "attempts": attempt + 1,
                }
                job.save(
                    update_fields=[
                        "status",
                        "provider_name",
                        "provider_job_id",
                        "metadata",
                        "updated_at",
                    ]
                )
                return job
        except (HTTPError, URLError, ValueError) as exc:
            last_error = str(exc)
            if attempt >= max(0, int(max_retries)):
                job.status = "failed"
                job.metadata = {
                    **(job.metadata or {}),
                    "error": last_error,
                    "latency_ms": int((time.monotonic() - start) * 1000),
                    "attempts": attempt + 1,
                }
                job.save(update_fields=["status", "metadata", "updated_at"])
                return job
            time.sleep(backoff_base * (2**attempt))


def run_training_pipeline(company, sitec, created_by=None, since_days=180, limit=5000):
    rows = build_training_dataset(company, sitec, since_days=since_days, limit=limit)
    dataset_path = export_dataset_to_jsonl(company, sitec, rows)
    job = AiTrainingJob.objects.create(
        company=company,
        sitec=sitec,
        created_by=created_by,
        status="pending",
        dataset_path=str(dataset_path),
        dataset_size=os.path.getsize(dataset_path),
        dataset_checksum=_compute_sha256(dataset_path),
        metadata={
            "rows": len(rows),
            "since_days": since_days,
            "limit": limit,
        },
    )
    job.status = "dataset_ready"
    job.save(update_fields=["status", "updated_at"])
    return submit_training_job(job, dataset_path)
