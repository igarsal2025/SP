// Medición de performance en tiempo real
// Usa Performance API del navegador para medir FCP, TTI y tamaño de recursos

class PerformanceMonitor {
  constructor() {
    this.metrics = {
      fcp: null,
      tti: null,
      lcp: null,
      cls: 0,
      ttfb: null,
      jsSize: 0,
      resourceCount: 0,
      loadTime: null,
    };
    this.sent = false;
    this.observe();
  }

  observe() {
    // Medir First Contentful Paint (FCP)
    if ("PerformanceObserver" in window) {
      try {
        const fcpObserver = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (entry.name === "first-contentful-paint") {
              this.metrics.fcp = Math.round(entry.startTime);
              this.reportMetric("FCP", this.metrics.fcp, 1000);
            }
          }
        });
        fcpObserver.observe({ entryTypes: ["paint"] });
      } catch (e) {
        console.warn("[Performance] FCP observer not supported");
      }
    }

    if ("PerformanceObserver" in window) {
      try {
        const lcpObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const last = entries[entries.length - 1];
          if (last) {
            this.metrics.lcp = Math.round(last.startTime);
          }
        });
        lcpObserver.observe({ type: "largest-contentful-paint", buffered: true });
      } catch (e) {
        console.warn("[Performance] LCP observer not supported");
      }
    }

    if ("PerformanceObserver" in window) {
      try {
        const clsObserver = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (!entry.hadRecentInput) {
              this.metrics.cls += entry.value;
            }
          }
          this.metrics.cls = parseFloat(this.metrics.cls.toFixed(4));
        });
        clsObserver.observe({ type: "layout-shift", buffered: true });
      } catch (e) {
        console.warn("[Performance] CLS observer not supported");
      }
    }

    // Medir Time to Interactive (TTI) aproximado
    // TTI real requiere más complejidad, usamos DOMContentLoaded + 100ms como aproximación
    window.addEventListener("DOMContentLoaded", () => {
      setTimeout(() => {
        const domReady = performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart;
        const interactive = domReady + 100; // Aproximación
        this.metrics.tti = interactive;
        this.reportMetric("TTI", this.metrics.tti, 2500);
      }, 100);
    });

    // Medir tamaño de recursos JS cargados
    window.addEventListener("load", () => {
      this.measureNavigationTiming();
      this.measureResourceSizes();
      this.metrics.loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
      this.sendMetrics();
    });

    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "hidden") {
        this.sendMetrics(true);
      }
    });
  }

  measureNavigationTiming() {
    if (!("getEntriesByType" in performance)) return;
    const navigation = performance.getEntriesByType("navigation")[0];
    if (!navigation) return;
    this.metrics.ttfb = Math.round(navigation.responseStart);
  }

  measureResourceSizes() {
    if (!("getEntriesByType" in performance)) return;

    const resources = performance.getEntriesByType("resource");
    let jsSize = 0;

    resources.forEach((resource) => {
      if (resource.name.includes(".js") && resource.transferSize) {
        jsSize += resource.transferSize;
      }
    });

    this.metrics.jsSize = jsSize;
    this.metrics.resourceCount = resources.length;
    this.reportMetric("JS Size", (jsSize / 1024).toFixed(2) + " KB", "100 KB");
  }

  reportMetric(name, value, limit) {
    const status = typeof limit === "number" ? (value <= limit ? "✓" : "⚠") : "ℹ";
    const limitText = typeof limit === "number" ? ` / ${limit}ms` : ` / ${limit}`;
    console.log(`[Performance] ${status} ${name}: ${value}${limitText}`);
    
    // Mostrar en UI si está disponible
    const perfEl = document.getElementById("performanceMetrics");
    if (perfEl) {
      const metricEl = document.createElement("div");
      metricEl.className = value <= (typeof limit === "number" ? limit : 100000) ? "perf-ok" : "perf-warn";
      metricEl.textContent = `${name}: ${value}${limitText}`;
      perfEl.appendChild(metricEl);
    }
  }

  sendMetrics(silent = false) {
    // Enviar métricas al servidor para análisis
    if (this.sent) return;
    const data = {
      fcp: this.metrics.fcp,
      tti: this.metrics.tti,
      lcp: this.metrics.lcp,
      cls: this.metrics.cls,
      ttfb: this.metrics.ttfb,
      js_size: this.metrics.jsSize,
      resource_count: this.metrics.resourceCount,
      load_time: this.metrics.loadTime,
      url: window.location.href,
      connection: navigator.connection?.effectiveType || null,
      timestamp: new Date().toISOString(),
    };
    const payload = JSON.stringify(data);

    // Intentar usar sendBeacon primero (más confiable para envíos al cerrar página)
    if (navigator.sendBeacon) {
      const blob = new Blob([payload], { type: "application/json" });
      try {
        // sendBeacon retorna false si no puede enviar (bloqueado por cliente, etc.)
        const sent = navigator.sendBeacon("/api/wizard/performance/metrics/", blob);
        if (sent) {
          this.sent = true;
          return;
        }
        // Si sendBeacon retorna false, continuar con fetch como fallback
        // No mostrar error ya que puede ser bloqueado por ad blockers
      } catch (error) {
        // Ignorar errores silenciosamente (pueden ser bloqueados por ad blockers)
        // Continuar con fetch como fallback
      }
    }

    // Fallback a fetch si sendBeacon no está disponible o falló
    fetch("/api/wizard/performance/metrics/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: payload,
      keepalive: true,
    })
    .then((response) => {
      // Verificar si la respuesta es exitosa
      if (!response.ok && !silent) {
        // Solo mostrar warning si no es un error de bloqueo
        console.warn("[Performance] Error enviando métricas:", response.status);
      }
      this.sent = true;
    })
    .catch((error) => {
      // Ignorar completamente errores de bloqueo por cliente (ad blockers)
      // Estos errores aparecen en la consola del navegador pero no afectan la funcionalidad
      const isBlockedError = 
        error.name === "TypeError" || 
        error.message?.includes("blocked") ||
        error.message?.includes("Failed to fetch") ||
        error.message?.includes("network error");
      
      if (!isBlockedError && !silent) {
        console.warn("[Performance] Error enviando métricas:", error);
      }
      // Marcar como enviado incluso si falló para evitar reintentos
      this.sent = true;
    });
  }

  getMetrics() {
    return { ...this.metrics };
  }
}

// Inicializar monitor de performance
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    window.performanceMonitor = new PerformanceMonitor();
  });
} else {
  window.performanceMonitor = new PerformanceMonitor();
}
