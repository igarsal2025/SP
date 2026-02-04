from django.core.management.base import BaseCommand

from apps.ai.pipeline import run_training_pipeline
from apps.companies.models import Company, Sitec


class Command(BaseCommand):
    help = "Ejecuta pipeline IA real (dataset + envio opcional)."

    def add_arguments(self, parser):
        parser.add_argument("--company", required=False, help="UUID de company")
        parser.add_argument("--sitec", required=False, help="UUID de sitec")
        parser.add_argument("--since-days", type=int, default=180)
        parser.add_argument("--limit", type=int, default=5000)

    def handle(self, *args, **options):
        company_id = options.get("company")
        sitec_id = options.get("sitec")
        since_days = options.get("since_days")
        limit = options.get("limit")

        company = Company.objects.filter(id=company_id).first() if company_id else Company.objects.first()
        if not company:
            self.stdout.write(self.style.ERROR("Company no encontrada."))
            return
        sitec = (
            Sitec.objects.filter(id=sitec_id).first()
            if sitec_id
            else Sitec.objects.filter(company=company).first()
        )
        if not sitec:
            self.stdout.write(self.style.ERROR("Sitec no encontrado."))
            return

        job = run_training_pipeline(company, sitec, created_by=None, since_days=since_days, limit=limit)
        self.stdout.write(self.style.SUCCESS(f"Pipeline IA ejecutado: {job.id} ({job.status})"))
