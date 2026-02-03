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
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return PolicyDecision(allowed=False)

    profile = UserProfile.objects.select_related("company").filter(user=user).first()
    if not profile or not profile.company:
        return PolicyDecision(allowed=False)

    if profile.role == "admin_empresa":
        return PolicyDecision(allowed=True)

    context = build_context(request, profile)
    policies = (
        AccessPolicy.objects.filter(company=profile.company, is_active=True)
        .order_by("-priority")
        .all()
    )
    if not policies.exists():
        return PolicyDecision(allowed=True)

    for policy in policies:
        if not action_matches(policy.action, action_name):
            continue
        if matches_conditions(policy.conditions, context):
            return PolicyDecision(
                allowed=policy.effect == "allow",
                policy_id=str(policy.id),
                policy_action=policy.action,
                policy_effect=policy.effect,
            )

    return PolicyDecision(allowed=False)
