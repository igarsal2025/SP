from celery import shared_task

from .models import Document
from .services import generate_report_pdf


@shared_task
def generate_report_document(document_id):
    document = Document.objects.select_related("report").filter(id=document_id).first()
    if not document:
        return None
    try:
        generate_report_pdf(document)
        return str(document.id)
    except Exception:
        document.status = "failed"
        document.save(update_fields=["status", "updated_at"])
        raise
