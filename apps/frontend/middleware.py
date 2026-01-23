"""
Middleware para agregar contexto de usuario a las requests.
Proporciona información del usuario, permisos y configuración de UI
para uso en templates y vistas.
"""
from apps.accounts.models import UserProfile
from apps.accounts.services import get_ui_config_for_role, get_user_permissions


class UserContextMiddleware:
    """
    Middleware que agrega user_context a request para usuarios autenticados.
    El contexto incluye información del perfil, permisos y configuración de UI.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Agregar contexto de usuario si está autenticado
        # Nota: algunos tests/escenarios pueden inyectar un User() no guardado;
        # en ese caso, tratamos como no autenticado para evitar queries inválidas.
        if (
            hasattr(request, "user")
            and getattr(request.user, "is_authenticated", False)
            and getattr(request.user, "pk", None)
        ):
            try:
                profile = UserProfile.objects.select_related("company", "user").get(
                    user=request.user
                )
                
                # Obtener permisos del usuario
                permissions = get_user_permissions(request)
                
                # Obtener configuración de UI según rol
                ui_config = get_ui_config_for_role(profile.role)
                
                # Agregar contexto a request
                request.user_context = {
                    "profile": {
                        "role": profile.role,
                        "department": profile.department,
                        "location": profile.location,
                        "company": {
                            "id": str(profile.company.id) if profile.company else None,
                            "name": profile.company.name if profile.company else None,
                        } if profile.company else None,
                    },
                    "permissions": permissions,
                    "ui_config": ui_config,
                }
            except UserProfile.DoesNotExist:
                # Usuario sin perfil - contexto vacío
                request.user_context = None
        else:
            # Usuario no autenticado - sin contexto
            request.user_context = None

        response = self.get_response(request)
        return response
