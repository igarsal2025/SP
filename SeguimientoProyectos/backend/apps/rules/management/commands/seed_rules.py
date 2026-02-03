from django.core.management.base import BaseCommand

from apps.companies.models import Company, Sitec
from apps.rules.models import RuleItem, RuleSet


class Command(BaseCommand):
    help = "Seed reglas base (NOM/negocio) para el wizard."

    def handle(self, *args, **options):
        company = Company.objects.first()
        sitec = Sitec.objects.first()
        if not company or not sitec:
            self.stdout.write(self.style.WARNING("No existe Company/Sitec para seed_rules."))
            return

        ruleset, created = RuleSet.objects.get_or_create(
            company=company,
            sitec=sitec,
            scope="wizard",
            version=1,
            defaults={"name": "Reglas Wizard v1", "is_active": True},
        )
        if not created:
            self.stdout.write(self.style.WARNING("Ruleset ya existe, no se recrea."))
            return

        RuleItem.objects.bulk_create(
            [
                RuleItem(
                    ruleset=ruleset,
                    code="nom_progress_pct_range",
                    field="progress_pct",
                    severity="critical",
                    message="Porcentaje de avance debe estar entre 0 y 100.",
                    step=2,
                    condition={"field": "progress_pct", "op": "lt", "value": 0},
                ),
                RuleItem(
                    ruleset=ruleset,
                    code="nom_cabling_nodes_required",
                    field="cabling_nodes_total",
                    severity="critical",
                    message="Total de nodos cableados es obligatorio.",
                    step=3,
                    condition={"field": "cabling_nodes_total", "op": "required"},
                ),
                RuleItem(
                    ruleset=ruleset,
                    code="biz_security_devices_required",
                    field="security_devices",
                    severity="critical",
                    message="Dispositivos de seguridad es obligatorio.",
                    step=5,
                    condition={"field": "security_devices", "op": "required"},
                ),
                RuleItem(
                    ruleset=ruleset,
                    code="biz_incidents_detail_required",
                    field="incidents_detail",
                    severity="warning",
                    message="Detalle de incidentes recomendado cuando hay incidentes.",
                    step=10,
                    condition={"field": "incidents", "op": "eq", "value": "true"},
                ),
            ]
        )

        self.stdout.write(self.style.SUCCESS("Reglas base creadas correctamente."))
