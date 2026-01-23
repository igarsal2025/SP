import logging
from rest_framework.permissions import BasePermission

from .services import action_from_request, evaluate_access_policy

logger = logging.getLogger(__name__)


class AccessPolicyPermission(BasePermission):
    """Aplica politicas ABAC basicas por company y rol."""

    def has_permission(self, request, view):
        action_name = action_from_request(request, view)
        user = getattr(request, "user", None)
        
        logger.debug(
            f"[ABAC Permission] Checking access: action={action_name}, "
            f"user={user.username if user else 'anonymous'}, "
            f"authenticated={user.is_authenticated if user else False}"
        )
        
        decision = evaluate_access_policy(request, action_name)
        
        if not decision.allowed:
            logger.warning(
                f"[ABAC Permission] Access DENIED: action={action_name}, "
                f"user={user.username if user else 'anonymous'}, "
                f"authenticated={user.is_authenticated if user else False}, "
                f"policy={decision.policy_action}"
            )
        else:
            logger.debug(
                f"[ABAC Permission] Access GRANTED: action={action_name}, "
                f"user={user.username if user else 'anonymous'}, "
                f"policy={decision.policy_action}"
            )
        
        return decision.allowed
