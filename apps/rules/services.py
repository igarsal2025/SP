import re

from django.core.cache import cache

from .models import RuleSet

CACHE_TTL = 300


def _get_value(data, field):
    return data.get(field)


def _match_condition(data, condition):
    field = condition.get("field")
    op = condition.get("op")
    value = condition.get("value")

    current = _get_value(data, field)

    if op == "required":
        return current is None or current == ""
    if op == "eq":
        return current == value
    if op == "neq":
        return current != value
    if op == "gt":
        return current is not None and float(current) > float(value)
    if op == "gte":
        return current is not None and float(current) >= float(value)
    if op == "lt":
        return current is not None and float(current) < float(value)
    if op == "lte":
        return current is not None and float(current) <= float(value)
    if op == "contains":
        return current is not None and str(value) in str(current)
    if op == "regex":
        if current is None:
            return False
        return re.match(str(value), str(current)) is None

    return False


def evaluate_rules(ruleset, step, data):
    results = []
    if not ruleset:
        return results
    for rule in ruleset.rules.all():
        if rule.step and rule.step != step:
            continue
        condition = rule.condition or {}
        if _match_condition(data, condition):
            results.append(
                {
                    "code": rule.code,
                    "severity": rule.severity,
                    "message": rule.message,
                    "field": rule.field,
                }
            )
    return results


def get_active_ruleset(company, sitec, scope="wizard"):
    cache_key = f"ruleset:{company.id}:{sitec.id}:{scope}"
    cached_id = cache.get(cache_key)
    if cached_id:
        return RuleSet.objects.filter(id=cached_id).first()
    ruleset = (
        RuleSet.objects.filter(
            company=company,
            sitec=sitec,
            scope=scope,
            is_active=True,
        )
        .order_by("-version")
        .first()
    )
    if ruleset:
        cache.set(cache_key, ruleset.id, CACHE_TTL)
    return ruleset
