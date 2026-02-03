from django.core.management.base import BaseCommand

from apps.accounts.models import AccessPolicy
from apps.companies.models import Company, Sitec


class Command(BaseCommand):
    help = "Crea los registros base de SITEC (Company y Sitec)."

    def handle(self, *args, **options):
        company, created_company = Company.objects.get_or_create(
            name="SITEC",
            defaults={
                "rfc": "",
                "tax_regime": "",
                "timezone": "America/Mexico_City",
                "locale": "es-MX",
                "plan": "enterprise",
                "status": "active",
            },
        )

        sitec, created_sitec = Sitec.objects.get_or_create(
            company=company,
            schema_name="sitec",
            defaults={"status": "active"},
        )

        policy, created_policy = AccessPolicy.objects.get_or_create(
            company=company,
            action="*",
            defaults={
                "conditions": {},
                "effect": "allow",
                "priority": 0,
                "is_active": True,
            },
        )

        signature_policies = [
            {
                "action": "wizard.signature.require.tech",
                "conditions": {"role": "tecnico"},
                "effect": "allow",
                "priority": 10,
            },
            {
                "action": "wizard.signature.require.supervisor",
                "conditions": {"role": "supervisor"},
                "effect": "allow",
                "priority": 10,
            },
            {
                "action": "wizard.signature.require.client",
                "conditions": {"role": "cliente"},
                "effect": "allow",
                "priority": 10,
            },
            {
                "action": "wizard.signature.require.supervisor",
                "conditions": {"role": "pm"},
                "effect": "allow",
                "priority": 10,
            },
            {
                "action": "wizard.signature.require.supervisor",
                "conditions": {"role": "admin_empresa"},
                "effect": "allow",
                "priority": 10,
            },
            {
                "action": "wizard.signature.require.supervisor",
                "conditions": {"signature_supervisor_required": "true"},
                "effect": "allow",
                "priority": 20,
            },
            {
                "action": "wizard.signature.require.client",
                "conditions": {"incidents": "true"},
                "effect": "allow",
                "priority": 20,
            },
        ]
        policy_catalog = [
            {"action": "wizard.*", "conditions": {"role": "tecnico"}, "priority": 5},
            {"action": "wizard.*", "conditions": {"role": "supervisor"}, "priority": 5},
            {"action": "wizard.*", "conditions": {"role": "pm"}, "priority": 5},
            {"action": "wizard.*", "conditions": {"role": "admin_empresa"}, "priority": 5},
            {"action": "wizard.*", "conditions": {"role": "cliente", "method": "get"}, "priority": 5},
            {"action": "reports.*", "conditions": {"role": "tecnico"}, "priority": 5},
            {"action": "reports.*", "conditions": {"role": "supervisor"}, "priority": 5},
            {"action": "reports.*", "conditions": {"role": "pm"}, "priority": 5},
            {"action": "reports.*", "conditions": {"role": "admin_empresa"}, "priority": 5},
            {"action": "reports.*", "conditions": {"role": "cliente", "method": "get"}, "priority": 5},
            {"action": "projects.*", "conditions": {"role": "tecnico", "method": "get"}, "priority": 5},
            {"action": "projects.*", "conditions": {"role": "supervisor"}, "priority": 5},
            {"action": "projects.*", "conditions": {"role": "pm"}, "priority": 5},
            {"action": "projects.*", "conditions": {"role": "admin_empresa"}, "priority": 5},
            {"action": "documents.*", "conditions": {"role": "tecnico"}, "priority": 5},
            {"action": "documents.*", "conditions": {"role": "supervisor"}, "priority": 5},
            {"action": "documents.*", "conditions": {"role": "pm"}, "priority": 5},
            {"action": "documents.*", "conditions": {"role": "admin_empresa"}, "priority": 5},
            {"action": "dashboard.*", "conditions": {"role": "pm"}, "priority": 5},
            {"action": "dashboard.*", "conditions": {"role": "admin_empresa"}, "priority": 5},
            {"action": "roi.*", "conditions": {"role": "pm"}, "priority": 5},
            {"action": "roi.*", "conditions": {"role": "admin_empresa"}, "priority": 5},
            {"action": "sync.*", "conditions": {"role": "tecnico"}, "priority": 5},
            {"action": "sync.*", "conditions": {"role": "supervisor"}, "priority": 5},
            {"action": "sync.*", "conditions": {"role": "pm"}, "priority": 5},
            {"action": "sync.*", "conditions": {"role": "admin_empresa"}, "priority": 5},
            {"action": "ai.*", "conditions": {"role": "tecnico"}, "priority": 5},
            {"action": "ai.*", "conditions": {"role": "supervisor"}, "priority": 5},
            {"action": "ai.*", "conditions": {"role": "pm"}, "priority": 5},
            {"action": "ai.*", "conditions": {"role": "admin_empresa"}, "priority": 5},
        ]
        created_signatures = 0
        for policy_data in signature_policies:
            _, created_sig = AccessPolicy.objects.get_or_create(
                company=company,
                action=policy_data["action"],
                conditions=policy_data["conditions"],
                defaults={
                    "effect": policy_data["effect"],
                    "priority": policy_data["priority"],
                    "is_active": True,
                },
            )
            if created_sig:
                created_signatures += 1
        created_catalog = 0
        for policy_data in policy_catalog:
            _, created_cat = AccessPolicy.objects.get_or_create(
                company=company,
                action=policy_data["action"],
                conditions=policy_data["conditions"],
                defaults={
                    "effect": "allow",
                    "priority": policy_data["priority"],
                    "is_active": True,
                },
            )
            if created_cat:
                created_catalog += 1

        if created_company:
            self.stdout.write(self.style.SUCCESS("Company SITEC creada."))
        else:
            self.stdout.write("Company SITEC ya existe.")

        if created_sitec:
            self.stdout.write(self.style.SUCCESS("Sitec activo creado."))
        else:
            self.stdout.write("Sitec activo ya existe.")

        if created_policy:
            self.stdout.write(self.style.SUCCESS("Politica default creada (allow *)."))
        else:
            self.stdout.write("Politica default ya existe.")

        if created_signatures:
            self.stdout.write(
                self.style.SUCCESS(f"Politicas de firma por rol creadas: {created_signatures}.")
            )
        else:
            self.stdout.write("Politicas de firma por rol ya existen.")
        if created_catalog:
            self.stdout.write(
                self.style.SUCCESS(f"Catalogo ABAC creado: {created_catalog}.")
            )
        else:
            self.stdout.write("Catalogo ABAC ya existe.")
