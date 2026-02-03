# Instrucciones Alternativas: Generar Datos de Prueba P0

**Fecha**: 2026-01-23  
**Versión**: 1.0

---

## ⚠️ Problema Detectado

Si el comando `generate_test_data_p0` falla con error `disk I/O error`, puede deberse a problemas con la base de datos SQLite. Esta guía proporciona métodos alternativos.

---

## 🔧 Método 1: Usar Django Shell (Recomendado)

### Paso 1: Abrir Django Shell

```powershell
cd G:\SeguimientoProyectos\backend
..\.venv\Scripts\python.exe manage.py shell
```

### Paso 2: Ejecutar Script de Creación

Copiar y pegar el siguiente código en el shell:

```python
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.accounts.models import AccessPolicy, UserProfile
from apps.companies.models import Company, Sitec
from apps.projects.models import Proyecto
from apps.reports.models import ReporteSemanal

User = get_user_model()

# Obtener company y sitec
company = Company.objects.first()
sitec = Sitec.objects.first()

if not company or not sitec:
    print("Error: Ejecuta primero 'python manage.py seed_sitec'")
    exit()

# Crear usuarios
users = {}
test_users = [
    {"username": "test_pm", "email": "test_pm@sitec.mx", "password": "test123", "role": "pm", "first_name": "Test", "last_name": "PM"},
    {"username": "test_supervisor", "email": "test_supervisor@sitec.mx", "password": "test123", "role": "supervisor", "first_name": "Test", "last_name": "Supervisor"},
    {"username": "test_tecnico", "email": "test_tecnico@sitec.mx", "password": "test123", "role": "tecnico", "first_name": "Test", "last_name": "Técnico"},
    {"username": "test_admin", "email": "test_admin@sitec.mx", "password": "test123", "role": "admin_empresa", "first_name": "Test", "last_name": "Admin"},
]

for ud in test_users:
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
        print(f"✓ Usuario creado: {username}")
    else:
        print(f"→ Usuario existente: {username}")
    
    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={"company": company, "role": role},
    )
    if profile.role != role:
        profile.role = role
        profile.save()
    
    users[role] = user

# Crear política de acceso
AccessPolicy.objects.get_or_create(
    company=company,
    action="*",
    defaults={"effect": "allow", "priority": 0, "is_active": True},
)

# Crear proyectos
today = date.today()
projects = {}

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
]

for pd in project_data:
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
        print(f"✓ Proyecto creado: {project.name}")
    else:
        projects[code] = project
        print(f"→ Proyecto existente: {project.name}")

# Crear reportes
technician = users.get("tecnico")
supervisor = users.get("supervisor")
project = projects.get("TEST-P0-001") or Proyecto.objects.filter(name__startswith="[TEST P0]").first()

if technician and project:
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
            print(f"✓ Reporte creado: {report.project_name} - Semana {week_start} ({status})")
        else:
            print(f"→ Reporte existente: {report.project_name} - Semana {week_start}")

print("\n✅ Datos de prueba generados exitosamente!")
print("\nUsuarios creados:")
for role, user in users.items():
    print(f"  • {user.username} ({role}) - Contraseña: test123")
```

### Paso 3: Salir del Shell

```python
exit()
```

---

## 🔧 Método 2: Crear Script Python Independiente

Crear un archivo `generate_test_data_manual.py` en la raíz del proyecto:

```python
#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Ahora importar modelos
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.accounts.models import AccessPolicy, UserProfile
from apps.companies.models import Company, Sitec
from apps.projects.models import Proyecto
from apps.reports.models import ReporteSemanal

# ... (resto del código del método 1)
```

Ejecutar:
```powershell
cd G:\SeguimientoProyectos
..\.venv\Scripts\python.exe generate_test_data_manual.py
```

---

## 🔧 Método 3: Verificar y Reparar Base de Datos

Si el problema persiste, puede ser necesario verificar la integridad de la base de datos:

```powershell
cd G:\SeguimientoProyectos\backend
..\.venv\Scripts\python.exe manage.py dbshell
```

En el shell de SQLite:
```sql
PRAGMA integrity_check;
```

Si hay errores, hacer backup y recrear:
```powershell
# Backup
Copy-Item db.sqlite3 db.sqlite3.backup

# Recrear (esto eliminará todos los datos)
Remove-Item db.sqlite3
..\.venv\Scripts\python.exe manage.py migrate
..\.venv\Scripts\python.exe manage.py seed_sitec
```

---

## ✅ Verificación

Después de generar los datos, verificar:

```python
# En Django shell
from apps.projects.models import Proyecto
from apps.reports.models import ReporteSemanal

print(f"Proyectos TEST P0: {Proyecto.objects.filter(name__startswith='[TEST P0]').count()}")
print(f"Reportes TEST P0: {ReporteSemanal.objects.filter(project_name__startswith='[TEST P0]').count()}")
```

---

**Última actualización**: 2026-01-23
