from rest_framework.permissions import BasePermission

from .services import action_from_request, evaluate_access_policy


class AccessPolicyPermission(BasePermission):
    """Aplica politicas ABAC basicas por company y rol."""

    def has_permission(self, request, view):
        action_name = action_from_request(request, view)
        decision = evaluate_access_policy(request, action_name)
        return decision.allowed
