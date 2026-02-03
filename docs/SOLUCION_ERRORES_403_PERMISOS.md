# Solución de Errores 403 - Permisos ABAC

**Fecha**: 2026-01-18  
**Versión**: 1.0

---

## 🔍 Problema

El usuario está autenticado pero recibe errores 403 en:
- `/api/wizard/validate/`
- `/api/wizard/analytics/`
- `/api/wizard/sync/`

A pesar de que:
- El usuario tiene rol `tecnico`
- Existen políticas `wizard.*` con `{"role": "tecnico"}`
- Existe una política global `{"action": "*", "effect": "allow"}`

---

## ✅ Solución Implementada

### Problema Identificado

La función `evaluate_access_policy()` no estaba evaluando la política global `*` cuando no encontraba políticas específicas que coincidieran.

**Antes:**
```python
for policy in policies:
    if not action_matches(policy.action, action_name):
        continue
    if matches_conditions(policy.conditions, context):
        return PolicyDecision(...)

# Si no hay coincidencias, retornar False
return PolicyDecision(allowed=False)
```

**Ahora:**
```python
# Buscar políticas específicas primero
for policy in policies:
    if not action_matches(policy.action, action_name):
        continue
    if matches_conditions(policy.conditions, context):
        return PolicyDecision(...)

# Si no hay políticas específicas, buscar política global "*"
if action_name != "*":
    for policy in policies:
        if policy.action == "*" and matches_conditions(policy.conditions, context):
            return PolicyDecision(...)

# Si no hay políticas que coincidan, denegar por defecto
return PolicyDecision(allowed=False)
```

---

## 🔧 Cambios Realizados

### `backend/apps/accounts/services.py`

**Función `evaluate_access_policy()`**:
- Ahora evalúa la política global `*` cuando no encuentra políticas específicas
- Evita recursión al no evaluar `*` cuando la acción es `*` misma
- Mantiene el orden de prioridad (políticas específicas primero, luego global)

---

## 📋 Verificación

Para verificar que las políticas funcionan correctamente:

1. **Verificar políticas activas**:
```bash
python manage.py shell
>>> from apps.accounts.models import AccessPolicy
>>> from apps.companies.models import Company
>>> company = Company.objects.first()
>>> AccessPolicy.objects.filter(company=company, is_active=True, action__startswith="wizard").values("action", "effect", "priority", "conditions")
```

2. **Verificar rol del usuario**:
```bash
>>> from apps.accounts.models import UserProfile
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(username="demo")
>>> profile = UserProfile.objects.get(user=user)
>>> print(f"Rol: {profile.role}, Company: {profile.company.name}")
```

3. **Probar evaluación de políticas**:
```bash
>>> from apps.accounts.services import evaluate_access_policy
>>> from django.test import RequestFactory
>>> factory = RequestFactory()
>>> request = factory.post("/api/wizard/validate/")
>>> request.user = user
>>> request.company = company
>>> decision = evaluate_access_policy(request, "wizard.validate")
>>> print(f"Allowed: {decision.allowed}, Policy: {decision.policy_action}")
```

---

## ✅ Resultado Esperado

Después de esta corrección:

1. ✅ Usuarios con rol `tecnico` pueden acceder a `wizard.validate`, `wizard.analytics`, `wizard.sync`
2. ✅ La política global `*` se evalúa cuando no hay políticas específicas
3. ✅ No más errores 403 para usuarios autenticados con roles válidos

---

## 🔄 Próximos Pasos

Si los errores persisten:

1. **Verificar que las políticas estén activas**:
   ```bash
   python manage.py seed_sitec
   ```

2. **Verificar que el usuario tenga un `UserProfile` con rol válido**

3. **Verificar el contexto de evaluación**:
   - El contexto debe incluir `role`, `company_id`, `method`, etc.
   - Verificar que `build_context()` esté construyendo el contexto correctamente

---

**Última actualización**: 2026-01-18
