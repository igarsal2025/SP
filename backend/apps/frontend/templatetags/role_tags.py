"""
Template tags para controlar la visibilidad de elementos según el rol del usuario.
"""
from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def show_for_role(context, *allowed_roles):
    """
    Retorna True si el rol del usuario actual está en la lista de roles permitidos.
    
    Uso:
        {% show_for_role "pm" "admin_empresa" as can_edit %}
        {% if can_edit %}
            <button>Editar</button>
        {% endif %}
    """
    user_context = context.get("user_context")
    if not user_context:
        return False
    
    user_role = user_context.get("profile", {}).get("role")
    if not user_role:
        return False
    
    return user_role in allowed_roles


@register.simple_tag(takes_context=True)
def dashboard_section_visible(context, section_name):
    """
    Retorna True si la sección del dashboard está visible para el rol del usuario.
    
    Uso:
        {% dashboard_section_visible "roi" as show_roi %}
        {% if show_roi %}
            <div class="panel">
                <!-- Contenido de ROI -->
            </div>
        {% endif %}
    """
    user_context = context.get("user_context")
    if not user_context:
        return False
    
    dashboard_sections = user_context.get("ui_config", {}).get("dashboard_sections", [])
    return section_name in dashboard_sections


@register.simple_tag(takes_context=True)
def has_permission(context, permission_name):
    """
    Retorna True si el usuario tiene el permiso especificado.
    
    Uso:
        {% has_permission "projects.create" as can_create %}
        {% if can_create %}
            <button>Crear Proyecto</button>
        {% endif %}
    """
    user_context = context.get("user_context")
    if not user_context:
        return False
    
    permissions = user_context.get("permissions", {})
    return permissions.get(permission_name, False)


@register.simple_tag(takes_context=True)
def user_role(context):
    """
    Retorna el rol del usuario actual.
    
    Uso:
        {% user_role as role %}
        <span>Rol: {{ role }}</span>
    """
    user_context = context.get("user_context")
    if not user_context:
        return None
    
    return user_context.get("profile", {}).get("role")


@register.simple_tag(takes_context=True)
def can_access_navigation(context, nav_item):
    """
    Retorna True si el usuario puede acceder a un elemento de navegación.
    
    Uso:
        {% can_access_navigation "dashboard" as show_dashboard %}
        {% if show_dashboard %}
            <a href="/dashboard">Dashboard</a>
        {% endif %}
    """
    user_context = context.get("user_context")
    if not user_context:
        return False
    
    navigation = user_context.get("ui_config", {}).get("navigation", [])
    return nav_item in navigation


@register.simple_tag(takes_context=True)
def wizard_mode(context):
    """
    Retorna el modo del wizard para el usuario actual ('full' o 'readonly').
    
    Uso:
        {% wizard_mode as mode %}
        {% if mode == "full" %}
            <button>Guardar</button>
        {% endif %}
    """
    user_context = context.get("user_context")
    if not user_context:
        return "readonly"
    
    return user_context.get("ui_config", {}).get("wizard_mode", "readonly")
