# Instrucciones para Aplicar Migración rejected_at

**Fecha**: 2026-01-23

---

## 📋 Cambio Realizado

Se agregó el campo `rejected_at` al modelo `ReporteSemanal` en `backend/apps/reports/models.py`:

```python
rejected_at = models.DateTimeField(null=True, blank=True)
```

---

## 🔧 Pasos para Aplicar Migración

### 1. Activar Entorno Virtual

```powershell
cd G:\SeguimientoProyectos\backend
.\.venv\Scripts\Activate.ps1
```

### 2. Crear Migración

```bash
python manage.py makemigrations reports --name add_rejected_at
```

### 3. Aplicar Migración

```bash
python manage.py migrate reports
```

---

## ✅ Verificación

Después de aplicar la migración, verificar que:

1. El campo `rejected_at` existe en la tabla `reports_reportesemanal`
2. El endpoint `/api/reports/reportes/<id>/reject/` funciona correctamente
3. El campo se serializa correctamente en las respuestas API

---

**Nota**: La migración se creará automáticamente cuando se ejecute `makemigrations`. El campo es nullable, por lo que no afectará datos existentes.
