from dataclasses import dataclass

from .models import AccessPolicy, UserProfile


@dataclass
class PolicyDecision:
    allowed: bool
    policy_id: str | None = None
    policy_action: str | None = None
    policy_effect: str | None = None


def build_context(request, profile):
    return {
        "role": profile.role,
        "department": profile.department,
        "location": profile.location,
        "company_id": str(getattr(profile.company, "id", "")),
        "sitec_id": str(getattr(request, "sitec", None) or ""),
        "method": request.method.lower(),
        "path": request.path,
    }


def action_from_request(request, view):
    if hasattr(view, "action") and view.action:
        return view.action
    path_parts = request.path.strip("/").split("/")
    if len(path_parts) >= 2 and path_parts[0] == "api":
        return ".".join(path_parts[1:])
    return request.method.lower()


def action_matches(policy_action, action_name):
    if policy_action == "*":
        return True
    if policy_action == action_name:
        return True
    if policy_action.endswith(".*"):
        prefix = policy_action[:-2]
        return action_name.startswith(prefix)
    # Manejar casos como "transactions.create" vs "create"
    # Si la política tiene un prefijo como "transactions.", verificar si la acción coincide con el sufijo
    if "." in policy_action:
        parts = policy_action.split(".")
        if len(parts) == 2:
            # Política: "transactions.create", acción: "create"
            if parts[1] == action_name:
                return True
            # Política: "transactions.create", acción: "transactions.create"
            if policy_action == action_name:
                return True
    return False


def matches_conditions(conditions, context):
    if not conditions:
        return True
    for key, expected in conditions.items():
        actual = context.get(key)
        if isinstance(expected, list):
            if actual not in expected:
                return False
            continue
        if actual != expected:
            return False
    return True


