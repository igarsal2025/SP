import hashlib
import json
import logging
import os
import ssl
import time
from pathlib import Path
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError

from django.conf import settings
from django.utils import timezone

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.graphics import renderPDF
    from reportlab.graphics.barcode import qr
except ImportError:  # pragma: no cover - handled by runtime dependency
    canvas = None
    A4 = None
    cm = None
    renderPDF = None
    qr = None


def ensure_storage_dir():
    storage_root = Path(settings.BASE_DIR) / "storage" / "documents"
    storage_root.mkdir(parents=True, exist_ok=True)
    return storage_root


def build_document_path(document):
    storage_root = ensure_storage_dir()
    folder = storage_root / str(document.report_id)
    folder.mkdir(parents=True, exist_ok=True)
    filename = f"reporte_semanal_v{document.version}.pdf"
    return folder / filename


def compute_sha256(file_path):
    digest = hashlib.sha256()
    with open(file_path, "rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def render_qr(canvas_obj, token, x, y, size):
    if not qr or not renderPDF:
        return
    widget = qr.QrCodeWidget(str(token))
    bounds = widget.getBounds()
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    drawing = renderPDF.Drawing(size, size, transform=[size / width, 0, 0, size / height, 0, 0])
    drawing.add(widget)
    renderPDF.draw(drawing, canvas_obj, x, y)


def get_client_signature(report):
    if report.metadata and report.metadata.get("signature_client"):
        return report.metadata.get("signature_client")
    data = report.wizard_data or {}
    steps = data.get("steps", {}) if isinstance(data, dict) else {}
    step_11 = steps.get("11") or steps.get(11) or {}
    if isinstance(step_11, dict):
        return step_11.get("signature_client")
    return None


def _render_report_pdf(document, file_path, nom151_stamp):
    report = document.report
    pdf = canvas.Canvas(str(file_path), pagesize=A4)
    width, height = A4
    padding = 2 * cm

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(padding, height - padding, "Reporte Semanal SITEC")

    pdf.setFont("Helvetica", 10)
    pdf.drawString(padding, height - padding - 20, f"Proyecto: {report.project_name}")
    pdf.drawString(padding, height - padding - 35, f"Semana inicio: {report.week_start}")
    pdf.drawString(padding, height - padding - 50, f"Avance: {report.progress_pct}%")
    pdf.drawString(padding, height - padding - 65, f"Estatus: {report.status}")
    pdf.drawString(padding, height - padding - 80, f"Técnico: {getattr(report.technician, 'username', '')}")

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(padding, height - padding - 110, "Firmas")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(padding, height - padding - 130, f"Firma técnico: {bool(report.signature_tech)}")
    pdf.drawString(padding, height - padding - 145, f"Firma supervisor: {bool(report.signature_supervisor)}")
    client_signature = get_client_signature(report)
    pdf.drawString(padding, height - padding - 160, f"Firma cliente: {bool(client_signature)}")

    pdf.setFont("Helvetica", 8)
    pdf.drawString(
        padding,
        padding + 40,
        f"QR verificación: {document.qr_token}",
    )
    render_qr(pdf, document.qr_token, width - padding - 80, padding + 10, 70)

    pdf.setFont("Helvetica", 8)
    stamp_text = nom151_stamp or "pendiente"
    pdf.drawString(padding, padding + 20, f"Sello NOM-151: {stamp_text}")

    pdf.showPage()
    pdf.save()


def generate_report_pdf(document):
    if not canvas:
        raise RuntimeError("ReportLab no está disponible.")

    file_path = build_document_path(document)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    document.file_path = str(file_path)
    document.file_name = os.path.basename(file_path)
    document.issued_at = timezone.now()

    _render_report_pdf(document, file_path, nom151_stamp="pendiente")
    file_size = os.path.getsize(file_path)
    checksum = compute_sha256(file_path)

    document.file_size = file_size
    document.checksum_sha256 = checksum
    if document.nom151_stamp:
        nom151_stamp = document.nom151_stamp
        nom151_metrics = {"latency_ms": 0, "attempts": 0, "success": True, "status": "cached"}
    else:
        nom151_stamp, nom151_metrics = request_nom151_stamp(document, checksum)
    if nom151_metrics:
        metadata = document.metadata or {}
        metadata["nom151"] = {**metadata.get("nom151", {}), **nom151_metrics}
        document.metadata = metadata

    if nom151_stamp and nom151_stamp != "pendiente":
        _render_report_pdf(document, file_path, nom151_stamp=nom151_stamp)
        file_size = os.path.getsize(file_path)
        checksum = compute_sha256(file_path)

    document.file_size = file_size
    document.checksum_sha256 = checksum
    document.nom151_stamp = nom151_stamp
    document.status = "ready"
    document.save(
        update_fields=[
            "file_path",
            "file_name",
            "file_size",
            "checksum_sha256",
            "issued_at",
            "nom151_stamp",
            "metadata",
            "status",
            "updated_at",
        ]
    )

    return document


def _parse_nom151_response(body):
    payload = json.loads(body) if body else {}
    stamp = payload.get("nom151_stamp") or payload.get("stamp") or payload.get("folio")
    if not stamp:
        logging.getLogger(__name__).warning("NOM151 response missing stamp: %s", payload)
    return stamp or "pendiente"


def _encode_multipart(fields, files):
    boundary = f"----sitec-nom151-{int(time.time() * 1000)}"
    lines = []
    for key, value in fields.items():
        lines.extend(
            [
                f"--{boundary}",
                f'Content-Disposition: form-data; name="{key}"',
                "",
                str(value),
            ]
        )
    for key, file_info in files.items():
        filename, content_type, content = file_info
        lines.extend(
            [
                f"--{boundary}",
                f'Content-Disposition: form-data; name="{key}"; filename="{filename}"',
                f"Content-Type: {content_type}",
                "",
            ]
        )
        lines.append(content)
    lines.append(f"--{boundary}--")
    body = b""
    for line in lines:
        if isinstance(line, bytes):
            body += line + b"\r\n"
        else:
            body += f"{line}\r\n".encode("utf-8")
    content_type = f"multipart/form-data; boundary={boundary}"
    return body, content_type


def request_nom151_stamp(document, checksum_sha256):
    provider_url = getattr(settings, "NOM151_PROVIDER_URL", "")
    api_key = getattr(settings, "NOM151_API_KEY", "")
    timeout = getattr(settings, "NOM151_TIMEOUT", 15)
    verify_ssl = getattr(settings, "NOM151_VERIFY_SSL", True)
    max_retries = getattr(settings, "NOM151_RETRIES", 1)
    backoff_base = getattr(settings, "NOM151_BACKOFF_BASE", 0.5)
    provider_mode = getattr(settings, "NOM151_PROVIDER_MODE", "json")
    send_pdf = getattr(settings, "NOM151_SEND_PDF", False)
    if not provider_url:
        return "pendiente", {"latency_ms": 0, "attempts": 0, "success": False, "status": "disabled"}

    payload = {
        "document_id": str(document.id),
        "report_id": str(document.report_id),
        "file_name": document.file_name,
        "file_size": document.file_size,
        "checksum_sha256": checksum_sha256,
        "issued_at": document.issued_at.isoformat() if document.issued_at else None,
    }
    headers = {}
    if provider_mode == "multipart":
        files = {}
        if send_pdf and document.file_path and os.path.exists(document.file_path):
            with open(document.file_path, "rb") as handle:
                files["file"] = (
                    document.file_name or "document.pdf",
                    "application/pdf",
                    handle.read(),
                )
        data, content_type = _encode_multipart(payload, files)
        headers["Content-Type"] = content_type
    else:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    ssl_context = ssl.create_default_context() if verify_ssl else ssl._create_unverified_context()
    req = urlrequest.Request(provider_url, data=data, headers=headers, method="POST")
    attempts = max(0, int(max_retries))
    start = time.monotonic()
    last_error = None
    for attempt in range(attempts + 1):
        try:
            with urlrequest.urlopen(req, timeout=timeout, context=ssl_context) as response:
                body = response.read().decode("utf-8")
                stamp = _parse_nom151_response(body)
                latency_ms = int((time.monotonic() - start) * 1000)
                return stamp, {
                    "latency_ms": latency_ms,
                    "attempts": attempt + 1,
                    "success": stamp != "pendiente",
                    "status": "ok" if stamp != "pendiente" else "empty",
                }
        except (HTTPError, URLError, ValueError) as exc:
            logging.getLogger(__name__).warning("NOM151 provider error: %s", exc)
            last_error = str(exc)
            if attempt >= attempts:
                latency_ms = int((time.monotonic() - start) * 1000)
                return "pendiente", {
                    "latency_ms": latency_ms,
                    "attempts": attempt + 1,
                    "success": False,
                    "status": "error",
                    "error": last_error,
                }
            time.sleep(backoff_base * (2 ** attempt))
