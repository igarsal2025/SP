# Guía de Uso - Tendencias Históricas del Dashboard

**Fecha**: 2026-01-18  
**Versión**: 1.0

---

## 📊 Introducción

El panel de **Tendencias Históricas** permite visualizar la evolución de métricas clave del sistema a lo largo del tiempo, con gráficos interactivos y funcionalidades de exportación.

---

## 🎯 Acceso

1. Navegar al **Dashboard** (`/dashboard/`)
2. Desplazarse hasta el panel **"Tendencias Históricas"**
3. Seleccionar tipo de período y número de períodos
4. Hacer clic en **"Cargar"**

---

## ⚙️ Configuración

### Tipo de Período

- **Mensual**: Muestra datos agregados por mes
- **Semanal**: Muestra datos por semana

### Número de Períodos

- **6 períodos**: Últimos 6 meses/semanas
- **12 períodos**: Último año (recomendado)
- **24 períodos**: Últimos 2 años

---

## 📈 Métricas Disponibles

### 1. Reportes
- Total de reportes generados en el período
- Comparación con períodos anteriores

### 2. Reportes Enviados
- Reportes con estado "submitted" o "approved"
- Indicador de productividad

### 3. Proyectos Creados
- Nuevos proyectos iniciados
- Tendencias de crecimiento

### 4. Riesgos Altos
- Riesgos con severidad "high" o "critical"
- Indicador de estabilidad

---

## 🖱️ Interactividad

### Tooltips

Al pasar el mouse sobre cualquier punto del gráfico, se muestra un tooltip con:
- **Período**: Fecha del punto de datos
- **Valor**: Valor numérico exacto
- **Delta**: Cambio porcentual respecto al período anterior (si está disponible)

### Efectos Visuales

- **Hover**: Los puntos se agrandan y cambian de color al pasar el mouse
- **Cursor**: Cambia a "pointer" sobre puntos interactivos

---

## 📤 Exportación

Cada gráfico tiene un botón **"Exportar"** que permite:

### Exportar como PNG
- Formato de imagen rasterizada
- Resolución: 800x400px
- Fondo blanco
- Nombre: `[Métrica]-[Fecha].png`

### Exportar como SVG
- Formato vectorial escalable
- Editable en software de diseño
- Nombre: `[Métrica]-[Fecha].svg`

**Uso**:
1. Hacer clic en el botón **"Exportar"** del gráfico deseado
2. Seleccionar formato (PNG o SVG)
3. El archivo se descargará automáticamente

---

## ⚠️ Alertas Visuales

El sistema detecta automáticamente **tendencias significativas** (cambios > 10%):

### Tendencia Positiva (Verde)
- Aumento significativo en la métrica
- Muestra: `⚠️ Tendencia positiva: X% de aumento`
- Color: Verde (#28a745)

### Tendencia Negativa (Rojo)
- Disminución significativa en la métrica
- Muestra: `⚠️ Tendencia negativa: X% de disminución`
- Color: Rojo (#dc3545)

---

## 📊 Estadísticas Mostradas

Cada gráfico muestra:

- **Promedio**: Valor promedio de todos los períodos
- **Último**: Valor del período más reciente
- **Cambio**: Porcentaje de cambio desde el primer período

El cambio se resalta en color si es significativo (>10%).

---

## 💡 Consejos de Uso

### Análisis Mensual
- Usar **12 períodos mensuales** para ver tendencias anuales
- Útil para planificación estratégica
- Identificar estacionalidad

### Análisis Semanal
- Usar **6-12 períodos semanales** para análisis de corto plazo
- Útil para monitoreo operativo
- Detectar problemas rápidamente

### Comparación
- Exportar gráficos para comparar en presentaciones
- Usar tooltips para obtener valores exactos
- Prestar atención a alertas visuales

---

## 🔧 Troubleshooting

### No se muestran datos
- Verificar que hay datos en el rango de fechas seleccionado
- Comprobar permisos de acceso al dashboard
- Revisar que el período seleccionado es válido

### Tooltips no aparecen
- Verificar que JavaScript está habilitado
- Comprobar que no hay conflictos con extensiones del navegador
- Probar en modo incógnito

### Exportación no funciona
- Verificar permisos de descarga del navegador
- Comprobar espacio en disco
- Probar con otro navegador

---

## 📝 Notas Técnicas

- Los datos se cachean por 15 minutos
- Los gráficos se generan en el cliente (SVG nativo)
- No se requiere conexión para visualizar datos cacheados
- Compatible con navegadores modernos (Chrome, Firefox, Edge, Safari)

---

**Última actualización**: 2026-01-18