def evaluate_access_policy(request, action_name):
    import logging
    logger = logging.getLogger(__name__)
    
    user = getattr(request, "user", None)
    if not user:
        logger.debug(f"[ABAC] No user found for action: {action_name}")
        return PolicyDecision(allowed=False)
    
    # Verificar autenticación - usar el método correcto para Django
    # En Django, is_authenticated es una propiedad, no un método
    if not hasattr(user, 'is_authenticated'):
        logger.debug(f"[ABAC] User {user} has no is_authenticated attribute")
        return PolicyDecision(allowed=False)
    
    # Verificar si es una propiedad o método
    is_authenticated = user.is_authenticated
    if callable(is_authenticated):
        is_authenticated = is_authenticated()
    
    if not is_authenticated:
        logger.debug(f"[ABAC] User {user.username} is not authenticated for action: {action_name}")
        return PolicyDecision(allowed=False)

    profile = UserProfile.objects.select_related("company").filter(user=user).first()
    if not profile:
        logger.debug(f"[ABAC] No profile found for user {user.username}")
        return PolicyDecision(allowed=False)
    
    if not profile.company:
        logger.debug(f"[ABAC] No company found for user {user.username}")
        return PolicyDecision(allowed=False)

    # Admin empresa siempre tiene acceso completo
    if profile.role == "admin_empresa":
        logger.debug(f"[ABAC] Admin empresa {user.username} granted access to {action_name}")
        return PolicyDecision(
            allowed=True,
            policy_action="admin_empresa",
            policy_effect="allow",
        )

    context = build_context(request, profile)
    
    # Primero verificar políticas explícitas (tienen máxima prioridad)
    policies = (
        AccessPolicy.objects.filter(company=profile.company, is_active=True)
        .order_by("-priority")
        .all()
    )
    
    # PRIMERO: Verificar políticas de solo lectura ANTES de buscar políticas específicas o globales
    # Esto asegura que las restricciones de solo lectura tengan máxima prioridad
    write_actions = ['create', 'update', 'partial_update', 'destroy']
    if action_name in write_actions:
        # Buscar políticas de lectura específicas para el mismo recurso
        # Estas políticas tienen prioridad sobre políticas globales y específicas de escritura
        for policy in policies.order_by("-priority"):
            # Verificar si es una política de solo lectura (ej: transactions.read)
            policy_parts = policy.action.split('.')
            is_read_only = len(policy_parts) == 2 and policy_parts[1] == 'read'
            
            if is_read_only and policy.effect == "allow":
                # Verificar condiciones (rol, etc.)
                if matches_conditions(policy.conditions, context):
                    # Verificar si es para el mismo recurso (ej: transactions.read vs transactions.create)
                    policy_resource = policy_parts[0]
                    action_resource = None
                    if 'transactions' in request.path.lower() or 'transacciones' in request.path.lower():
                        action_resource = 'transactions'
                    
                    if policy_resource and action_resource and policy_resource == action_resource:
                        logger.debug(
                            f"[ABAC] Read-only policy found for write action: "
                            f"policy={policy.action}, action={action_name}, role={context.get('role')}, "
                            f"resource={action_resource}, priority={policy.priority}, DENYING"
                        )
                        return PolicyDecision(
                            allowed=False,
                            policy_action=policy.action,
                            policy_effect="deny",
                        )
    
    # SEGUNDO: Buscar políticas específicas que coincidan exactamente (incluyendo deny)
    for policy in policies:
        if not action_matches(policy.action, action_name):
            continue
        if matches_conditions(policy.conditions, context):
            decision = PolicyDecision(
                allowed=policy.effect == "allow",
                policy_id=str(policy.id),
                policy_action=policy.action,
                policy_effect=policy.effect,
            )
            logger.debug(
                f"[ABAC] Policy matched: action={action_name}, "
                f"policy_action={policy.action}, effect={policy.effect}, "
                f"priority={policy.priority}, allowed={decision.allowed}"
            )
            return decision

    # TERCERO: Si no hay políticas específicas que coincidan, buscar política global "*"
    # (solo si no es la acción "*" misma para evitar recursión)
    if action_name != "*":
        for policy in policies:
            if policy.action == "*" and matches_conditions(policy.conditions, context):
                decision = PolicyDecision(
                    allowed=policy.effect == "allow",
                    policy_id=str(policy.id),
                    policy_action=policy.action,
                    policy_effect=policy.effect,
                )
                logger.debug(
                    f"[ABAC] Global policy matched: action={action_name}, "
                    f"effect={policy.effect}, allowed={decision.allowed}"
                )
                return decision
    
    # Si no hay políticas explícitas, aplicar reglas por defecto
    # Políticas restrictivas por defecto para transacciones
    # Solo ciertos roles pueden realizar operaciones CRUD en transacciones
    if action_name in ['create', 'update', 'partial_update', 'destroy']:
        # Verificar si es una acción de transacciones
        if 'transactions' in request.path.lower() or 'transacciones' in request.path.lower():
            # Solo admin_empresa, pm, supervisor y tecnico pueden crear/actualizar/eliminar
            allowed_roles = ['admin_empresa', 'pm', 'supervisor', 'tecnico']
            if profile.role not in allowed_roles:
                logger.debug(
                    f"[ABAC] Access DENIED for transactions {action_name}: "
                    f"role={profile.role} not in allowed_roles={allowed_roles}"
                )
                return PolicyDecision(
                    allowed=False,
                    policy_action=action_name,
                    policy_effect="deny",
                )
    
    # Si no hay políticas y no es una acción de transacciones, aplicar reglas por defecto
    if not policies.exists():
        # Por defecto, permitir solo lectura para la mayoría de acciones
        # pero denegar escritura si no hay políticas explícitas
        if action_name in ['create', 'update', 'partial_update', 'destroy']:
            # Para acciones de escritura, requerir políticas explícitas
            logger.debug(
                f"[ABAC] No policies found, denying write action: {action_name}"
            )
            return PolicyDecision(allowed=False)
        # Para acciones de lectura, permitir si está autenticado
        return PolicyDecision(allowed=True)
    
    # Si hay políticas pero ninguna coincidió, denegar por defecto para escritura
    if action_name in ['create', 'update', 'partial_update', 'destroy']:
        logger.debug(
            f"[ABAC] No matching policy found, denying write action: {action_name}"
        )
        return PolicyDecision(allowed=False)
    
    # Para lectura, permitir si está autenticado
    return PolicyDecision(allowed=True)


