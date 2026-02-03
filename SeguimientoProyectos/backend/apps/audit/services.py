import json

from django.forms.models import model_to_dict

from apps.accounts.models import UserProfile

from .models import AuditLog


def _get_client_ip(request):
    if not request:
        return None
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _to_json_safe(payload):
    if payload is None:
        return None
    return json.loads(json.dumps(payload, default=str))


def log_audit_event(request, action, instance, before=None, extra_data=None):
    company = getattr(request, "company", None) if request else None
    actor = None
    user = getattr(request, "user", None) if request else None
    if user is not None and getattr(user, "is_authenticated", False):
        actor = user
        try:
            profile = UserProfile.objects.get(user=user)
            company = profile.company
        except UserProfile.DoesNotExist:
            if company is None:
                company = None

    after = _to_json_safe(model_to_dict(instance)) if instance else None
    before = _to_json_safe(before)
    
    # Si hay extra_data, agregarlo al campo after
    if extra_data:
        if after is None:
            after = {}
        after.update(_to_json_safe(extra_data))
    
    entity_type = instance.__class__.__name__ if instance else "System"
    entity_id = str(instance.pk) if instance and instance.pk else "system"
    if not entity_id:
        entity_id = "system"
    
    AuditLog.objects.create(
        company=company,
        actor=actor,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        before=before,
        after=after,
        ip_address=_get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "") if request else "",
    )
