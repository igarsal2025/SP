# Actualizar Cache del Navegador

**Fecha**: 2026-01-18  
**Versión**: 1.0

---

## 🔍 Problema

Después de actualizar el código JavaScript, el navegador puede estar usando una versión en caché, lo que causa que los errores persistan.

---

## ✅ Solución: Forzar Recarga del Cache

### Opción 1: Recarga Forzada (Recomendado)

**Chrome/Edge/Firefox:**
- **Windows/Linux**: `Ctrl + Shift + R` o `Ctrl + F5`
- **Mac**: `Cmd + Shift + R`

### Opción 2: Limpiar Cache del Navegador

1. **Chrome/Edge:**
   - Presiona `F12` para abrir DevTools
   - Click derecho en el botón de recargar
   - Selecciona "Vaciar caché y volver a cargar de forma forzada"

2. **Firefox:**
   - Presiona `Ctrl + Shift + Delete` (Windows) o `Cmd + Shift + Delete` (Mac)
   - Selecciona "Caché" y "Ahora"
   - Recarga la página

### Opción 3: Modo Incógnito

Abre la página en modo incógnito/privado para evitar el cache:
- **Chrome/Edge**: `Ctrl + Shift + N` (Windows) o `Cmd + Shift + N` (Mac)
- **Firefox**: `Ctrl + Shift + P` (Windows) o `Cmd + Shift + P` (Mac)

---

## 🔧 Verificar que se Cargó la Versión Correcta

1. Abre DevTools (`F12`)
2. Ve a la pestaña **Network**
3. Recarga la página con `Ctrl + Shift + R`
4. Busca `wizard.js` en la lista
5. Verifica que la columna **Size** no diga "(from cache)"
6. Click en `wizard.js` y verifica la pestaña **Response** para ver el código actualizado

---

## 📋 Cambios Recientes que Requieren Recarga

Los siguientes cambios requieren una recarga forzada:

1. ✅ Verificación de autenticación en `validateStep()`
2. ✅ Deshabilitación de geolocalización automática
3. ✅ Manejo mejorado de errores 403/401
4. ✅ Inclusión de `credentials: "include"` en fetch requests

---

## ⚠️ Si los Errores Persisten

Si después de limpiar el cache los errores persisten:

1. **Verifica que el servidor esté ejecutándose**:
   ```bash
   cd backend
   python manage.py runserver
   ```

2. **Verifica que los archivos se hayan guardado correctamente**:
   - Revisa `backend/static/frontend/js/wizard.js`
   - Busca las funciones `getCurrentProfile()` y `validateStep()`

3. **Verifica la consola del navegador**:
   - Abre DevTools (`F12`)
   - Ve a la pestaña **Console**
   - Busca errores específicos

4. **Verifica la autenticación**:
   - Asegúrate de estar autenticado
   - Usa las credenciales demo: `demo` / `demo123`

---

## 🔄 Actualización Automática del Cache

Para desarrollo, puedes deshabilitar el cache en DevTools:

1. Abre DevTools (`F12`)
2. Ve a la pestaña **Network**
3. Marca la casilla **"Disable cache"**
4. Mantén DevTools abierto mientras desarrollas

**Nota**: Esto solo funciona mientras DevTools está abierto.

---

**Última actualización**: 2026-01-18
