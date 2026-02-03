"""
Comando para generar datos de prueba para validar funcionalidades P0:
- Proyectos en diferentes estados
- Reportes en diferentes estados (draft, submitted, approved, rejected)
- Usuarios con diferentes roles
"""
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import AccessPolicy, UserProfile
from apps.companies.models import Company, Sitec
from apps.projects.models import Proyecto
from apps.reports.models import ReporteSemanal

User = get_user_model()


class Command(BaseCommand):
    help = "Genera datos de prueba para validar funcionalidades P0 (navegación y rechazo de reportes)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Elimina datos de prueba existentes antes de crear nuevos",
        )

    def handle(self, *args, **options):
        try:
            # Obtener company y sitec
            company = Company.objects.first()
            sitec = Sitec.objects.first()

            if not company or not sitec:
                self.stdout.write(
                    self.style.ERROR("Error: Ejecuta primero 'python manage.py seed_sitec'")
                )
                return

            # Limpiar datos si se solicita
            if options["clear"]:
                self.stdout.write(self.style.WARNING("Eliminando datos de prueba existentes..."))
                try:
                    ReporteSemanal.objects.filter(
                        project_name__startswith="[TEST P0]"
                    ).delete()
                    Proyecto.objects.filter(name__startswith="[TEST P0]").delete()
                    self.stdout.write(self.style.SUCCESS("Datos eliminados"))
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error eliminando datos: {e}")
                    )

            # Crear o obtener usuarios de prueba
            users = self._create_test_users(company)

            # Crear política de acceso si no existe
            try:
                AccessPolicy.objects.get_or_create(
                    company=company,
                    action="*",
                    defaults={
                        "effect": "allow",
                        "priority": 0,
                        "is_active": True,
                    },
                )
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"No se pudo crear política de acceso: {e}")
                )

            # Crear proyectos de prueba
            projects = self._create_test_projects(company, sitec, users)

            # Crear reportes de prueba
            reports = self._create_test_reports(company, sitec, users, projects)

            # Mostrar resumen
            self._show_summary(users, projects, reports)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"\nError general: {e}")
            )
            self.stdout.write(
                self.style.WARNING(
                    "\nPosibles causas:\n"
                    "1. La base de datos está bloqueada (servidor Django corriendo)\n"
                    "2. Problemas de permisos en db.sqlite3\n"
                    "3. Problemas de I/O del disco\n\n"
                    "Solución: Cerrar el servidor Django y volver a intentar"
                )
            )
            raise

    def _create_test_users(self, company):
        """Crear usuarios de prueba con diferentes roles"""
        users = {}

        test_users = [
            {
                "username": "test_pm",
                "email": "test_pm@sitec.mx",
                "password": "test123",
                "role": "pm",
                "first_name": "Test",
                "last_name": "PM",
            },
            {
                "username": "test_supervisor",
                "email": "test_supervisor@sitec.mx",
                "password": "test123",
                "role": "supervisor",
                "first_name": "Test",
                "last_name": "Supervisor",
            },
            {
                "username": "test_tecnico",
                "email": "test_tecnico@sitec.mx",
                "password": "test123",
                "role": "tecnico",
                "first_name": "Test",
                "last_name": "Técnico",
            },
            {
                "username": "test_admin",
                "email": "test_admin@sitec.mx",
                "password": "test123",
                "role": "admin_empresa",
                "first_name": "Test",
                "last_name": "Admin",
            },
        ]

        for user_data in test_users:
            try:
                username = user_data.get("username")
                password = user_data.get("password")
                role = user_data.get("role")
                
                if not username:
                    continue

                user = User.objects.filter(username=username).first()
                created = False

                if not user:
                    user = User(
                        username=username,
                        email=user_data.get("email", f"{username}@sitec.mx"),
                        first_name=user_data.get("first_name", ""),
                        last_name=user_data.get("last_name", ""),
                    )
                    user.set_password(password)
                    user.save()
                    created = True
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ Usuario creado: {username} ({role})")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"→ Usuario existente: {username} ({role})")
                    )

                # Crear o actualizar perfil
                try:
                    profile, profile_created = UserProfile.objects.get_or_create(
                        user=user,
                        defaults={"company": company, "role": role},
                    )
                    if profile.role != role:
                        profile.role = role
                        profile.save()
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"Error actualizando perfil de {username}: {e}")
                    )

                users[role] = user
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error creando usuario {user_data.get('username', 'unknown')}: {e}")
                )
                continue

        return users

    def _create_test_projects(self, company, sitec, users):
        """Crear proyectos de prueba en diferentes estados"""
        projects = {}
        today = date.today()

        test_projects = [
            {
                "name": "[TEST P0] Proyecto En Progreso",
                "code": "TEST-P0-001",
                "description": "Proyecto de prueba en estado 'En Progreso' para validar navegación",
                "site_address": "Av. Reforma 123, CDMX",
                "client_name": "Cliente Test 1",
                "client_contact": "contacto1@test.com",
                "start_date": today - timedelta(days=30),
                "estimated_end_date": today + timedelta(days=60),
                "status": "in_progress",
                "priority": "high",
                "progress_pct": 45,
                "budget_estimated": 500000.00,
                "budget_actual": 225000.00,
                "project_manager": users.get("pm"),
            },
            {
                "name": "[TEST P0] Proyecto Planificación",
                "code": "TEST-P0-002",
                "description": "Proyecto en estado 'Planificación' para probar creación/edición",
                "site_address": "Calle Principal 456, Guadalajara",
                "client_name": "Cliente Test 2",
                "client_contact": "contacto2@test.com",
                "start_date": today + timedelta(days=7),
                "estimated_end_date": today + timedelta(days=90),
                "status": "planning",
                "priority": "medium",
                "progress_pct": 0,
                "budget_estimated": 300000.00,
                "budget_actual": 0.00,
                "project_manager": users.get("pm"),
            },
            {
                "name": "[TEST P0] Proyecto Completado",
                "code": "TEST-P0-003",
                "description": "Proyecto completado para ver historial",
                "site_address": "Blvd. Industrial 789, Monterrey",
                "client_name": "Cliente Test 3",
                "client_contact": "contacto3@test.com",
                "start_date": today - timedelta(days=120),
                "end_date": today - timedelta(days=30),
                "estimated_end_date": today - timedelta(days=30),
                "status": "completed",
                "priority": "high",
                "progress_pct": 100,
                "budget_estimated": 750000.00,
                "budget_actual": 720000.00,
                "project_manager": users.get("pm"),
            },
            {
                "name": "[TEST P0] Proyecto En Pausa",
                "code": "TEST-P0-004",
                "description": "Proyecto en pausa para probar diferentes estados",
                "site_address": "Av. Tecnológico 321, Puebla",
                "client_name": "Cliente Test 4",
                "client_contact": "contacto4@test.com",
                "start_date": today - timedelta(days=60),
                "estimated_end_date": today + timedelta(days=30),
                "status": "on_hold",
                "priority": "medium",
                "progress_pct": 25,
                "budget_estimated": 400000.00,
                "budget_actual": 100000.00,
                "project_manager": users.get("pm"),
            },
        ]

        for project_data in test_projects:
            code = project_data["code"]
            project, created = Proyecto.objects.get_or_create(
                code=code,
                defaults={
                    "company": company,
                    "sitec": sitec,
                    **project_data,
                },
            )

            if created:
                # Asignar técnicos
                if users.get("tecnico"):
                    project.technicians.add(users["tecnico"])

                projects[code] = project
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Proyecto creado: {project.name} ({project.status})")
                )
            else:
                projects[code] = project
                self.stdout.write(
                    self.style.WARNING(f"→ Proyecto existente: {project.name}")
                )

        return projects

    def _create_test_reports(self, company, sitec, users, projects):
        """Crear reportes de prueba en diferentes estados"""
        reports = {}
        today = date.today()
        technician = users.get("tecnico")
        supervisor = users.get("supervisor")

        if not technician:
            self.stdout.write(
                self.style.ERROR("No se encontró usuario técnico para crear reportes")
            )
            return reports

        # Obtener primer proyecto disponible
        project = projects.get("TEST-P0-001") or Proyecto.objects.filter(
            name__startswith="[TEST P0]"
        ).first()

        test_reports = [
            {
                "project_name": "[TEST P0] Proyecto En Progreso",
                "week_start": today - timedelta(days=7),
                "site_address": "Av. Reforma 123, CDMX",
                "progress_pct": 45,
                "status": "submitted",
                "submitted_at": timezone.now() - timedelta(days=2),
                "description": "Reporte enviado esperando aprobación/rechazo",
            },
            {
                "project_name": "[TEST P0] Proyecto En Progreso",
                "week_start": today - timedelta(days=14),
                "site_address": "Av. Reforma 123, CDMX",
                "progress_pct": 40,
                "status": "approved",
                "submitted_at": timezone.now() - timedelta(days=9),
                "approved_at": timezone.now() - timedelta(days=8),
                "supervisor": supervisor,
                "description": "Reporte aprobado (no se puede rechazar)",
            },
            {
                "project_name": "[TEST P0] Proyecto En Progreso",
                "week_start": today - timedelta(days=21),
                "site_address": "Av. Reforma 123, CDMX",
                "progress_pct": 35,
                "status": "rejected",
                "submitted_at": timezone.now() - timedelta(days=16),
                "rejected_at": timezone.now() - timedelta(days=15),
                "supervisor": supervisor,
                "metadata": {
                    "rejection_reason": "Falta información en la sección de incidentes",
                    "rejected_by": str(supervisor.id) if supervisor else None,
                },
                "description": "Reporte rechazado (para ver historial)",
            },
            {
                "project_name": "[TEST P0] Proyecto En Progreso",
                "week_start": today,
                "site_address": "Av. Reforma 123, CDMX",
                "progress_pct": 50,
                "status": "draft",
                "description": "Reporte en borrador (no se puede rechazar)",
            },
            {
                "project_name": "[TEST P0] Proyecto En Progreso",
                "week_start": today - timedelta(days=3),
                "site_address": "Av. Reforma 123, CDMX",
                "progress_pct": 48,
                "status": "submitted",
                "submitted_at": timezone.now() - timedelta(hours=12),
                "description": "Reporte recién enviado para probar rechazo",
            },
        ]

        for i, report_data in enumerate(test_reports):
            week_start = report_data["week_start"]
            status = report_data["status"]
            description = report_data.pop("description", "")

            # Crear reporte único
            report, created = ReporteSemanal.objects.get_or_create(
                company=company,
                sitec=sitec,
                technician=technician,
                week_start=week_start,
                project_name=report_data["project_name"],
                defaults={
                    "project": project,
                    "site_address": report_data["site_address"],
                    "progress_pct": report_data["progress_pct"],
                    "status": status,
                    "submitted_at": report_data.get("submitted_at"),
                    "approved_at": report_data.get("approved_at"),
                    "rejected_at": report_data.get("rejected_at"),
                    "supervisor": report_data.get("supervisor"),
                    "metadata": report_data.get("metadata", {}),
                    "cabling_nodes_total": 100,
                    "cabling_nodes_ok": 95,
                    "racks_installed": 5,
                    "security_devices": 10,
                    "tests_passed": True,
                    "incidents": status == "rejected",
                    "incidents_count": 1 if status == "rejected" else 0,
                },
            )

            if created:
                reports[f"{status}_{i}"] = report
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Reporte creado: {report.project_name} - Semana {week_start} ({status})"
                    )
                )
            else:
                reports[f"{status}_{i}"] = report
                self.stdout.write(
                    self.style.WARNING(
                        f"→ Reporte existente: {report.project_name} - Semana {week_start}"
                    )
                )

        return reports

    def _show_summary(self, users, projects, reports):
        """Mostrar resumen de datos creados"""
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("DATOS DE PRUEBA P0 GENERADOS"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write("")

        # Usuarios
        self.stdout.write(self.style.WARNING("👥 USUARIOS DE PRUEBA:"))
        for role, user in users.items():
            self.stdout.write(f"  • {user.username} ({role}) - Contraseña: test123")
        self.stdout.write("")

        # Proyectos
        self.stdout.write(self.style.WARNING("📁 PROYECTOS DE PRUEBA:"))
        for code, project in projects.items():
            self.stdout.write(
                f"  • {project.name} - Estado: {project.get_status_display()} - Código: {code}"
            )
            self.stdout.write(f"    URL: /projects/{project.id}/")
        self.stdout.write("")

        # Reportes
        self.stdout.write(self.style.WARNING("📄 REPORTES DE PRUEBA:"))
        submitted_count = sum(1 for r in reports.values() if r.status == "submitted")
        approved_count = sum(1 for r in reports.values() if r.status == "approved")
        rejected_count = sum(1 for r in reports.values() if r.status == "rejected")
        draft_count = sum(1 for r in reports.values() if r.status == "draft")

        self.stdout.write(f"  • Enviados (submitted): {submitted_count} - URL: /reports/approvals/")
        self.stdout.write(f"  • Aprobados: {approved_count}")
        self.stdout.write(f"  • Rechazados: {rejected_count}")
        self.stdout.write(f"  • Borradores: {draft_count}")
        self.stdout.write("")

        # URLs de prueba
        self.stdout.write(self.style.SUCCESS("🔗 URLs PARA PRUEBAS:"))
        self.stdout.write("  • Lista de Proyectos: /projects/")
        self.stdout.write("  • Lista de Reportes: /reports/")
        self.stdout.write("  • Aprobaciones: /reports/approvals/")
        if projects:
            first_project = list(projects.values())[0]
            self.stdout.write(f"  • Detalle Proyecto: /projects/{first_project.id}/")
            self.stdout.write(f"  • Editar Proyecto: /projects/{first_project.id}/edit/")
        self.stdout.write("  • Crear Proyecto: /projects/create/")
        self.stdout.write("")

        self.stdout.write(self.style.SUCCESS("✅ Datos de prueba listos para validación manual"))
