"""
Comando para crear usuarios demo con contraseñas conocidas
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.accounts.models import UserProfile
from apps.companies.models import Company, Sitec

User = get_user_model()


class Command(BaseCommand):
    help = "Crea usuarios demo con contraseñas conocidas para pruebas"

    def handle(self, *args, **options):
        # Obtener company y sitec
        company = Company.objects.first()
        sitec = Sitec.objects.first()

        if not company or not sitec:
            self.stdout.write(
                self.style.ERROR("Error: Ejecuta primero 'python manage.py seed_sitec'")
            )
            return

        # Usuarios demo a crear
        demo_users = [
            {
                "username": "demo",
                "email": "demo@sitec.mx",
                "password": "demo123",
                "role": "tecnico",
                "first_name": "Usuario",
                "last_name": "Demo",
            },
            {
                "username": "pm",
                "email": "pm@sitec.mx",
                "password": "pm123",
                "role": "pm",
                "first_name": "Project",
                "last_name": "Manager",
            },
            {
                "username": "supervisor",
                "email": "supervisor@sitec.mx",
                "password": "supervisor123",
                "role": "supervisor",
                "first_name": "Supervisor",
                "last_name": "Demo",
            },
            {
                "username": "admin",
                "email": "admin@sitec.mx",
                "password": "admin123",
                "role": "admin_empresa",
                "first_name": "Administrador",
                "last_name": "Demo",
            },
        ]

        created_count = 0
        updated_count = 0
        users_info = []  # Guardar info para mostrar al final

        for user_data in demo_users:
            # Guardar copia para mostrar al final
            user_info = {
                "username": user_data["username"],
                "password": user_data["password"],
                "role": user_data["role"],
            }
            users_info.append(user_info)

            username = user_data.pop("username")
            password = user_data.pop("password")
            role = user_data.pop("role")

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": user_data["email"],
                    "first_name": user_data.get("first_name", ""),
                    "last_name": user_data.get("last_name", ""),
                    "is_staff": True,  # Permitir login en admin y sistema
                    "is_active": True,
                },
            )

            # Actualizar contraseña y flags siempre
            user.set_password(password)
            user.is_staff = True  # Asegurar que todos los usuarios demo puedan iniciar sesión
            user.is_active = True
            user.save()

            # Crear o actualizar perfil
            profile, profile_created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    "company": company,
                    "role": role,
                },
            )

            if not profile_created:
                # Actualizar si ya existe
                profile.company = company
                profile.role = role
                profile.save()

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"[OK] Usuario '{username}' creado (password: {password}, rol: {role})"
                    )
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"[UPDATE] Usuario '{username}' actualizado (password: {password}, rol: {role})"
                    )
                )

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("USUARIOS DEMO DISPONIBLES:"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        for user_info in users_info:
            self.stdout.write(
                f"  Usuario: {user_info['username']:<15} | Password: {user_info['password']:<15} | Rol: {user_info['role']}"
            )
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Total: {created_count} creados, {updated_count} actualizados"
            )
        )
