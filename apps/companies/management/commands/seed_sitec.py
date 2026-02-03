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
            # Wizard - Acceso general
            {"action": "wizard.*", "conditions": {"role": "tecnico"}, "priority": 5},
            {"action": "wizard.*", "conditions": {"role": "supervisor"}, "priority": 5},
            {"action": "wizard.*", "conditions": {"role": "pm"}, "priority": 5},
            {"action": "wizard.*", "conditions": {"role": "admin_empresa"}, "priority": 5},
            {"action": "wizard.*", "conditions": {"role": "cliente", "method": "get"}, "priority": 5},
            # Wizard - Acciones específicas
            {"action": "wizard.save", "conditions": {"role": "tecnico"}, "priority": 6},
            {"action": "wizard.save", "conditions": {"role": "supervisor"}, "priority": 6},
            {"action": "wizard.save", "conditions": {"role": "pm"}, "priority": 6},
            {"action": "wizard.save", "conditions": {"role": "admin_empresa"}, "priority": 6},
            {"action": "wizard.submit", "conditions": {"role": "supervisor"}, "priority": 6},
            {"action": "wizard.submit", "conditions": {"role": "pm"}, "priority": 6},
            {"action": "wizard.submit", "conditions": {"role": "admin_empresa"}, "priority": 6},
            # Wizard - Pasos específicos (firmas y aprobaciones)
            {"action": "wizard.step.11.view", "conditions": {"role": "tecnico"}, "priority": 7},
            {"action": "wizard.step.11.view", "conditions": {"role": "supervisor"}, "priority": 7},
            {"action": "wizard.step.11.view", "conditions": {"role": "pm"}, "priority": 7},
            {"action": "wizard.step.11.view", "conditions": {"role": "admin_empresa"}, "priority": 7},
            {"action": "wizard.step.11.view", "conditions": {"role": "cliente"}, "priority": 7},
            {"action": "wizard.step.12.view", "conditions": {"role": "supervisor"}, "priority": 7},
            {"action": "wizard.step.12.view", "conditions": {"role": "pm"}, "priority": 7},
            {"action": "wizard.step.12.view", "conditions": {"role": "admin_empresa"}, "priority": 7},
            # Dashboard y componentes avanzados
            {"action": "dashboard.view", "conditions": {"role": "pm"}, "priority": 5},
            {"action": "dashboard.view", "conditions": {"role": "admin_empresa"}, "priority": 5},
            {"action": "dashboard.view", "conditions": {"role": "supervisor"}, "priority": 5},
            {"action": "dashboard.trends.view", "conditions": {"role": "pm"}, "priority": 6},
            {"action": "dashboard.trends.view", "conditions": {"role": "admin_empresa"}, "priority": 6},
            {"action": "dashboard.trends.view", "conditions": {"role": "supervisor"}, "priority": 6},
            {"action": "dashboard.export", "conditions": {"role": "pm"}, "priority": 6},
            {"action": "dashboard.export", "conditions": {"role": "admin_empresa"}, "priority": 6},
            # IA y sugerencias
            {"action": "ai.suggest", "conditions": {"role": "tecnico"}, "priority": 5},
            {"action": "ai.suggest", "conditions": {"role": "supervisor"}, "priority": 5},
            {"action": "ai.suggest", "conditions": {"role": "pm"}, "priority": 5},
            {"action": "ai.suggest", "conditions": {"role": "admin_empresa"}, "priority": 5},
            {"action": "ai.stats.view", "conditions": {"role": "pm"}, "priority": 6},
            {"action": "ai.stats.view", "conditions": {"role": "admin_empresa"}, "priority": 6},
            # Documentos
            {"action": "documents.generate", "conditions": {"role": "tecnico"}, "priority": 5},
            {"action": "documents.generate", "conditions": {"role": "supervisor"}, "priority": 5},
            {"action": "documents.generate", "conditions": {"role": "pm"}, "priority": 5},
            {"action": "documents.generate", "conditions": {"role": "admin_empresa"}, "priority": 5},
            {"action": "documents.download", "conditions": {"role": "tecnico"}, "priority": 5},
            {"action": "documents.download", "conditions": {"role": "supervisor"}, "priority": 5},
            {"action": "documents.download", "conditions": {"role": "pm"}, "priority": 5},
            {"action": "documents.download", "conditions": {"role": "admin_empresa"}, "priority": 5},
            {"action": "documents.download", "conditions": {"role": "cliente"}, "priority": 5},
            # Reportes
            {"action": "reports.*", "conditions": {"role": "tecnico"}, "priority": 5},
            {"action": "reports.*", "conditions": {"role": "supervisor"}, "priority": 5},
            {"action": "reports.*", "conditions": {"role": "pm"}, "priority": 5},
            {"action": "reports.*", "conditions": {"role": "admin_empresa"}, "priority": 5},
            {"action": "reports.*", "conditions": {"role": "cliente", "method": "get"}, "priority": 5},
            {"action": "reports.approve", "conditions": {"role": "supervisor"}, "priority": 6},
            {"action": "reports.approve", "conditions": {"role": "pm"}, "priority": 6},
            {"action": "reports.approve", "conditions": {"role": "admin_empresa"}, "priority": 6},
            # Proyectos
            {"action": "projects.*", "conditions": {"role": "tecnico", "method": "get"}, "priority": 5},
            {"action": "projects.*", "conditions": {"role": "supervisor"}, "priority": 5},
            {"action": "projects.*", "conditions": {"role": "pm"}, "priority": 5},
            {"action": "projects.*", "conditions": {"role": "admin_empresa"}, "priority": 5},
            {"action": "projects.create", "conditions": {"role": "supervisor"}, "priority": 6},
            {"action": "projects.create", "conditions": {"role": "pm"}, "priority": 6},
            {"action": "projects.create", "conditions": {"role": "admin_empresa"}, "priority": 6},
            {"action": "projects.edit", "conditions": {"role": "supervisor"}, "priority": 6},
            {"action": "projects.edit", "conditions": {"role": "pm"}, "priority": 6},
            {"action": "projects.edit", "conditions": {"role": "admin_empresa"}, "priority": 6},
            # Documentos (acceso completo)
            {"action": "documents.*", "conditions": {"role": "tecnico"}, "priority": 5},
            {"action": "documents.*", "conditions": {"role": "supervisor"}, "priority": 5},
            {"action": "documents.*", "conditions": {"role": "pm"}, "priority": 5},
            {"action": "documents.*", "conditions": {"role": "admin_empresa"}, "priority": 5},
            # Dashboard (acceso completo)
            {"action": "dashboard.*", "conditions": {"role": "pm"}, "priority": 5},
            {"action": "dashboard.*", "conditions": {"role": "admin_empresa"}, "priority": 5},
            {"action": "dashboard.*", "conditions": {"role": "supervisor"}, "priority": 5},
            # ROI
            {"action": "roi.*", "conditions": {"role": "pm"}, "priority": 5},
            {"action": "roi.*", "conditions": {"role": "admin_empresa"}, "priority": 5},
            {"action": "roi.view", "conditions": {"role": "supervisor"}, "priority": 6},
            # Sincronización
            {"action": "sync.*", "conditions": {"role": "tecnico"}, "priority": 5},
            {"action": "sync.*", "conditions": {"role": "supervisor"}, "priority": 5},
            {"action": "sync.*", "conditions": {"role": "pm"}, "priority": 5},
            {"action": "sync.*", "conditions": {"role": "admin_empresa"}, "priority": 5},
            # IA (acceso completo)
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