def get_ui_config_for_role(role):
    """
    Obtiene la configuración de UI según el rol del usuario.
    Define qué navegación, secciones de dashboard y modo de wizard se muestran.
    """
    configs = {
        "admin_empresa": {
            "navigation": ["dashboard", "projects", "reports", "documents", "configuration", "users"],
            "dashboard_sections": [
                "kpis",
                "alerts",
                "comparatives",
                "trends",
                "history",
                "aggregate",
                "roi",
                "projects",
                "reports",
            ],
            "wizard_mode": "full",
            "can_create_projects": True,
            "can_approve_reports": True,
            "can_edit_projects": True,
            "can_use_field_mode": True,
            "can_use_ai_chat": True,
            "can_generate_pdf": True,
        },
        "pm": {
            "navigation": ["dashboard", "projects", "reports", "documents"],
            "dashboard_sections": [
                "kpis",
                "alerts",
                "comparatives",
                "trends",
                "roi",
                "projects",
                "reports",
            ],
            "wizard_mode": "full",
            "can_create_projects": True,
            "can_approve_reports": True,
            "can_edit_projects": True,
            "can_use_field_mode": False,
            "can_use_ai_chat": True,
            "can_generate_pdf": True,
        },
        "supervisor": {
            "navigation": ["dashboard", "projects", "reports", "approvals"],
            "dashboard_sections": [
                "kpis",
                "alerts",
                "projects",
                "reports",
            ],
            "wizard_mode": "full",
            "can_create_projects": False,
            "can_approve_reports": True,
            "can_edit_projects": False,
            "can_use_field_mode": False,
            "can_use_ai_chat": True,
            "can_generate_pdf": True,
        },
        "tecnico": {
            "navigation": ["wizard", "projects", "reports", "documents"],
            "dashboard_sections": [
                "kpis",
                "alerts",
                "projects",
                "reports",
            ],
            "wizard_mode": "full",
            "can_create_projects": False,
            "can_approve_reports": False,
            "can_edit_projects": False,
            "can_use_field_mode": True,
            "can_use_ai_chat": True,
            "can_generate_pdf": True,
        },
        "cliente": {
            "navigation": ["projects", "documents"],
            "dashboard_sections": [
                "projects",
            ],
            "wizard_mode": "readonly",
            "can_create_projects": False,
            "can_approve_reports": False,
            "can_edit_projects": False,
            "can_use_field_mode": False,
            "can_use_ai_chat": False,
            "can_generate_pdf": False,
        },
    }
    return configs.get(role, configs["cliente"])


def get_user_permissions(request, actions_to_check=None):
    """
    Obtiene los permisos del usuario para un conjunto de acciones.
    Si no se especifican acciones, devuelve un conjunto común de permisos.
    """
    if actions_to_check is None:
        actions_to_check = [
            "dashboard.view",
            "dashboard.trends.view",
            "dashboard.export",
            "projects.create",
            "projects.edit",
            "projects.view",
            "reports.create",
            "reports.approve",
            "reports.view",
            "wizard.save",
            "wizard.submit",
            "wizard.view",
            "wizard.validate",
            "wizard.sync",
            "wizard.analytics",
            "documents.generate",
            "documents.download",
            "roi.view",
            "roi.export",
        ]
    
    permissions = {}
    for action in actions_to_check:
        decision = evaluate_access_policy(request, action)
        permissions[action] = decision.allowed
    
    return permissions
