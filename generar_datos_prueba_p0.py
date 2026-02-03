#!/usr/bin/env python
"""
Script independiente para generar datos de prueba P0
Ejecutar directamente: python generar_datos_prueba_p0.py
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    django.setup()
except Exception as e:
    print(f"Error configurando Django: {e}")
    sys.exit(1)

from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.accounts.models import AccessPolicy, UserProfile
from apps.companies.models import Company, Sitec
from apps.projects.models import Proyecto
from apps.reports.models import ReporteSemanal

User = get_user_model()

def main():
    print("=" * 60)
    print("Generación de Datos de Prueba P0")
    print("=" * 60)
    print()

    # Obtener company y sitec
    try:
        company = Company.objects.first()
        sitec = Sitec.objects.first()
    except Exception as e:
        print(f"ERROR: Error accediendo a la base de datos: {e}")
        print("\nPosibles soluciones:")
        print("1. Verificar que la base de datos no esté bloqueada")
        print("2. Verificar permisos en db.sqlite3")
        print("3. Intentar reparar la base de datos")
        return

    if not company or not sitec:
        print("ERROR: No se encontró Company o Sitec")
        print("Ejecuta primero: python manage.py seed_sitec")
        return

    print(f"✓ Company encontrada: {company.name}")
    print(f"✓ Sitec encontrado: {sitec.schema_name}")
    print()

    # Crear usuarios
    print("👥 Creando usuarios de prueba...")
    users = {}
    test_users = [
        {"username": "test_pm", "email": "test_pm@sitec.mx", "password": "test123", "role": "pm", "first_name": "Test", "last_name": "PM"},
        {"username": "test_supervisor", "email": "test_supervisor@sitec.mx", "password": "test123", "role": "supervisor", "first_name": "Test", "last_name": "Supervisor"},
        {"username": "test_tecnico", "email": "test_tecnico@sitec.mx", "password": "test123", "role": "tecnico", "first_name": "Test", "last_name": "Técnico"},
        {"username": "test_admin", "email": "test_admin@sitec.mx", "password": "test123", "role": "admin_empresa", "first_name": "Test", "last_name": "Admin"},
    ]

    for ud in test_users:
        try:
            username = ud["username"]
            password = ud["password"]
            role = ud["role"]
            
            user = User.objects.filter(username=username).first()
            if not user:
                user = User.objects.create_user(
                    username=username,
                    email=ud["email"],
                    password=password,
                    first_name=ud["first_name"],
                    last_name=ud["last_name"],
                )
                print(f"  ✓ Usuario creado: {username} ({role})")
            else:
                print(f"  → Usuario existente: {username} ({role})")
            
            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={"company": company, "role": role},
            )
            if profile.role != role:
                profile.role = role
                profile.save()
            
            users[role] = user
        except Exception as e:
            print(f"  ERROR: Error creando usuario {ud.get('username', 'unknown')}: {e}")
            continue

    print()

    # Crear política de acceso
    try:
        AccessPolicy.objects.get_or_create(
            company=company,
            action="*",
            defaults={"effect": "allow", "priority": 0, "is_active": True},
        )
        print("✓ Política de acceso configurada")
    except Exception as e:
        print(f"⚠️  No se pudo crear política de acceso: {e}")
    print()

    # Crear proyectos
    print("📁 Creando proyectos de prueba...")
    projects = {}
    today = date.today()

    project_data = [
        {
            "name": "[TEST P0] Proyecto En Progreso",
            "code": "TEST-P0-001",
            "description": "Proyecto de prueba en estado 'En Progreso'",
            "site_address": "Av. Reforma 123, CDMX",
            "client_name": "Cliente Test 1",
            "start_date": today - timedelta(days=30),
            "estimated_end_date": today + timedelta(days=60),
            "status": "in_progress",
            "priority": "high",
            "progress_pct": 45,
            "budget_estimated": 500000.00,
            "budget_actual": 225000.00,
        },
        {
            "name": "[TEST P0] Proyecto Planificación",
            "code": "TEST-P0-002",
            "description": "Proyecto en estado 'Planificación'",
            "site_address": "Calle Principal 456, Guadalajara",
            "client_name": "Cliente Test 2",
            "start_date": today + timedelta(days=7),
            "estimated_end_date": today + timedelta(days=90),
            "status": "planning",
            "priority": "medium",
            "progress_pct": 0,
            "budget_estimated": 300000.00,
        },
        {
            "name": "[TEST P0] Proyecto Completado",
            "code": "TEST-P0-003",
            "description": "Proyecto completado",
            "site_address": "Blvd. Industrial 789, Monterrey",
            "client_name": "Cliente Test 3",
            "start_date": today - timedelta(days=120),
            "end_date": today - timedelta(days=30),
            "estimated_end_date": today - timedelta(days=30),
            "status": "completed",
            "priority": "high",
            "progress_pct": 100,
            "budget_estimated": 750000.00,
            "budget_actual": 720000.00,
        },
        {
            "name": "[TEST P0] Proyecto En Pausa",
            "code": "TEST-P0-004",
            "description": "Proyecto en pausa",
            "site_address": "Av. Tecnológico 321, Puebla",
            "client_name": "Cliente Test 4",
            "start_date": today - timedelta(days=60),
            "estimated_end_date": today + timedelta(days=30),
            "status": "on_hold",
            "priority": "medium",
            "progress_pct": 25,
            "budget_estimated": 400000.00,
            "budget_actual": 100000.00,
        },
    ]

    for pd in project_data:
        try:
            code = pd.pop("code")
            project, created = Proyecto.objects.get_or_create(
                code=code,
                defaults={
                    "company": company,
                    "sitec": sitec,
                    "project_manager": users.get("pm"),
                    **pd,
                },
            )
            if created:
                if users.get("tecnico"):
                    project.technicians.add(users["tecnico"])
                projects[code] = project
                print(f"  ✓ Proyecto creado: {project.name} ({project.status})")
            else:
                projects[code] = project
                print(f"  → Proyecto existente: {project.name}")
        except Exception as e:
                print(f"  ERROR: Error creando proyecto {pd.get('name', 'unknown')}: {e}")
            continue

    print()

    # Crear reportes
    print("📄 Creando reportes de prueba...")
    technician = users.get("tecnico")
    supervisor = users.get("supervisor")
    project = projects.get("TEST-P0-001") or Proyecto.objects.filter(name__startswith="[TEST P0]").first()

    if not technician:
        print("  ⚠️  No se encontró usuario técnico, saltando reportes")
    elif not project:
        print("  ⚠️  No se encontró proyecto, saltando reportes")
    else:
        report_data = [
            {
                "project_name": "[TEST P0] Proyecto En Progreso",
                "week_start": today - timedelta(days=3),
                "site_address": "Av. Reforma 123, CDMX",
                "progress_pct": 48,
                "status": "submitted",
                "submitted_at": timezone.now() - timedelta(hours=12),
            },
            {
                "project_name": "[TEST P0] Proyecto En Progreso",
                "week_start": today - timedelta(days=7),
                "site_address": "Av. Reforma 123, CDMX",
                "progress_pct": 45,
                "status": "submitted",
                "submitted_at": timezone.now() - timedelta(days=2),
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
                "metadata": {"rejection_reason": "Falta información en la sección de incidentes"},
            },
            {
                "project_name": "[TEST P0] Proyecto En Progreso",
                "week_start": today,
                "site_address": "Av. Reforma 123, CDMX",
                "progress_pct": 50,
                "status": "draft",
            },
        ]
        
        for rd in report_data:
            try:
                week_start = rd["week_start"]
                status = rd["status"]
                
                report, created = ReporteSemanal.objects.get_or_create(
                    company=company,
                    sitec=sitec,
                    technician=technician,
                    week_start=week_start,
                    project_name=rd["project_name"],
                    defaults={
                        "project": project,
                        "site_address": rd["site_address"],
                        "progress_pct": rd["progress_pct"],
                        "status": status,
                        "submitted_at": rd.get("submitted_at"),
                        "approved_at": rd.get("approved_at"),
                        "rejected_at": rd.get("rejected_at"),
                        "supervisor": rd.get("supervisor"),
                        "metadata": rd.get("metadata", {}),
                        "cabling_nodes_total": 100,
                        "cabling_nodes_ok": 95,
                        "racks_installed": 5,
                        "security_devices": 10,
                        "tests_passed": True,
                    },
                )
                if created:
                    print(f"  ✓ Reporte creado: {report.project_name} - Semana {week_start} ({status})")
                else:
                    print(f"  → Reporte existente: {report.project_name} - Semana {week_start}")
            except Exception as e:
                print(f"  ❌ Error creando reporte: {e}")
                continue

    print()
    print("=" * 60)
    print("✅ Datos de prueba generados exitosamente!")
    print("=" * 60)
    print()
    print("👥 USUARIOS DE PRUEBA:")
    for role, user in users.items():
        print(f"  • {user.username} ({role}) - Contraseña: test123")
    print()
    print("📁 PROYECTOS DE PRUEBA:")
    for code, project in projects.items():
        print(f"  • {project.name} - Estado: {project.get_status_display()} - Código: {code}")
        print(f"    URL: /projects/{project.id}/")
    print()
    print("🔗 URLs PARA PRUEBAS:")
    print("  • Lista de Proyectos: /projects/")
    print("  • Lista de Reportes: /reports/")
    print("  • Aprobaciones: /reports/approvals/")
    if projects:
        first_project = list(projects.values())[0]
        print(f"  • Detalle Proyecto: /projects/{first_project.id}/")
        print(f"  • Editar Proyecto: /projects/{first_project.id}/edit/")
    print("  • Crear Proyecto: /projects/create/")
    print()

if __name__ == "__main__":
    main()
