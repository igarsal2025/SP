# Performance Budget - SITEC Web

## Límites de Performance

Este documento define los límites de performance que deben cumplirse en el proyecto SITEC Web.

### Métricas Principales

| Métrica | Límite | Descripción |
|---------|--------|-------------|
| **FCP** (First Contentful Paint) | < 1000ms | Tiempo hasta que se renderiza el primer contenido |
| **TTI** (Time to Interactive) | < 2500ms | Tiempo hasta que la página es completamente interactiva |
| **JS Inicial** | < 100KB | Tamaño total de JavaScript inicial cargado |

### Métricas Secundarias (Warnings)

| Métrica | Límite | Descripción |
|---------|--------|-------------|
| **LCP** (Largest Contentful Paint) | < 2500ms | Tiempo hasta que se renderiza el elemento más grande |
| **CLS** (Cumulative Layout Shift) | < 0.1 | Medida de estabilidad visual |
| **Speed Index** | < 3000ms | Velocidad a la que se muestra el contenido visualmente |

## Verificación

### Local

```bash
# Verificar tamaño de JS
npm run check-performance

# Ejecutar Lighthouse CI
npm run lighthouse
```

### CI/CD

El budget de performance se verifica automáticamente en cada PR mediante GitHub Actions:

- **Workflow**: `.github/workflows/performance.yml`
- **Trigger**: Pull requests y pushes a `main`/`develop`
- **Herramientas**: Lighthouse CI + script de verificación de tamaño

## Medición en Tiempo Real

El frontend incluye un monitor de performance (`performance.js`) que:

- Mide FCP usando Performance Observer
- Calcula TTI aproximado
- Mide tamaño de recursos JS cargados
- Envía métricas al servidor para análisis

Las métricas se muestran en la consola del navegador y se envían a `/api/wizard/performance/metrics/`.

## Estrategias de Optimización

### Para cumplir FCP < 1s:

1. **Critical CSS inline**: Incluir CSS crítico en `<head>`
2. **Lazy loading**: Cargar recursos no críticos de forma diferida
3. **Preload**: Usar `<link rel="preload">` para recursos críticos
4. **Minificación**: Minificar CSS y JS
5. **CDN**: Servir assets estáticos desde CDN

### Para cumplir TTI < 2.5s:

1. **Code splitting**: Dividir JS en chunks más pequeños
2. **Tree shaking**: Eliminar código no utilizado
3. **Async/Defer**: Cargar scripts de forma asíncrona
4. **Service Worker**: Cache de recursos estáticos
5. **Optimización de imágenes**: Usar formatos modernos (WebP, AVIF)

### Para cumplir JS < 100KB:

1. **Bundle analysis**: Analizar dependencias con `webpack-bundle-analyzer`
2. **Lazy imports**: Importar módulos solo cuando se necesiten
3. **Eliminar dependencias innecesarias**: Revisar `package.json`
4. **Polyfills condicionales**: Solo incluir polyfills necesarios
5. **Compresión**: Usar gzip/brotli en el servidor

## Alertas y Monitoreo

- Las métricas se registran en `AuditLog` con acción `performance_metrics`
- Se generan warnings si se exceden los límites
- En producción, considerar integrar con herramientas como:
  - Google Analytics (Core Web Vitals)
  - Sentry (Performance Monitoring)
  - Datadog (APM)

## Referencias

- [Web Vitals](https://web.dev/vitals/)
- [Lighthouse CI](https://github.com/GoogleChrome/lighthouse-ci)
- [Performance Budget](https://web.dev/performance-budgets-101/)
